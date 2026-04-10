from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from igdb.services import get_latest_games
from utils.rate_limiter import limiter, rate_limit_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.post("/games/popular")
@limiter.limit("30/minute")
async def get_latest_games_endpoint(request: Request, limit: int = 10):
    return await get_latest_games(limit=limit)