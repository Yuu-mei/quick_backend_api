from fastapi import Body
import httpx
from pydantic import Json
from utils.token import CLIENT_ID, get_token


async def igdb_request(endpoint: str, body: str = Body(..., media_type="text/plain")) -> Json:
    token = await get_token()

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }

    url = f"https://api.igdb.com/v4/{endpoint}"

    async with httpx.AsyncClient() as client:
        res = await client.post(url=url, headers=headers, content=body)
        res.raise_for_status()
        return res.json()