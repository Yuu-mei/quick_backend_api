from typing import List

from fastapi import Body, FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import httpx
from slowapi.errors import RateLimitExceeded
from igdb.services import get_franchise_games, get_game_additional_content, get_game_details, get_latest_games, get_popular_games, simple_search_games
from models.game import PopularityTypes
from models.requests import AdditionalContentRequest, FranchiseContentRequest
from utils.rate_limiter import limiter, rate_limit_handler
import utils.client as igdb_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    igdb_module.igdb_client = httpx.AsyncClient(
        timeout=20.0,
        http2=True
    )
    yield
    await igdb_module.igdb_client.aclose()

app = FastAPI(lifespan=lifespan)
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
    
@app.post("/games")
@limiter.limit("30/minute")
async def simple_search_games_endpoint(request: Request, search: str, limit: int = 50):
    return await simple_search_games(search_query=search, limit=limit)

@app.post("/games/dlcs")
@limiter.limit("30/minute")
async def get_game_additional_content_endpoint(request: Request, additional_content_request: AdditionalContentRequest = Body(...)):
    return await get_game_additional_content(dlc_ids=additional_content_request.dlc_ids, expansion_ids=additional_content_request.expansion_ids)

@app.post("/games/franchise")
@limiter.limit("30/minute")
async def get_franchise_games_endpoint(request: Request, franchise_game_ids: FranchiseContentRequest = Body(...)):
    franchise_ids = franchise_game_ids.franchise_ids
    return await get_franchise_games(franchise_game_ids=franchise_ids)

@app.post("/games/{game_id}")
@limiter.limit("30/minute")
async def get_game_details_endpoint(request: Request, game_id: int):
    return await get_game_details(game_id=game_id)