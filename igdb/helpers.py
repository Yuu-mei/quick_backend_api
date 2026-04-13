from datetime import datetime
from typing import List

from models.game import GameResponseBase


def build_image_url(image_id: str, size="t_cover_big") -> str:
    """Helper function that returns the full url of the cover image given an image_id and size parameters
    """
    return f"https://images.igdb.com/igdb/image/upload/{size}/{image_id}.jpg"

def format_release_date(date: int) -> str:
    """Helper function that formats unix timestamp into Y-M-D format
    """
    return datetime.fromtimestamp(date).strftime("%Y-%m-%d")

def build_game_base_data(game_list:List[GameResponseBase], game: object, cover: dict[int, str]):
    """Helper function to build the game base data and add it to a list
    """
    game_list.append(
        GameResponseBase(
            id= game.get("id"),
            name= game.get("name", "???"),
            cover_url= cover.get(game.get("cover")),
            release_date= format_release_date(game["first_release_date"]) if game.get("first_release_date") else "Unknown",
            avg_rating= game.get("aggregated_rating", -1.0)
        )
    )