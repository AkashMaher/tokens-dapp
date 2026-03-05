import requests
from typing import Dict, Any
from app.models.token import Token, MarketData

BASE_URL = "https://api.coingecko.com/api/v3"

def fetch_token_data(coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
    try:
        meta_url = f"{BASE_URL}/coins/{coin_id}"
        meta_response = requests.get(meta_url)
        meta_response.raise_for_status()
        meta = meta_response.json()

        market_url = (
            f"{BASE_URL}/simple/price?"
            f"ids={coin_id}&"
            f"vs_currencies={vs_currency}&"
            f"include_market_cap=true&"
            f"include_24hr_vol=true&"
            f"include_24hr_change=true"
        )
        market_response = requests.get(market_url)
        market_response.raise_for_status()
        price_data = market_response.json()[coin_id]

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
    try:
        history_url = f"{BASE_URL}/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"
        history_response = requests.get(history_url)
        history_response.raise_for_status()
        return history_response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"CoinGecko API error: {str(e)}")