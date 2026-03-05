from pydantic import BaseModel
from typing import Optional

class InsightRequest(BaseModel):
    vs_currency: str = "usd"
    history_days: int = 30

class MarketData(BaseModel):
    current_price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    total_volume_usd: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None

class Token(BaseModel):
    id: str
    symbol: str
    name: str
    market_data: MarketData
    historical_data: Optional[dict] = None

class PartialInsightResponse(BaseModel):  
    source: str
    token: Token