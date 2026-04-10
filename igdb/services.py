from datetime import datetime
from typing import List

from igdb.client import igdb_request
from models.game import GameResponseBase

def build_image_url(image_id: str, size="t_cover_big"):
    return f"https://images.igdb.com/igdb/image/upload/{size}/{image_id}.jpg"

def format_release_date(date: int) -> str:
    return datetime.fromtimestamp(date).strftime("%Y-%m-%d")

async def get_latest_games(limit: int) -> List[GameResponseBase]:
    res: List[GameResponseBase] = [];

    games = await igdb_request("games", f"fields name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; limit {limit}; sort first_release_date desc;")
    if(not games):
        return res
    
    #Cover images
    for game in games:
        game_cover = await get_game_cover(game["cover"])
        res.append(
            GameResponseBase(
                id=game["id"],
                name=game["name"],
                cover_url=game_cover,
                release_date=format_release_date(game["first_release_date"]),
                avg_rating=game.get("aggregated_rating", -1.0)
            )
        )

    return res

async def get_game_cover(cover_id: int) -> str:
    cover = await igdb_request("covers", f"fields image_id; where id = {cover_id};")
    image_id = cover[0]["image_id"]
    return build_image_url(image_id=image_id)