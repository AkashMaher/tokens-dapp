from pydantic import BaseModel
from typing import List


class DailyPnL(BaseModel):
    date: str  
    realized_pnl_usd: float
    unrealized_pnl_usd: float
    fees_usd: float
    funding_usd: float
    net_pnl_usd: float
    equity_usd: float  


class Summary(BaseModel):
    total_realized_usd: float
    total_unrealized_usd: float
    total_fees_usd: float
    total_funding_usd: float
    net_pnl_usd: float


class Diagnostics(BaseModel):
    data_source: str = "hyperliquid_api"
    last_api_call: str  
    notes: str = "PnL calculated using daily close prices"


class PnLResponse(BaseModel):
    wallet: str
    start: str  
    end: str  
    daily: List[DailyPnL]
    summary: Summary
    diagnostics: Diagnostics
