from pydantic import BaseModel
    
class AgeRatingOrganizationResponse(BaseModel):
    id: int;
    name: str;
    
class AgeRatingCategoryResponse(BaseModel):
    id: int;
    organization: int;
    rating_name: str;
    
class AgeRatingResponse(BaseModel):
    id: int;
    rating_category: AgeRatingCategoryResponse;
    rating_cover_url: str;
    rating_organization: AgeRatingOrganizationResponse;

