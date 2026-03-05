from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Body
from app.models.token import Insight, InsightRequest, InsightResponse, Token
from app.services.ai import AIGeneration
from app.services.coingecko import fetch_token_data, fetch_historical_data
from logging import getLogger

router = APIRouter()

logger = getLogger(__name__)


def get_ai_service() -> AIGeneration:
    return AIGeneration()


def get_closest_price(prices: list[tuple[int, float]], target_ts: int) -> float | None:
    """
    Find the closest historical price to the target timestamp (from past data).
    prices: List of [timestamp_ms, price] tuples, sorted ascending.
    Returns the price from the most recent entry <= target_ts, or None if none available.
    """
    if not prices:
        return None
    for ts, price in reversed(prices):
        if ts <= target_ts:
            return price
    return None


@router.post("/token/{coin_id}/insight", response_model=InsightResponse)
async def get_insight(coin_id: str, req: InsightRequest = Body(None)):
    """
    Fetch token metadata and market data from CoinGecko.
    Full insight (AI) coming in next phase.
    """
    try:
        fetch_historical = req.fetch_historical if req else True
        vs_currency = req.vs_currency if req else "usd"
        history_days = req.history_days if req else 30
        logger.info(
            f"Received insight request for {coin_id} with vs_currency={vs_currency}, fetch_historical={fetch_historical}, history_days={history_days}"
        )
        data = fetch_token_data(coin_id, vs_currency)

        historical_prices = {}
        if fetch_historical:
            historical_data = fetch_historical_data(
                coin_id,
                vs_currency,
                history_days,
            )
            prices = historical_data.get("prices", [])
            if prices:
                now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                intervals = {
                    "48h_ago": 2 * 24 * 3600 * 1000,
                    "7d_ago": 7 * 24 * 3600 * 1000,
                    "15d_ago": 15 * 24 * 3600 * 1000,
                    "29d_ago": 29 * 24 * 3600 * 1000,
                }
                for label, delta_ms in intervals.items():
                    if delta_ms // (24 * 3600 * 1000) <= history_days:
                        target_ts = now_ms - delta_ms
                        closest_price = get_closest_price(prices, target_ts)
                        if closest_price is not None:
                            historical_prices[label] = closest_price

                if historical_prices:
                    data["token"]["historical_prices"] = historical_prices

        aiservice = get_ai_service()
        insight, model_info = await aiservice.generate_insight(token_data=data["token"])

        full_response = InsightResponse(
            source="coingecko",
            token=Token(**data["token"]),
            insight=Insight(**insight),
            model=model_info,
        )

        logger.info(
            f"Generated insight for {coin_id} using model {model_info['model']} from provider {model_info['provider']}"
        )

        return full_response.model_dump(exclude_none=True)
    except ValueError as e:
        logger.error(f"Error processing insight request for {coin_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
