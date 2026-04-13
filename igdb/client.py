from fastapi import Body
from pydantic import Json
from utils.token import CLIENT_ID, get_token
import utils.client as igdb_module


async def igdb_request(endpoint: str, body: str = Body(..., media_type="text/plain")) -> Json:
    token = await get_token()

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }

    url = f"https://api.igdb.com/v4/{endpoint}"
    
    res = await igdb_module.igdb_client.post(url=url, headers=headers, content=body)
    res.raise_for_status()
    return res.json()