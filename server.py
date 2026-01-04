from fastmcp import FastMCP

# this creates an instance of an MCP server
mcp = FastMCP("local-mcp-server")

# definition of a tool from the docs: Functions that your LLM can actively call, 
# and decides when to use them based on user requests. Tools can write to 
# databases, call external APIs, modify files, or trigger other logic.
@mcp.tool(
    name="ping",
    description="Checks if the server is running and ready to use. Returns pong if true."
    )
def ping() -> str:
    return "pong"

# Run as an HTTP server (needed for ChatGPT)
if __name__ == "__main__":
    mcp.run(transport="sse", port=8000)
