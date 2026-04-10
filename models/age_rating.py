from enum import Enum

from pydantic import BaseModel

class OrganizationEnum(Enum):
    ESRB = 1;
    PEGI = 2;
    CERO = 3;
    USK = 4;
    GRAC = 5;
    CLASS_IND = 6;
    ACB = 7;

class RatingCategoryResponse(BaseModel):
    organization: int;
    rating: str;

class AgeRatingResponse(BaseModel):
    organization: OrganizationEnum;
    rating: RatingCategoryResponse;

