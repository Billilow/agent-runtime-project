from crewai.tools import tool
from calculator import calculator
from crypto_price import get_crypto_price
from websearch import web_search

CALCULATOR_CALLS = []

@tool("Calculator")
def calculator_tool(expression: str) -> str:
    '''Calculates arithmetic expressions,
    supporting parentheses and operator precedence.'''

    result = calculator(expression)
    CALCULATOR_CALLS.append(result)
    return str(result)

@tool("Crypto_Price")
def crypto_price_tool(coin_id: str, vs_currency: str="usd") -> str:
    '''Gets the current price of a cryptocurrency.
    coin_id must be the CoinGecko id (e.g. "bitcoin", "ethereum"), not the ticker symbol.
    vs_currency is the quote currency code (e.g. "usd", "krw"), default "usd".'''
    result = get_crypto_price(coin_id, vs_currency)
    return str(result)

@tool("Web_Search")
def websearch_tool(query: str, max_results: int=3) -> str:
    '''Gets the newest information of what user asks using TAVILY API.
    query is what user asks.
    max_result is the amount of results of information the agent should retrieve from the TAVILY results.'''
    result = web_search(query, max_results)
    return str(result)

