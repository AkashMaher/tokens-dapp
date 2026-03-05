from pydantic import BaseModel, validator
from typing import Optional

class InsightRequest(BaseModel):
    vs_currency: str = "usd"
    history_days: int = 30
    fetch_historical: bool = True  

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
    historical_prices: str | int | float | dict | None = None

class PartialInsightResponse(BaseModel):  
    source: str
    token: Token
    
    
class Insight(BaseModel):
    reasoning: str
    sentiment: str  

    @validator("sentiment")
    def validate_sentiment(cls, v):
        if v not in ["Bullish", "Bearish", "Neutral"]:
            raise ValueError('sentiment must be "Bullish", "Bearish", or "Neutral"')
        return v


class InsightResponse(BaseModel):
    source: str
    token: Token
    insight: Insight
    model: dict[str, str]
    historical_data: Optional[dict] = None
    
    
class ModelInfo(BaseModel):
    provider: str
    model: str