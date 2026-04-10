from fastapi import HTTPException
import os
import time
import httpx

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