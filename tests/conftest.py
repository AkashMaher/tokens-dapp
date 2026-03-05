from logging.handlers import RotatingFileHandler
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers import pnl, token
import logging 


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "app.log")

handler = RotatingFileHandler(
    filename=log_file,
    mode="a",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
    delay=False,
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
handler.setFormatter(formatter)
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler, console_handler],
)


logger = logging.getLogger(__name__)

@pytest.fixture
def app():
    _app = FastAPI(
        title="Test Token Insight & Hyperliquid App with AI", version="1.0.2"
    )

    _app.include_router(token.router, prefix="/api")
    _app.include_router(pnl.router, prefix="/api")


    return _app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        c.app = app
        c.logger = logger
        yield c
