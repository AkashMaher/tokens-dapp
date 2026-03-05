import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
import json
from logging import getLogger


class HyperLiquidClient:
    """
    Client for HyperLiquid Info API to fetch wallet data and calculate pnl.
    """

    def __init__(
        self, base_url: str = "https://api.hyperliquid.xyz", timeout: int = 10
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.logger = getLogger(__name__)

    def validate_wallet(self, wallet: str) -> None:
        """Validate wallet address format."""
        if (
            not wallet.startswith("0x")
            or len(wallet) != 42
            or not all(c in "0123456789abcdefABCDEF" for c in wallet[2:])
        ):
            raise ValueError(
                f"Invalid wallet format: {wallet}. Must be 0x + 40 hex chars."
            )

    def _post_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal: POST to /info endpoint.
        """
        try:
            self.logger.debug(
                f"Sending payload to /info: {json.dumps(payload, indent=2)}"
            )
            response = requests.post(
                f"{self.base_url}/info", json=payload, timeout=self.timeout
            )
            if response.status_code == 422:
                self.logger.error(
                    f"422 Unprocessable Entity for payload: {json.dumps(payload)}"
                )
            response.raise_for_status()
            data = response.json()
            self.logger.info(
                f"Successfully fetched from /info (type: {payload.get('type', 'unknown')})"
            )
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HyperLiquid API request failed: {str(e)}")
            raise ValueError(f"HyperLiquid API error: {str(e)}")

    def fetch_user_fills(
        self, wallet: str, start_ts_ms: int, end_ts_ms: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch fills/trades for wallet in time range
        """
        self.validate_wallet(wallet)
        now_ms = int(datetime.now().timestamp() * 1000)
        start_ts_ms = min(start_ts_ms, now_ms)
        end_ts_ms = min(end_ts_ms, now_ms)
        if start_ts_ms > end_ts_ms:
            raise ValueError("startTime must be before endTime")
        payload = {
            "type": "userFillsByTime",
            "user": wallet,
            "startTime": start_ts_ms,
            "endTime": end_ts_ms,
            "aggregateByTime": True,
        }
        fills = self._post_info(payload)
        self.logger.info(
            f"Fetched {len(fills)} fills for wallet {wallet} in range {start_ts_ms}-{end_ts_ms}"
        )
        return fills

    def fetch_funding_history(
        self, wallet: str, start_ts_ms: int, end_ts_ms: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch funding payments for wallet in range
        """
        self.validate_wallet(wallet)
        now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        start_ts_ms = min(start_ts_ms, now_ms)
        end_ts_ms = min(end_ts_ms, now_ms)
        if start_ts_ms > end_ts_ms:
            raise ValueError("startTime must be before endTime")
        payload = {
            "type": "userFunding",
            "user": wallet,
            "startTime": start_ts_ms,
            "endTime": end_ts_ms,
        }
        funding = self._post_info(payload)
        self.logger.info(
            f"Fetched {len(funding)} funding entries for wallet {wallet} in range {start_ts_ms}-{end_ts_ms}"
        )
        return funding

    def fetch_user_state(self, wallet: str) -> Dict[str, Any]:
        """
        Fetch current user state
        """
        self.validate_wallet(wallet)
        payload = {"type": "subAccounts", "user": wallet}
        data = self._post_info(payload)
        return data

    def fetch_daily_close_price(self, coin: str, date_str: str) -> Optional[float]:
        """
        Fetch daily close price for a coin on a specific date
        """
        try:
            date = datetime.fromisoformat(date_str).date()
            if date > datetime.now(tz=timezone.utc).date():
                self.logger.warning(
                    f"Future date {date_str} for close price; using today"
                )
                date = datetime.now(tz=timezone.utc).date()
            start_ts = int(date.timestamp() * 1000)
            end_ts = int((date + timedelta(days=1)).timestamp() * 1000)
            req = {
                "coin": coin,
                "interval": "1D",
                "startTime": start_ts,
                "endTime": end_ts,
            }
            payload = {"type": "candleSnapshot", "req": req}
            data = self._post_info(payload)
            candles = data.get("candles", [])
            if candles:
                close_price = float(candles[-1]["c"])
                self.logger.info(
                    f"Fetched close price for {coin} on {date_str}: {close_price}"
                )
                return close_price
            else:
                self.logger.warning(f"No candles found for {coin} on {date_str}")
                return None
        except Exception as e:
            self.logger.error(
                f"Failed to fetch close price for {coin} on {date_str}: {str(e)}"
            )
            raise ValueError(
                f"Failed to fetch close price for {coin} on {date_str}: {str(e)}"
            )

    def fetch_all_data_for_range(
        self, wallet: str, start: str, end: str
    ) -> Dict[str, Any]:
        """
        Orchestrator: Fetch all raw data for date range.
        """
        try:
            self.validate_wallet(wallet)
            start_date = datetime.fromisoformat(start).date()
            end_date = datetime.fromisoformat(end).date()
            if start_date > end_date:
                raise ValueError("Start date must be before or equal to end date")
            if end_date > datetime.now(tz=timezone.utc).date():
                end_date = datetime.now(tz=timezone.utc).date()

            start_ts = int(
                datetime.combine(start_date, datetime.min.time()).timestamp() * 1000
            )
            end_ts = int(
                datetime.combine(end_date, datetime.max.time()).timestamp() * 1000
            )

            self.logger.info(
                f"Starting fetch for wallet {wallet} from {start} to {end}"
            )

            # if end date is in the future, adjusted to today for api calls
            end = min(end, datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"))

            raw_data = {
                "fills": self.fetch_user_fills(wallet, start_ts, end_ts),
                "funding": self.fetch_funding_history(wallet, start_ts, end_ts),
                "user_state": self.fetch_user_state(wallet),
                "start": start,
                "end": end,
                "start_ts": start_ts,
                "end_ts": end_ts,
                "wallet": wallet,
            }

            positions = (raw_data["user_state"] or {}).get("assetPositions", [])
            if not raw_data["fills"] and not raw_data["funding"] and not positions:
                self.logger.warning(
                    f"Empty data for wallet {wallet}—may be invalid or inactive"
                )
            else:
                self.logger.info(
                    f"Fetch complete for {wallet}: {len(raw_data['fills'])} fills, {len(raw_data['funding'])} funding, {len(positions)} positions"
                )
            return raw_data
        except ValueError as e:
            self.logger.exception(f"ValueError in fetch_all_data_for_range: {str(e)}")
            raise e
        except Exception as e:
            self.logger.exception(
                f"Unexpected error in fetch_all_data_for_range: {str(e)}"
            )
            raise ValueError(f"Failed to fetch HyperLiquid data: {str(e)}")

    def _get_date_from_timestamp(self, ts_ms: int) -> str:
        """Convert timestamp ms to YYYY-MM-DD."""
        return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

    def _get_day_fills_and_funding(
        self, fills: List[Dict], funding: List[Dict], date_str: str
    ) -> tuple[List[Dict], List[Dict]]:
        """Filter fills and funding for a specific date."""
        date_start = int(
            datetime.fromisoformat(f"{date_str} 00:00:00").timestamp() * 1000
        )
        date_end = (
            int(datetime.fromisoformat(f"{date_str} 23:59:59").timestamp() * 1000) + 1
        )
        day_fills = [f for f in fills if date_start <= f.get("time", 0) <= date_end]
        day_funding = [f for f in funding if date_start <= f.get("time", 0) <= date_end]
        return day_fills, day_funding

    def _calculate_unrealized_pnl(self, positions: List[Dict], date_str: str) -> float:
        """Calculate unrealized PnL for open positions marked to daily close price."""
        unrealized = 0.0
        for pos in positions:
            coin = pos.get("coin")
            if not coin:
                continue
            entry_px = float(pos.get("entryPx", 0))
            szi = float(pos.get("szi", 0))
            direction = 1 if szi > 0 else -1
            abs_size = abs(szi)
            close_price = self.fetch_daily_close_price(coin, date_str)
            if close_price is not None:
                unrealized += (close_price - entry_px) * abs_size * direction
        self.logger.debug(f"Unrealized PnL for {date_str}: {unrealized}")
        return unrealized

    def calculate_daily_pnl(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate daily PnL from raw data.
        """
        wallet = (
            raw_data["wallet"]
            if "wallet" in raw_data
            else raw_data.get("wallet", "unknown")
        )
        start = raw_data["start"]
        end = raw_data["end"]
        fills = raw_data["fills"]
        funding = raw_data["funding"]
        user_state = raw_data["user_state"] or {}
        positions = user_state.get("assetPositions", [])

        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
        current_date = start_date
        daily = []
        cumulative_equity = 0.0

        totals = {
            "realized": 0.0,
            "unrealized": 0.0,
            "fees": 0.0,
            "funding": 0.0,
            "net": 0.0,
        }

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            day_fills, day_funding = self._get_day_fills_and_funding(
                fills, funding, date_str
            )

            realized = sum(float(f.get("closedPnl", 0)) for f in day_fills)

            fees = sum(abs(float(f.get("fee", 0))) for f in day_fills)

            funding_sum = sum(
                float(f.get("delta", {}).get("usdc", 0)) for f in day_funding
            )

            unrealized = self._calculate_unrealized_pnl(positions, date_str)

            net = realized + unrealized - fees + funding_sum
            cumulative_equity += net

            daily.append(
                {
                    "date": date_str,
                    "realized_pnl_usd": round(realized, 2),
                    "unrealized_pnl_usd": round(unrealized, 2),
                    "fees_usd": round(fees, 2),
                    "funding_usd": round(funding_sum, 2),
                    "net_pnl_usd": round(net, 2),
                    "equity_usd": round(cumulative_equity, 2),
                }
            )

            totals["realized"] += realized
            totals["unrealized"] += unrealized
            totals["fees"] += fees
            totals["funding"] += funding_sum
            totals["net"] += net

            current_date += timedelta(days=1)

        summary = {
            "total_realized_usd": round(totals["realized"], 2),
            "total_unrealized_usd": round(totals["unrealized"], 2),
            "total_fees_usd": round(totals["fees"], 2),
            "total_funding_usd": round(totals["funding"], 2),
            "net_pnl_usd": round(totals["net"], 2),
        }

        diagnostics = {
            "data_source": "hyperliquid_api",
            "last_api_call": datetime.now(tz=timezone.utc).isoformat() + "Z",
            "notes": "PnL calculated using daily close prices",
        }

        response = {
            "wallet": wallet,
            "start": start,
            "end": end,
            "daily": daily[::-1], # reverse to return recent to old
            "summary": summary,
            "diagnostics": diagnostics,
        }

        self.logger.info(
            f"Calculated PnL for {wallet}: net {summary['net_pnl_usd']}, {len(daily)} days"
        )
        return response
