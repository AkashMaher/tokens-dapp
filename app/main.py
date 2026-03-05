from fastapi import FastAPI
from app.routers import token, pnl
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import os

app = FastAPI(title="Token Insight App with AI", version="1.0.1")


# Log configs
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

# End log configs

app.include_router(token.router, prefix="/api")
app.include_router(pnl.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)