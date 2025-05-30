from pydantic import BaseModel, Field

class EvaluatorOutput(BaseModel):
    is_numeric: bool = Field(description="Whether the response is a number (True) or words (False)")
    final_answer: str = Field(description="The final answer extracted from the response") 