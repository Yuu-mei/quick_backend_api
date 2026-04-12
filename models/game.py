from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from models.age_rating import AgeRatingResponse
from models.genre import GenreResponse

class GameResponseBase(BaseModel):
    id: int;
    name: str;
    cover_url: str;
    genres: Optional[List[GenreResponse]] = None;
    tags: Optional[List[int]] = None;
    age_ratings: Optional[List[AgeRatingResponse]] = None;
    release_date: Optional[str] = None;
    avg_rating: float;

class GameDetailResponse(GameResponseBase):
    dlcs: Optional[List[GameResponseBase]];
    expansions: Optional[List[GameResponseBase]];
    franchise: Optional[str];
    parent_game: Optional[GameResponseBase];
    websites: Optional[str];

class PopularityTypes(Enum):
    IGDB_VISITS = 1
    IGDB_WANT_TO_PLAY = 2
    IGDB_PLAYING = 3
    IGDB_PLAYED = 4
    STEAM_24H_PEAK = 5
    STEAM_POSITIVE_REVIEWS = 6
    STEAM_NEGATIVE_REVIEWS = 7
    STEAM_TOTAL_REVIEWS = 8
    STEAM_TOP_SELLERS = 9
    STEAM_TOP_WISHLIST = 10
    TWITCH_HOURS_WATCHED = 11