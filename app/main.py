from fastapi import FastAPI
from app.routers import token
import uvicorn

app = FastAPI(
    title="Token Insight APP",
    version="1.0.0"
)

app.include_router(token.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)