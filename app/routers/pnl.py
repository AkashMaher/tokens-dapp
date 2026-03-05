from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Query

from app.models.hyperliquid import PnLResponse
from app.services.hyperliquid import HyperLiquidClient
from logging import getLogger


logger = getLogger(__name__)
router = APIRouter()

cached = {}


def get_cached_pnl(wallet: str, start: str, end: str) -> PnLResponse | None:
    try:
        key = f"{wallet}_{start}_{end}"
        entry = cached.get(key)
        if entry and (datetime.now() - entry["timestamp"]).total_seconds() < 30:
            logger.info(f"Returning cached insight for {key}")
            return entry["response"]
        return None
    except Exception as e:
        logger.error(f"Failed to get cached PnL response for {key}: {e}")
        return None


def cache_pnl(wallet: str, start: str, end: str, response: PnLResponse):
    try:
        key = f"{wallet}_{start}_{end}"
        cached[key] = {"response": response, "timestamp": datetime.now()}
        logger.info(f"Cached PnL response for {key}")
    except Exception as e:
        logger.error(f"Failed to cache PnL response for {key}: {e}")


def get_hyperliquid_client() -> HyperLiquidClient:
    return HyperLiquidClient()


@router.get("/hyperliquid/{wallet}/pnl", response_model=PnLResponse)
async def get_pnl(
    wallet: str,
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
):
    """
    Placeholder: Fetch raw data only and return structured response.
    """

    try:
        results = get_cached_pnl(wallet, start, end)
        if results:
            return results
        hyper_client = get_hyperliquid_client()

        raw_data = hyper_client.fetch_all_data_for_range(wallet, start, end)

        result: dict[str, Any] = hyper_client.calculate_daily_pnl(raw_data)

        if "wallet" not in result:
            result["wallet"] = wallet

        resp = PnLResponse(**result)
        cache_pnl(wallet, start, end, resp)
        return resp

    except ValueError as e:
        logger.error(f"Value error while processing PnL for wallet {wallet} from {start} to {end}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while processing PnL for wallet {wallet} from {start} to {end}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
