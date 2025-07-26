# main.py
from fastapi import FastAPI
from receipt_agent import router as receipt_router
from analytics_agent import router as analytics_router
from game_agent import router as game_router
from wallet_agent import router as wallet_router
from root_agent import router as root_router

app = FastAPI()

app.include_router(root_router)
app.include_router(receipt_router, prefix="/receipt", tags=["Receipt Processing"])
app.include_router(analytics_router, prefix="/analytics", tags=["Financial Analytics"])
app.include_router(game_router, prefix="/game", tags=["Gamification"])
app.include_router(wallet_router, prefix="/wallet", tags=["Digital Wallet"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
