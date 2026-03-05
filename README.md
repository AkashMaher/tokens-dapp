# Token Insight & Analytics API

Backend service built for the assignment that provides:

- Token insights using CoinGecko data + AI-generated reasoning & sentiment
- Daily PnL (Profit & Loss) calculations for HyperLiquid wallets

## Features

- **POST /api/token/{coin_id}/insight**  
  Fetches current market data + selected historical price points (48h, 7d, 15d, 30d ago) from CoinGecko  
  Generates insight (reasoning + sentiment: Bullish/Bearish/Neutral) using Groq (Llama 3)

- **GET /api/hyperliquid/{wallet}/pnl?start=YYYY-MM-DD&end=YYYY-MM-DD**  
  Fetches wallet activity (fills/trades, funding payments, current positions) from HyperLiquid Info API  
  Calculates daily realized/unrealized PnL, fees, funding, net PnL, cumulative equity  
  Returns structured JSON with daily breakdown + summary + diagnostics

## Tech Stack

- **Backend**: Python + FastAPI
- **HTTP Client**: requests
- **AI Provider**: Groq (free tier, Llama 3 8B model) – very fast inference with JSON mode
- **Data Sources**:
  - CoinGecko API (free, no key required)
  - HyperLiquid Info API (direct POST to `/info`, no key/auth required)
- **Validation**: Pydantic
- **Logging**: Python `logging` module
- **Testing**: pytest
- **Containerization**: Docker (preferred for deliverable)

## Prerequisites

- Python 3.10+
- Docker (recommended for production-like run)
- Groq API key (free signup: https://console.groq.com/keys)

## Installation & Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/token-analytics-api.git
cd token-analytics-api
```

2. Create and activate virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate          # Linux/macOS
# Windows: venv\Scripts\activate
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. copy `.env.example` to `.env`

```bash
cp .env.example .env
```

5. create Groq api key https://console.groq.com/keys and add into `.env` and Coingecko api key (optional)

```bash
GROQ_API_KEY=your_groq_api_key
COINGECKO_API_KEY=your_coingecko_api_key
```

### ================

Run on local

```bash
uvicorn app.main:app --reload
```

Check endpoints swagger UI http://localhost:8000/docs

Run on production

Docker Build Image

```bash
docker build -t token-app .
```

To import in postman

1. Open Postman & Click on Import
2. In the Import dialog box enter `http://localhost:8000/openapi.json` OR Import `.postman_collection.json` file
3. Ensure "Generate a collection from the import" is selected. Postman will detect the "OpenAPI 3.0" format.
4. Now Click on Import

New collection will get created

Run docker container

```bash
docker run -d --name mytoken-app --env-file .env -p 8000:8000 token-app
```

# API Endpoints

1. Token Insight

POST `/api/token/{coin_id}/insight`

Example request:

```bash
curl -X POST "http://localhost:8000/api/token/solana/insight" \
  -H "Content-Type: application/json" \
  -d '{"vs_currency": "usd", "history_days": 30, "fetch_historical": true}'
```

Example response:

```json
{
  "source": "coingecko",
  "token": {
    "id": "solana",
    "symbol": "SOL",
    "name": "Solana",
    "market_data": {
      "current_price_usd": 88.46,
      "market_cap_usd": 50373796800.454346,
      "total_volume_usd": 5385796848.097713,
      "price_change_percentage_24h": -3.7341207732625747
    },
    "historical_prices": {
      "48h_ago": 85.21093495098974,
      "7d_ago": 84.95017928966257,
      "15d_ago": 82.16148342808022,
      "29d_ago": 91.07143512264953
    }
  },
  "insight": {
    "reasoning": "The Solana token price has seen a decline in the last 24 hours but historical prices indicate a potential recovery as prices have increased from 29 days ago. However, the recent 24-hour price drop indicates caution.",
    "sentiment": "Neutral"
  },
  "model": {
    "provider": "groq",
    "model": "llama-3.1-8b-instant"
  }
}
```

2. HyperLiquid Wallet Daily PnL

GET `/api/hyperliquid/{wallet}/pnl?start=YYYY-MM-DD&end=YYYY-MM-DD`

Example request:

```bash
curl "http://localhost:8000/api/hyperliquid/0xcd82f03d5df801a69af899a7f13263388e1f6274/pnl?start=2026-02-25&end=2026-03-05"
```

Example response:

```json
{
  "wallet": "0xcd82f03d5df801a69af899a7f13263388e1f6274",
  "start": "2026-02-25",
  "end": "2026-03-05",
  "daily": [
    {
      "date": "2026-03-05",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 16.09,
      "net_pnl_usd": 16.09,
      "equity_usd": 1069.34
    },
    {
      "date": "2026-03-04",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 10.25,
      "net_pnl_usd": 10.25,
      "equity_usd": 1053.26
    },
    {
      "date": "2026-03-03",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": -3.48,
      "net_pnl_usd": -3.48,
      "equity_usd": 1043.01
    },
    {
      "date": "2026-03-02",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 10.94,
      "net_pnl_usd": 10.94,
      "equity_usd": 1046.48
    },
    {
      "date": "2026-03-01",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 7.17,
      "net_pnl_usd": 7.17,
      "equity_usd": 1035.54
    },
    {
      "date": "2026-02-28",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 23.1,
      "net_pnl_usd": 23.1,
      "equity_usd": 1028.36
    },
    {
      "date": "2026-02-27",
      "realized_pnl_usd": 0,
      "unrealized_pnl_usd": 0,
      "fees_usd": 0,
      "funding_usd": 0.73,
      "net_pnl_usd": 0.73,
      "equity_usd": 1005.26
    },
    {
      "date": "2026-02-26",
      "realized_pnl_usd": -3075.25,
      "unrealized_pnl_usd": 0,
      "fees_usd": 434.1,
      "funding_usd": -2.28,
      "net_pnl_usd": -3511.63,
      "equity_usd": 1004.54
    },
    {
      "date": "2026-02-25",
      "realized_pnl_usd": 5112.25,
      "unrealized_pnl_usd": 0,
      "fees_usd": 604.48,
      "funding_usd": 8.41,
      "net_pnl_usd": 4516.17,
      "equity_usd": 4516.17
    }
  ],
  "summary": {
    "total_realized_usd": 2036.99,
    "total_unrealized_usd": 0,
    "total_fees_usd": 1038.59,
    "total_funding_usd": 70.94,
    "net_pnl_usd": 1069.34
  },
  "diagnostics": {
    "data_source": "hyperliquid_api",
    "last_api_call": "2026-03-05T18:43:31.212360+00:00Z",
    "notes": "PnL calculated using daily close prices"
  }
}
```

## AI Setup (Groq)

We use Groq for fast, free inference.

1. Go to https://console.groq.com
2. Sign up / log in
3. Create a new API key
4. Paste it into `.env` as `GROQ_API_KEY=...`

Model used: `llama-3.1-8b-instant` (free, fast, reliable JSON output).

# Tests

Run test cases
```bash
# File wise
pytest tests/test_pnl.py -s -p no:warnings -vv

pytest tests/test_token.py -s -p no:warnings -vv

# Run all
pytest tests/ -s -p no:warnings -vv
```

## Project Structure

```bash
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── models/                 # Pydantic schemas
│   ├── routers/                # API routes
│   └── services/               # Business logic (CoinGecko, Groq, HyperLiquid)
├── tests/                      # pytest tests
├── logs/                       # log files
├── .env.example
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── .gitignore
└── README.md

```
