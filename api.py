from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
import httpx
import os
import time

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

TOKEN_CACHE = {"access_token": None, "expires_at": 0}


async def get_token():
    if TOKEN_CACHE["access_token"] and TOKEN_CACHE["expires_at"] > time.time():
        return TOKEN_CACHE["access_token"]

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get token")

        data = r.json()
        TOKEN_CACHE["access_token"] = data["access_token"]
        TOKEN_CACHE["expires_at"] = time.time() + data["expires_in"] - 60

        return TOKEN_CACHE["access_token"]

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

@app.post("/igdb/{endpoint}")
@limiter.limit("30/minute")
async def igdb_proxy(request: Request,endpoint: str, body: str = Body(...)):
    token = await get_token()

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }

    url = f"https://api.igdb.com/v4/{endpoint}"

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, content=body)

    return r.json()