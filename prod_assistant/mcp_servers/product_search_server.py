import sys
from mcp.server.fastmcp import FastMCP
from prod_assistant.retriever.retrieval import Retriever
from langchain_community.tools import DuckDuckGoSearchRun

# -----------------------------------------------------------------------------
# MCP RULE: never write to stdout (breaks stdio transport)
# -----------------------------------------------------------------------------
sys.stdout = sys.stderr

# -----------------------------------------------------------------------------
# Initialize MCP server
# -----------------------------------------------------------------------------
mcp = FastMCP("hybrid_search")

# -----------------------------------------------------------------------------
# Lazy singletons (initialized only when tool is called)
# -----------------------------------------------------------------------------
_retriever = None
_duckduckgo = None


def get_retriever():
    global _retriever
    if _retriever is None:
        retriever_obj = Retriever()
        _retriever = retriever_obj.load_retriever()
    return _retriever


def get_duckduckgo():
    global _duckduckgo
    if _duckduckgo is None:
        _duckduckgo = DuckDuckGoSearchRun()
    return _duckduckgo


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def format_docs(docs) -> str:
    if not docs:
        return ""

    chunks = []
    for d in docs:
        meta = d.metadata or {}
        chunks.append(
            f"Title: {meta.get('product_title', 'N/A')}\n"
            f"Price: {meta.get('price', 'N/A')}\n"
            f"Rating: {meta.get('rating', 'N/A')}\n"
            f"Reviews:\n{d.page_content.strip()}"
        )

    return "\n\n---\n\n".join(chunks)


# -----------------------------------------------------------------------------
# MCP Tools
# -----------------------------------------------------------------------------
@mcp.tool()
async def get_product_info(query: str) -> str:
    """
    Retrieve product information from the local vector retriever.
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)

        context = format_docs(docs)
        if not context.strip():
            return "No local results found."

        return context

    except Exception as e:
        return f"Error retrieving product info: {e}"


@mcp.tool()
async def web_search(query: str) -> str:
    """
    Fallback web search using DuckDuckGo.
    """
    try:
        duckduckgo = get_duckduckgo()
        return duckduckgo.run(query)

    except Exception as e:
        return f"Error during web search: {e}"


# -----------------------------------------------------------------------------
# Run MCP Server (stdio ONLY)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")

