from fastapi import APIRouter, HTTPException, Body
from app.models.token import InsightRequest
from app.services.coingecko import fetch_token_data, fetch_historical_data

router = APIRouter()

@router.post("/api/token/{coin_id}/insight")
def get_insight(coin_id: str, req: InsightRequest = Body(None)):
    """
    Fetch token metadata and market data from CoinGecko.
    Full insight (AI) coming in next phase.
    """
    try:
        data = fetch_token_data(coin_id, req.vs_currency if req else "usd")
        # we will add the historical data after ai insights generation so the prompt will bee more focused and less noisy data.
        
        historical_data = fetch_historical_data(coin_id, req.vs_currency if req else "usd", req.history_days if req else 30)
        data["token"]["historical_data"] = historical_data
        return data 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))