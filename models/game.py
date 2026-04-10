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
    release_date: str;
    avg_rating: float;

class GameDetailResponse(GameResponseBase):
    dlcs: Optional[List[GameResponseBase]];
    expansions: Optional[List[GameResponseBase]];
    franchise: Optional[str];
    parent_game: Optional[GameResponseBase];
    websites: Optional[str];

