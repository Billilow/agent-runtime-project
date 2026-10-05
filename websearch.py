import os
import requests
from calculator import ToolExecutionError
from dotenv import load_dotenv
load_dotenv()

def web_search(query: str, max_results: int=3) -> dict:
    try:
     api_key = os.getenv("TAVILY_API_KEY")

     response = requests.post(
         "https://api.tavily.com/search",
         headers={"Authorization": f"Bearer {api_key}"},
         json={"query": query, "max_results": max_results}
     )

     response.raise_for_status()
     data = response.json()

     simplified_results = [
         {"title": r["title"], "url": r["url"], "content": r["content"]}
         for r in data["results"]
     ]
    except requests.exceptions.HTTPError as e:
        raise ToolExecutionError(f"Failed to request the contents: {e}")
    except KeyError as e:
        raise ToolExecutionError("There is no valid key.")
    except Exception as e:
        raise ToolExecutionError(f"Unknown error occurred: {e}")

    return {"query": query, "results": simplified_results}

websearch_declaration = {
    "name": "web_search_tool",
    "description": "Searches the web for current or factual information you don't already know, such as recent news, current events, or specific up-to-date data.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "what the user wants to ask"},
            "max_results": {"type": "integer", "description": "the number of results the user can get from the web search"}
        },
        "required": ['query']
    }
}

if __name__ == '__main__':
    print(web_search("what is the capital of France"))