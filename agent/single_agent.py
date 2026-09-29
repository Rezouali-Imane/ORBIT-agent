from langchain.agents import create_agent
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL
from tools.web_search import web_search


model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)

agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=(
        "You are a concise research assistant. Use web_search for current or "
        "time-sensitive questions, then answer with the relevant source URLs."
    ),
)
