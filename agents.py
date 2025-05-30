from typing import Annotated, TypedDict, List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import uuid
import asyncio
from tools import tools
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig


def get_graph():
    # The state
    class State(TypedDict):
        messages: Annotated[List[Any], add_messages]
        task_id: str
        file_name: str
        iteration_count: int  # Only counter you need
        max_iterations: int   # Set your limit
            
    # Define a structured output for Evaluator agent
    class EvaluatorOutput(BaseModel):
        is_numeric: bool = Field(description="Whether the response is a number (True) or words (False)")
        final_answer: str = Field(description="The final answer extracted from the response")

    #Define a Tool Call limiter so it stops after a number of executions. Mainly for web in search
    class ToolCallLimiter(BaseCallbackHandler):
        def __init__(self, max_calls: int):
            self.max_calls = max_calls
            self.call_count = 0
            self.limit_reached = False

        def on_tool_start(self, tool_name: str, **kwargs):
            self.call_count += 1
            if self.call_count > self.max_calls:
                self.limit_reached = True
                raise Exception("Tool call limit reached")

    load_dotenv(override=True)

    # Initialize the LLMs
    worker_llm = ChatOpenAI(model="gpt-4o-mini")
    worker_llm_with_tools = worker_llm.bind_tools(tools)

    evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
    evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput, method="function_calling")

    # The worker node
    
    def worker(state: State) -> Dict[str, Any]:
        system_message = f"""You are a helpful assistant that can use tools to complete tasks and deliver a message to an evaluator.
    If the tool is not available, you can try to find the information online. You can also use your own knowledge to answer the question. 
    You need to provide a step-by-step explanation of how you arrived at the answer.
    If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer to the evaluator.

    If a file is needed given by the Human Message, you must follow these steps:
    1. First, call the `get_question_file` tool function using the following file_name: '{state['file_name']}'
    2. This will return a `file_path`. You must use this exact file_path for all subsequent tool calls that require access to the file (e.g., audio transcription, file parsing, etc.)
    3. Never use the filename or file path mentioned by the user in their prompt. Only use the file_path returned by the `get_question_file` tool.
    4. If you mistakenly use the user’s filename instead of the file_path from the tool, your task will fail.

    Important: Always explain the steps you are taking. For example, mention that you first retrieved the file path using the correct file_name, and then processed it using the appropriate tool.

    Your goal is to return only the final answer, after completing all required steps correctly."""

        found_system_message=False
        # Add in the system message
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True
        
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages
        
            # Check iteration limit first
        current_iterations = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 10)  

        if current_iterations >= max_iterations:
            # Force conclusion when limit reached
            return {
                "messages": [AIMessage(content="I've reached my iteration limit. Let me provide my best answer based on the information I've gathered so far.")],
            }

            # Invoke the LLM with tools
        response = worker_llm_with_tools.invoke(messages)

        # Return updated state
        return {
            "messages": [response],
            "iteration_count": current_iterations + 1
        }
        

    def worker_router(state: State) -> str:
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"

    def format_conversation(messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation

    def evaluator(state: State) -> State:
        last_response = state["messages"][-1].content

        system_message = f"""You are an evaluator that determines the final answer by an Assistant.
    Assess the Assistant's last response based on the given criteria. Respond if the answer is a number or a string of few words and determine the answer """
            
        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what type of answer (string or number) and output the answer.

    The entire conversation with the assistant, with the user's original request and all replies, is:
    {format_conversation(state['messages'])}

    And the final response from the Assistant that you are evaluating is:
    {last_response}

    You are a general AI evaluator. Based on the question given, finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. 
    YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. 
    If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. 
    If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
    """
        
        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = evaluator_llm_with_output.invoke(evaluator_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator final answer: {eval_result.final_answer}"}],
        }
        return new_state

    # Set up Graph Builder with State
    graph_builder = StateGraph(State)

    # Add nodes
    graph_builder.add_node("worker", worker)
    graph_builder.add_node("tools", ToolNode(tools=tools))
    graph_builder.add_node("evaluator", evaluator)

    # Add edges
    graph_builder.add_edge(START, "worker")
    graph_builder.add_conditional_edges("worker", worker_router, {"tools": "tools", "evaluator": "evaluator"})

    graph_builder.add_edge("tools", "worker")

    graph_builder.add_edge("evaluator", END)

    # Compile the graph
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    return graph

class BasicAgent:
    """A simple agent that manages interaction with the LangGraph."""
    
    def __init__(self, graph=None):
        """Initialize the agent with a LangGraph."""
        if graph is None:
            self.graph = get_graph()
        else:
            self.graph = graph

        thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": thread_id}}
    def __call__(self, question: str, task_id: str, file_name: str) -> str:
        """Process a question synchronously."""
        #Skipp the chess question
        if task_id == "cca530fc-4052-43b2-b130-b30968d8aa44":
            return "Skipped"
        else:
            # Use the class's config instead of creating a new one
            result = asyncio.run(self._async_call(question, task_id, file_name))
            return result

    async def _async_call(self, question: str, task_id: str, file_name: str) -> str:
        """Internal async method to handle the graph invocation."""
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        messages = await self.graph.ainvoke(
            {
                "messages": [HumanMessage(content=question)],
                "task_id": task_id,
                "file_name": file_name
            },
            config=config
        )
        
        # Extract the final answer, handling the "Evaluator final answer: " prefix
        final_content = messages['messages'][-1].content
        if final_content.startswith("Evaluator final answer: "):
            return final_content[24:]
        return final_content




# if __name__ == "__main__":
#     # Example usage
#     agent = BasicAgent()
    
#     question = "Review the chess position provided in the image. It is black's turn. Provide the correct next move for black which guarantees a win. Please provide your response in algebraic notation."
#     task_id = "cca530fc-4052-43b2-b130-b30968d8aa44"
#     file_name = "cca530fc-4052-43b2-b130-b30968d8aa44.png"



#     # question = "The attached Excel file contains the sales of menu items for a local fast-food chain. What were the total sales that the chain made from food (not including drinks)? Express your answer in USD with two decimal places."
#     # task_id = "7bd855d8-463d-4ed5-93ca-5fe35145f733"
#     # file_name = "7bd855d8-463d-4ed5-93ca-5fe35145f733.xlsx"

    
#     #question = "Given this table defining * on the set S = {a, b, c, d, e}\n\n|*|a|b|c|d|e|\n|---|---|---|---|---|---|\n|a|a|b|c|b|d|\n|b|b|c|a|e|c|\n|c|c|a|b|b|a|\n|d|b|e|b|e|d|\n|e|d|b|a|d|c|\n\nprovide the subset of S involved in any possible counter-examples that prove * is not commutative. Provide your answer as a comma separated list of the elements in the set in alphabetical order."
#     #task_id = "6f37996b-2ac7-44b0-8e68-6d28256631b4"
#     #file_name = ""
    
#     # question = "What is the first name of the only Malko Competition recipient from the 20th Century (after 1977) whose nationality on record is a country that no longer exists?"
#     # task_id = "5a0c1adf-205e-4841-a666-7c3ef95def9d"
#     # file_name = ""

#     # Using the BasicAgent class (synchronous)
#     result = agent(question, task_id, file_name)
#     print("Agent result:", result)