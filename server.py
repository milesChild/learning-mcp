from fastmcp import FastMCP
from typing import Union, List
from pathlib import Path
import logging # docs caution against using stdout operations like print() and recommend using stderr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this creates an instance of an MCP server
mcp = FastMCP("local-mcp-server")

FILES_DIR = Path("files")

# definition of a tool from the docs: Functions that your LLM can actively call, 
# and decides when to use them based on user requests. Tools can write to 
# databases, call external APIs, modify files, or trigger other logic.
@mcp.tool(
    name="ping",
    description="Checks if the server is running and ready to use. Returns pong if true."
    )
def ping() -> str:
    return "pong"

@mcp.tool(
    name="save_note",
    description="Saves a note to the local file server. If the provided filename already exists, an error is thrown."
)
def save_note(content: str, filename: str) -> Union[str, Exception]:
    # if chat tries to fw my actual files
    safe_name = Path(filename).name
    if not safe_name:
        raise ValueError("Filename cannot be empty.")
    path = FILES_DIR / safe_name

    # atomic create autofails if the file alr exists
    try:
        with open(path, "x", encoding="utf-8") as f:
            f.write(content.rstrip("\n") + "\n")
    except FileExistsError:
        raise FileExistsError(f"Filename '{safe_name}' already exists.")
    
    logger.info(f"Saved note to {path}")
    return f"Successfully saved to {path.as_posix()}"

@mcp.resource("notes://list")
def list_notes() -> str:
    """Provides a list of all available notes in the system."""
    files = [f.name for f in FILES_DIR.iterdir() if f.is_file()]
    if not files:
        return "No notes found."
    return "Available notes:\n" + "\n".join(f"- {name}" for name in files)

@mcp.resource("notes://{filename}")
def read_note(filename: str) -> str:
    """Reads the content of a specific note."""
    safe_name = Path(filename).name
    path = FILES_DIR / safe_name
    
    if not path.exists():
        return f"Error: Note '{safe_name}' not found."
    
    return path.read_text(encoding="utf-8")

@mcp.prompt("onboard-me")
def onboard_prompt() -> str:
    """Introduction to using this server."""
    return """Welcome! I am your Note Assistant. 
    I can help you:
    1. View your existing notes by checking the 'notes://list' resource.
    2. Save new ideas using the 'save_note' tool.
    
    How would you like to start?"""

@mcp.prompt("summarize-note")
def summarize_note(filename: str) -> str:
    """Ask the LLM to summarize a specific note by name."""
    return f"""Please perform the following steps:
    1. Read the content of the note at 'notes://{filename}'.
    2. Provide a 3-bullet point summary of that note."""

# use ngrok to expose http so chatgpt web can access it
if __name__ == "__main__":
    mcp.run(transport="sse", port=8000)
