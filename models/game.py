from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from models.age_rating import AgeRatingResponse
from models.genre import GenreResponse

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
    
class WebsiteTypes(Enum):
    OFFICIAL = 1
    WIKIA =	2
    WIKIPEDIA =	3
    FACEBOOK =	4
    TWITTER =	5
    TWITCH =	6
    INSTAGRAM =	8
    YOUTUBE =	9
    IPHONE =	10
    IPAD =	11
    ANDROID =	12
    STEAM =	13
    REDDIT =	14
    ITCH =	15
    EPICGAMES =	16
    GOG =	17
    DISCORD =	18
    BLUESKY =	19
    
class WebsiteResponse(BaseModel):
    id: int;
    type: WebsiteTypes;
    url: str;

class GameResponseBase(BaseModel):
    id: int;
    name: str;
    cover_url: str;
    genres: Optional[List[GenreResponse]] = None;
    tags: Optional[List[int]] = None;
    age_ratings: Optional[List[AgeRatingResponse]] = None;
    release_date: Optional[str] = None;
    avg_rating: float;
    
class FranchiseResponse(BaseModel):
    id: int;
    name: str;
    games: Optional[List[GameResponseBase]] = None;

class GameDetailResponse(GameResponseBase):
    dlcs: Optional[List[int]] = None;
    expansions: Optional[List[int]] = None;
    franchise: Optional[List[int]] = None;
    parent_game: Optional[GameResponseBase] = None;
    
class GameAdditionalContentResponse(BaseModel):
    dlcs: List[GameResponseBase];
    expansions: List[GameResponseBase];
