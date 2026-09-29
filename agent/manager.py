from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

from agent.checker import checker
from agent.librarian import librarian
from agent.researcher import researcher
from tools.notes import save_note
from config import GROQ_API_KEY, GROQ_MODEL


checkpointer = InMemorySaver()

manager = create_agent(
    model=ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, max_tokens=500),
    tools=[librarian, researcher, checker, save_note],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "save_note": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "description": "Review the proposed project note before saving it.",
                }
            }
        )
    ],
    checkpointer=checkpointer,
    system_prompt=(
        "You are the ORBIT manager. Decide which specialist tools to call based "
        "on the user's question; do not follow a fixed sequence. Use librarian "
        "for the user's documents, researcher for current or web information, "
        "and both when both kinds of evidence are needed. "
        "Use save_note when the user explicitly asks you to remember or save a "
        "project detail; include a concise title and the exact useful content. "
        "Combine specialist results into a draft with its sources. Call each needed specialist at most once. "
        "You must call checker exactly once with the draft and "
        "sources before answering. If checker flags unsupported claims, fix the "
        "draft using the available evidence and check it again. Never invent a "
        "source or claim that the specialists did not support."
    ),
)
