import requests
from langchain.tools import tool
from app.config import settings

from app.logger import logger

@tool
def google(query: str) -> str:
    """
    Perform a Google search to find relevant information.
    """
    logger.info("🔨SEARCHER tool | was invoked")
    logger.info(query)
    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}
    response = requests.post("https://google.serper.dev/search", json=payload, headers=headers)
    results = response.json()

    if "organic" in results and results["organic"]:
        return results["organic"][0].get("snippet", "No snippet found.")
    
    return "No results found."
