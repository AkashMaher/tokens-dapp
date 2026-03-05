import requests
from typing import Dict, Any
from app.models.token import Token, MarketData
from dotenv import load_dotenv
import os
load_dotenv()

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", None)
BASE_URL = "https://api.coingecko.com/api/v3"



def _get(endpoint: str, params: Dict[str, Any] = None) -> requests.Response:
    url = f"{BASE_URL}{endpoint}"
    if params is None:
        params = {}
    if COINGECKO_API_KEY:
        params["api_key"] = COINGECKO_API_KEY
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response
    

def fetch_token_data(coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
    """Fetch token metadata and market data from CoinGecko."""
    try:
        meta_response = _get(f"/coins/{coin_id}")
        meta = meta_response.json()

        endpoint = "/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        market_response = _get(endpoint, params)
        data = market_response.json()
        price_data = data[coin_id]

        market_data = MarketData(
            current_price_usd=price_data[vs_currency],
            market_cap_usd=price_data.get(f"{vs_currency}_market_cap", 0),
            total_volume_usd=price_data.get(f"{vs_currency}_24h_vol", 0),
            price_change_percentage_24h=price_data.get(f"{vs_currency}_24h_change", 0),
        )
        
        token = Token(
            id=coin_id,
            symbol=meta["symbol"].upper(),
            name=meta["name"],
            market_data=market_data,
        )

        return {
            "source": "coingecko",
            "token": token.model_dump(), 
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"CoinGecko API error: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Invalid coin ID or missing data: {str(e)}")
    

def fetch_historical_data(coin_id: str, vs_currency: str = "usd", days: int = 30) -> Dict[str, Any]:
    """Fetch historical price data for a token from CoinGecko."""
    try:
        endpoint = f"/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        history_response = _get(endpoint, params)
        return history_response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"CoinGecko API error: {str(e)}")