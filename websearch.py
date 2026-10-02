import os
import requests
from calculator import ToolExecutionError
from dotenv import load_dotenv
load_dotenv()

def web_search(query: str, max_results: int=3) -> dict:
    api_key = os.getenv("TAVILY_API_KEY")

    response = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"query": query, "max_results": max_results}
    )

    data = response.json()
    return data

if __name__ == '__main__':
    print(web_search("what is the capital of France"))