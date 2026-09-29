from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL


checker_agent = create_agent(
    model=ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, max_tokens=300),
    tools=[],
    system_prompt=(
        "You are a source checker. Compare the draft answer with the sources "
        "provided by the manager. Return a list of claims without supporting "
        "sources, or exactly 'The draft is fine.' when every claim is supported."
    ),
)


@tool(
    "checker",
    description=(
        "Use this when a draft and its sources are ready to audit; list unsupported "
        "claims or say the draft is fine."
    ),
)
def checker(draft_answer: str, sources_used: str) -> str:
    """Check whether a draft's claims are supported by its listed sources."""
    print("-> checker")
    request = (
        f"Draft answer:\n{draft_answer}\n\n"
        f"Sources used:\n{sources_used}"
    )
    result = checker_agent.invoke(
        {"messages": [{"role": "user", "content": request}]}
    )
    return result["messages"][-1].content
