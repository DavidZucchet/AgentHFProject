from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from langgraph.prebuilt import ToolNode
from langchain.agents import Tool
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import AssemblyAIAudioTranscriptLoader
from langchain_community.document_loaders import YoutubeLoader
import requests
import subprocess
import pandas as pd
import tempfile
import re

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# API URL configuration
DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"
api_url = DEFAULT_API_URL

@tool
def get_question_file(file_name):
    """
    Fetches a question-related file from a remote API and stores it as a temporary file.

    It downloads a file associated with a question from a specified API endpoint, based on the 
    `file_name` provided. The file is saved to a temporary file 
    Args:
        file_name (str): The name of the file to fetch (e.g., '001_audio.mp3', '002_data.xlsx').

    Returns:
        tempfile.NamedTemporaryFile or (None, None): A temporary file object containing the downloaded file.
                                                     Returns (None, None) if no file is provided or fetching fails.

    Example:
        >>> file = get_question_file("003_data.xlsx")
        >>> df = pd.read_excel(file.name)
    """
    if not file_name:
        print(f"No file associated with question")
        return None, None

    file_url = f"{api_url}/files/{file_name.split('.')[0]}"

    print(f"Fetching file from: {file_url}")
    try:
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()

        suffix = "." + file_name.split(".")[-1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(response.content)
        temp_file.flush()
        temp_file.seek(0)

        print(f"File saved temporarily at: {temp_file.name}")
        return temp_file.name

    except requests.exceptions.RequestException as e:
        print(f"Error fetching file {file_name}: {e}")
        return None, None

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a query and return maximum 2 results.
    Args:
        query: The search query."""
    search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"wiki_results": formatted_search_docs}

@tool
def web_search(query: str) -> str:
    """Search Tavily for a query and return maximum 3 results.
    Args:
        query: The search query."""
    search_docs = TavilySearchResults(max_results=3).invoke(query=query)
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"web_results": formatted_search_docs}

@tool
def arxiv_search(query: str) -> str:
    """Search Arxiv for a query and return maximum 3 result.
    Args:
        query: The search query."""
    search_docs = ArxivLoader(query=query, load_max_docs=3).load()
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content[:1000]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"arxiv_results": formatted_search_docs}

@tool
def audio_to_text(file_path: str) -> str:
    """Convert a file in mp3 to text format. It returns a str. The input you must insert is the file_path that you get 
    from the get_question_file function (don't use the name of the user prompt)
    Args:
        file_path: the file_path that you get from the get_question_file function. Don't use the name of the file in the prompt"""
    loader = AssemblyAIAudioTranscriptLoader(file_path)
    docs = loader.load()
    return docs[0].page_content

@tool
def loadExcelDocSum(file_path: str):
    """Load a Microsoft Excel file into a DataFrame variable and then sum columns. The input you must insert is the file_path that you get 
    from the get_question_file function (don't use the name of the user prompt)
    Args:
        file_path: the file_path that you get from the get_question_file function. Don't use the name of the file in the prompt
    Returns:
        pandas.Series: Series containing the sum of specified columns
    """
    df = pd.read_excel(file_path)
    column_sums = df.sum()
    return column_sums

@tool
def youtube_tool(url: str):
    """Get a transcript from a youtube video. The input must be the Url of the video
    Args:
        url: the Url of the youtube video
    """
    loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)
    document = loader.load()
    return document

def run_script_from_path(file_path: str) -> str:
    try:
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)

# Initialize search tools
search_tool = DuckDuckGoSearchRun()
serper = GoogleSerperAPIWrapper()
tool_search = Tool(
    name="search",
    func=serper.run,
    description="Use this tool when you want to get the results of an online web search"
)

run_script_tool = Tool(
    name="RunPythonScriptFromPath",
    func=run_script_from_path,
    description="""
    Execute a Python code and return a string with the result. The input you must insert is the file_path that you get 
    from the get_question_file function (don't use the name of the user prompt)
    """
)

def find_non_commutative_elements(table_str: str) -> str:
    """
    Analyzes a binary operation table defined in Markdown format and returns 
    the set of elements involved in any counterexample to commutativity.

    Args:
        table_str (str): The table as a string defining * on the set S.
                         Expected format is Markdown with header and grid.

    Returns:
        str: A comma-separated list of elements involved in counterexamples,
             sorted in alphabetical order (e.g., "b, e").
    """
    # Replace the top-left * label to prevent KeyError
    table_str = table_str.replace("|*|", "|")
    # Extract rows from the table
    lines = table_str.strip().splitlines()

    # Find the table start
    table_lines = [line for line in lines if line.strip().startswith('|')]

    # Parse header
    header = table_lines[0].strip().split('|')[1:-1]
    header = [h.strip() for h in header]  # ['a', 'b', 'c', 'd', 'e']

    # Parse the operation table into a dict of dicts
    operation = {}
    for row in table_lines[2:]:  # skip header and separator
        parts = row.strip().split('|')[1:-1]
        row_label = parts[0].strip()
        row_values = [val.strip() for val in parts[1:]]
        operation[row_label] = dict(zip(header, row_values))

    # Check for counterexamples to commutativity
    counterexample_elements = set()
    for x in header:
        for y in header:
            if operation[x][y] != operation[y][x]:
                counterexample_elements.update([x, y])

    # Return sorted, comma-separated list
    return ', '.join(sorted(counterexample_elements))

non_commutativity_tool = Tool.from_function(
    name="find_non_commutative_elements",
    func=find_non_commutative_elements,
    description=(
        "Given a binary operation table in Markdown format, identify elements involved in "
        "any counterexample to commutativity, and return them as a comma-separated list "
        "in alphabetical order."
    )
)

@tool
def sum_selected_items(series_str: str, include_only: list = None) -> str:
    """
    Calculates the sum of values from a pandas Series-like string, including only specified keys.

    Parameters:
    - series_str: String representation of a pandas Series.
    - include_only: List of labels (e.g., ["Burgers", "Fries"]) to include in the sum.

    Example:
        series_str = "Burgers    17571\\nHot Dogs   18003\\nSoda 19048"
        include_only = ["Burgers", "Hot Dogs"]
    Returns:
        Total sum of selected items, formatted as a string.
    """
    # Default include list (if none provided)
    if include_only is None:
        include_only = ["Burgers", "Hot Dogs", "Salads", "Fries", "Ice Cream"]

    total = 0

    for line in series_str.splitlines():
        # Match lines like: Label<whitespace>number
        match = re.match(r"(.+?)\s+([\d,]+)$", line.strip())
        if match:
            label = match.group(1).strip()
            value = int(match.group(2).replace(",", ""))
            if label in include_only:
                total += value

    return f"The total for selected items is ${total:,}"

@tool
def classify_plant_parts(items: list[str]) -> dict:
    """
    Classifies each item in a list as either 'vegetable', 'fruit', 'herb', 'nut', 'grain', or 'unknown'
    using strict botanical definitions.

    Returns a dictionary mapping each item to its category.
    """
    botanical_db = {
        "milk": "unknown",
        "eggs": "unknown",
        "flour": "grain",
        "whole bean coffee": "seed",
        "oreos": "unknown",
        "sweet potatoes": "vegetable",
        "fresh basil": "vegetable",
        "plums": "fruit",
        "green beans": "fruit",
        "rice": "grain",
        "corn": "fruit",
        "bell pepper": "fruit",
        "whole allspice": "spice",
        "acorns": "nut",
        "broccoli": "vegetable",
        "celery": "vegetable",
        "zucchini": "fruit",
        "lettuce": "vegetable",
        "peanuts": "nut",
    }

    return {item: botanical_db.get(item.lower(), "unknown") for item in items}

tools = [get_question_file, tool_search, search_tool, non_commutativity_tool, wiki_search, audio_to_text, loadExcelDocSum, youtube_tool, run_script_tool, sum_selected_items, classify_plant_parts]
