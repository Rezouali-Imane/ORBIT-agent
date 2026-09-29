from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL
from agent.helpers import compact_specialist_result
from tools.doc_search import search_my_documents


librarian_agent = create_agent(
    model=ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, max_tokens=400),
    tools=[search_my_documents],
    system_prompt=(
        "You are the document librarian. Answer only from passages returned by "
        "search_my_documents. Call search_my_documents at most once. Always list every source as document name and page "
        "number. If the tool returns NO_RELEVANT_DOCUMENTS, say exactly: I don't "
        "have this in my documents."
    ),
)


@tool(
    "librarian",
    description=(
        "Use this when the question needs information from the user's documents; "
        "return only passage-supported claims with document and page sources."
    ),
)
def librarian(query: str) -> str:
    """Search the user's documents and answer from the returned passages."""
    print("-> librarian")
    try:
        result = librarian_agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config={"recursion_limit": 5},
        )
        return compact_specialist_result(result["messages"][-1].content)
    except Exception:
        return compact_specialist_result(search_my_documents.invoke({"query": query}))
