from fastmcp import FastMCP
from typing import Union
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

# Run as an HTTP server (needed for ChatGPT)
if __name__ == "__main__":
    mcp.run(transport="sse", port=8000)
