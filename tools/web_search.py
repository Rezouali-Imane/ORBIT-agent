from langchain_tavily import TavilySearch

web_search = TavilySearch(
    name="web_search",
    description=(
        "Search the live web for current or time-sensitive information. "
        "Use this tool when the answer may have changed recently or needs web sources."
    ),
    max_results=5,
)
