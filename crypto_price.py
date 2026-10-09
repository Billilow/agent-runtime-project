from calculator import ToolExecutionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import requests

@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1,max=8),
    reraise=True
)
def _fetch_price(coin_id: str, vs_currency: str) -> dict:
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": coin_id, "vs_currencies": vs_currency}
    )

    response.raise_for_status()
    return response.json()

def get_crypto_price(coin_id:str, vs_currency:str="usd") -> dict:
    try:
        data = _fetch_price(coin_id, vs_currency)
        return {"coin_id": coin_id, "vs_currency": vs_currency, "price": data[coin_id][vs_currency]}
    except KeyError as e:
        raise ToolExecutionError("{} doesn't exist".format(coin_id))
    except Exception as e:
        raise ToolExecutionError(f"{e}, try again.")


crypto_declaration = {
    "name": "crypto_price_tool",
    "description": "You can use this when checking the price of the crypto",
    "parameters": {
        "type": "object",
        "properties": {
            "coin_id": {"type": "string", "description": "the id of coin, e.g: bitcoin"},
            "vs_currency": {"type": "string", "description": "the currency of the coin_id, e.g.: usd, twd, etc"}
        },
        "required": ["coin_id"]
    }
}

if __name__ == '__main__':
    print(get_crypto_price("bitcoin"))