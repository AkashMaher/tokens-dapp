
from typing import Any
from fastapi import APIRouter, HTTPException, Query

from app.models.hyperliquid import PnLResponse
from app.services.hyperliquid import HyperLiquidClient

router = APIRouter()

def get_hyperliquid_client() -> HyperLiquidClient:
    return HyperLiquidClient()

@router.get("/api/hyperliquid/{wallet}/pnl", response_model=PnLResponse)
async def get_pnl(
    wallet: str,
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
):
    """
    Placeholder: Fetch raw data only and return structured response.
    """
    
    try:
        hyper_client = get_hyperliquid_client()
        
        raw_data = hyper_client.fetch_all_data_for_range(wallet, start, end)
        
        result: dict[str, Any] = hyper_client.calculate_daily_pnl(raw_data)

        if "wallet" not in result:
            result["wallet"] = wallet

        return PnLResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
