from fastapi import FastAPI, HTTPException, Request
from slowapi.errors import RateLimitExceeded
from igdb.services import get_latest_games, get_popular_games, simple_search_games
from models.game import PopularityTypes
from utils.rate_limiter import limiter, rate_limit_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.post("/games/latest")
@limiter.limit("30/minute")
async def get_latest_games_endpoint(request: Request, limit: int = 10):
    return await get_latest_games(limit=limit)

@app.post("/games/popular/{type}")
@limiter.limit("30/minute")
async def get_popular_games_endpoint(request: Request, type: int = 9, limit: int = 10):
    try:
        popularity_type = PopularityTypes(type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid popularity type, must be between 1 and 11"
        )
        
    return await get_popular_games(limit=limit, popularity_type=popularity_type)
    
@app.post("/games/{search}")
@limiter.limit("30/minute")
async def simple_search_games_endpoint(request: Request, search: str, limit: int = 50):
    return await simple_search_games(search_query=search, limit=limit)