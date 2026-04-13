import asyncio
from typing import List

from igdb.client import igdb_request
from igdb.helpers import build_game_base_data, build_image_url, format_release_date
from models.age_rating import AgeRatingCategoryResponse, AgeRatingOrganizationResponse, AgeRatingResponse
from models.game import GameAdditionalContentResponse, GameDetailResponse, GameResponseBase, PopularityTypes, WebsiteResponse
from models.genre import GenreResponse

COVER_CACHE: dict[int, str] = {}

async def get_latest_games(limit: int) -> List[GameResponseBase]:
    """ Returns the latest games with the release date formated and the image url already built
    """
    res: List[GameResponseBase] = []

    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; limit {limit}; sort first_release_date desc;")
    if(not games):
        return res
    
    #Cover images
    game_covers_ids = [game["cover"] for game in games if game.get("cover")]
    game_covers_dict = await get_game_covers(cover_ids=game_covers_ids)
    
    for game in games:
        build_game_base_data(game_list=res, game=game, cover=game_covers_dict)

    return res

async def get_popular_games(limit: int, popularity_type: PopularityTypes) -> List[GameResponseBase]:
    """ Returns the most popular games according to the type given
    Popularity types:
        1- IGDB Visits
        2- IGDB Want to Play
        3- IGDB Playing
        4- IGDB Played
        5- Steam 24h Peak Players
        6- Steam Positive Reviews
        7- Steam Negative Reviews
        8- Steam Total Reviews
        9- Steam Global Top Sellers
        10- Most Wishlisted Upcoming
        11- Twitch Hours Watched
    """
    res: List[GameResponseBase] = []
    
    #List of game ids of popular games
    popular_games = await igdb_request("popularity_primitives", f"fields game_id, value, popularity_type; sort value desc; limit {limit}; where popularity_type={popularity_type.value};")
    
    #List of games from the previous popularity
    popular_games_ids = [game["game_id"] for game in popular_games]
    popular_games_list = await get_game_base(popular_games_ids)
    
    popular_games_covers_ids = [game["cover"] for game in popular_games_list if game.get("cover")]
    popular_games_covers_dict = await get_game_covers(cover_ids=popular_games_covers_ids)
    
    for popular_game in popular_games_list:
        build_game_base_data(game_list=res, game=popular_game, cover=popular_games_covers_dict)
        
    return res

async def simple_search_games(limit: int, search_query: str) -> List[GameResponseBase]:
    """Simple search method that accepts search by name parameter and sorts them by the rating
    """
    res: List[GameResponseBase] = []
    
    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; search \"{search_query}\"; limit {limit};")
    
    #Cover images
    game_covers_ids = [game["cover"] for game in games if game.get("cover")]
    game_covers_dict = await get_game_covers(cover_ids=game_covers_ids)
    
    for game in games:
        build_game_base_data(game_list=res, game=game, cover=game_covers_dict)
        
    return res;

async def get_game_details(game_id: int) -> GameDetailResponse:
    """Returns a more detailed view of the game, leaving the dlcs, expansion and franchises to other calls in order to avoid connection timeouts 
    (retaining the ids so that the app can them do the calls without retrieving the game again)
    """
    game_res = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, first_release_date, dlcs, expansions, franchises, parent_game, websites; where id = {game_id};")
    game = game_res[0]
    
    #Cover
    game_cover: str = ""
    game_cover_task = (
        get_game_cover(game["cover"]) 
        if game.get("cover") 
        else asyncio.sleep(0, "")
    )

    #Get dlc ids
    dlcs: List[int] = game.get("dlcs", [])
            
    #Get expansion ids
    expansions: List[int] = game.get("expansions", [])
            
    #Get franchise ids
    franchises: List[int] = game.get("franchises", [])
    
    #Find the parent game if any
    parent_game_res = None
    parent_game: GameResponseBase | None = None
    parent_game_task = (
        get_game_base(game["parent_game"])
        if game.get("parent_game")
        else asyncio.sleep(0, None)
    )
        
    #Get genres
    genre_ids: List[int] = game.get("genres", [])
    genres_list: GenreResponse | List[GenreResponse] = []
    genres_task = get_game_genres(genre_ids)
    
    #Get age ratings
    age_ratings_ids: List[int] = game.get("age_ratings", [])
    age_ratings_list: AgeRatingResponse | List[AgeRatingResponse] = []
    age_ratings_task = get_game_age_ratings(age_ratings_ids)
    
    #Execute async tasks
    game_cover, parent_game_res, genres_list, age_ratings_list = await asyncio.gather(game_cover_task, parent_game_task, genres_task, age_ratings_task)
    
    #Build parent game if any
    if(parent_game_res):
        parent_game_cover = await get_game_cover(parent_game_res["cover"]) if parent_game_res.get("cover") else ""
        
        parent_game = GameResponseBase(
            id= parent_game_res.get("id"),
            name= parent_game_res.get("name", "???"),
            cover_url= parent_game_cover,
            avg_rating= parent_game_res.get("aggregated_rating", -1.0)
        )
    

    return GameDetailResponse(
        id= game.get("id"),
        name= game.get("name", "???"),
        cover_url= game_cover,
        release_date= format_release_date(game["first_release_date"]) if game.get("first_release_date") else "Unknown",
        avg_rating= game.get("aggregated_rating", -1.0),
        dlcs= dlcs,
        expansions= expansions,
        franchise= franchises,
        parent_game= parent_game,
        genres= genres_list,
        age_ratings= age_ratings_list
    )
    
async def get_game_additional_content(dlc_ids: List[int], expansion_ids: List[int]) -> GameAdditionalContentResponse:
    #Find dlcs if any
    dlcs: List[GameResponseBase] = []
    if(dlc_ids):
        dlc_list = await get_game_base(dlc_ids)
        dlc_cover_ids = [game["cover"] for game in dlc_list if game.get("cover")]
        dlc_cover_dict = await get_game_covers(cover_ids=dlc_cover_ids)
        
        for dlc in dlc_list:
            build_game_base_data(game_list=dlcs, game=dlc, cover=dlc_cover_dict)
            
    #Find expansions if any
    expansions: List[GameResponseBase] = []
    if(expansion_ids):
        expansion_list = await get_game_base(expansion_ids)
        expansion_cover_ids = [game["cover"] for game in expansion_list if game.get("cover")]
        expansion_cover_dict = await get_game_covers(cover_ids=expansion_cover_ids)
        
        for expansion in expansion_list:
            build_game_base_data(game_list=dlcs, game=expansion, cover=expansion_cover_dict)
            
    return GameAdditionalContentResponse(
        dlcs= dlcs,
        expansions= expansions
    )
    
async def get_franchise_games(franchise_game_ids: List[int]) -> List[GameResponseBase]:
    franchise_games: List[GameResponseBase] = []
    if(franchise_game_ids):
        franchise_game_list = await get_game_base_by_franchise(franchise_game_ids)
        
        franchise_game_cover_ids = [game["cover"] for game in franchise_game_list if game.get("cover")]
        franchise_game_cover_dict = await get_game_covers(franchise_game_cover_ids)
        
        for game in franchise_game_list:
            build_game_base_data(game_list=franchise_games, game=game, cover=franchise_game_cover_dict)
            
    return franchise_games
    
    
async def get_game_base(game_id: int | List[int]) -> dict | List[dict]:
    """Returns general base result for the main discovery page based on a single (or multiple) game id
    """ 
    if(isinstance(game_id, int)):
        game = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; where id = {game_id};");
        return game[0]
    
    ids = ",".join(map(str, game_id))
    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; where id = ({ids});");
    return games

async def get_game_base_by_franchise(franchise_id: List[int]) -> dict | List[dict]:
    """Returns the base game response for all games from a franchise
    """ 
    if(len(franchise_id) > 1):
        ids = ",".join(map(str, franchise_id))
        return await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date, franchises; where franchises = ({ids});");
    
    return await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date, franchises; where franchises = {franchise_id[0]};");

async def get_game_cover(cover_id: int) -> str:
    """Returns image url by a given cover_id
    """ 
    cover = await igdb_request("covers", f"fields image_id; where id = {cover_id};")
    image_id = cover[0]["image_id"]
    return build_image_url(image_id=image_id)

async def get_game_covers(cover_ids: List[int]) -> dict[int, str]:
    if(not cover_ids):
        return {}
    
    ids = ",".join(map(str, cover_ids))
    covers = await igdb_request("covers", f"fields image_id; where id = ({ids});")
    
    return {
        cover["id"]: build_image_url(cover["image_id"])
        for cover in covers
    }

async def get_game_franchise_data(franchise_id: int):
    """Returns the franchise related to the game
    """
    return await igdb_request("franchises", f"fields id, name, games; where id = {franchise_id};")

async def get_game_genres(genre_id: int | List[int]) -> List[GenreResponse] | GenreResponse:
    """Returns the name of a given genre id
    """
    if(isinstance(genre_id, int)):
        genre = await igdb_request("genres", f"fields id, name; where id = {genre_id};")
        return GenreResponse(
            id = genre_id,
            name = genre.get("name", "")
        )
        
    ids = ",".join(map(str, genre_id))
    genres = await igdb_request("genres", f"fields id, name; where id = ({ids});")
    
    genre_list: List[GenreResponse] = []
    for genre in genres:
        genre_list.append(
            GenreResponse(
                id = genre.get("id"),
                name = genre.get("name", "")
            )
        )
    return genre_list

async def get_game_age_ratings(age_rating_id: int | List[int]) -> List[AgeRatingResponse] | AgeRatingResponse:
    if(isinstance(age_rating_id, int)):
        age_rating = await igdb_request("age_ratings", f"fields id, rating_category, rating_cover_url, organization; where id = {age_rating_id};")
        age_rating_category_res = await igdb_request("age_rating_categories", f"fields id, rating, organization; where id = {age_rating["rating_category"]};")
        age_rating_organization_res = await igdb_request("age_rating_organizations", f"fields id, name; where id = {age_rating["organization"]};")
        
        age_rating_organization = AgeRatingOrganizationResponse(
                id= age_rating_organization_res.get("id"),
                name= age_rating_organization_res.get("name", "")
        )
        
        age_rating_category = AgeRatingCategoryResponse(
            id= age_rating_category_res.get("id"),
            organization= age_rating_organization.id,
            rating_name= age_rating_category_res.get("rating", "")
        )
        
        return AgeRatingResponse(
            id = age_rating_id,
            rating_organization= age_rating_organization,
            rating_category= age_rating_category
        )
        
    ids = ",".join(map(str, age_rating_id))
    age_ratings = await igdb_request("age_ratings", f"fields id, rating_category, rating_cover_url, organization; where id = ({ids});")
    
    category_ids = {age_rating["rating_category"] for age_rating in age_ratings if age_rating.get("rating_category")}
    organization_ids = {age_rating["organization"] for age_rating in age_ratings if age_rating.get("organization")}
    
    categories = {}
    if(category_ids):
        category_ids_list = ",".join(map(str, category_ids))
        category_res = await igdb_request("age_rating_categories", f"fields id, rating, organization; where id = ({category_ids_list});")
        categories = {cat["id"]: cat for cat in category_res}
        
    organizations = {}
    if(organization_ids):
        organization_ids_list = ",".join(map(str, organization_ids))
        organization_res = await igdb_request("age_rating_organizations", f"fields id, name; where id = ({organization_ids_list});")
        organizations = {org["id"]: org for org in organization_res}
    
    age_rating_list: List[AgeRatingResponse] = []
    for age_rating in age_ratings:
        category_raw = categories.get(age_rating["rating_category"])
        organization_raw = organizations.get(age_rating["organization"])
        
        rating_org = AgeRatingOrganizationResponse(
            id= organization_raw.get("id"),
            name= organization_raw.get("name", "")
        ) if organization_raw else None
        
        rating_cat = AgeRatingCategoryResponse(
            id=category_raw["id"],
            organization=rating_org.id if rating_org else None,
            rating_name=category_raw.get("rating", "")
        ) if category_raw else None
        
        age_rating_list.append(
            AgeRatingResponse(
                id=age_rating["id"],
                rating_organization=rating_org,
                rating_category=rating_cat,
                rating_cover_url=age_rating.get("rating_cover_url", "")
            )
        )
    
    return age_rating_list

async def get_game_website(website_id: int | List[int]) -> List[WebsiteResponse]:
    """Returns the list of websites related to the game
    """
    if(isinstance(website_id, int)):
        return await igdb_request("websites", f"fields id, type, url; where id = {website_id};")
    
    ids = ",".join(map(str, website_id))
    return await igdb_request("websites", f"fields id, type, url; where id = ({ids});")

async def add_game_base_data(game_list:List[GameResponseBase], game: object):
    """Appends the game from the await to the given list
    """
    game_cover = await get_game_cover(game["cover"]) if game.get("cover") else ""
    game_list.append(
        GameResponseBase(
            id= game.get("id"),
            name= game.get("name", "???"),
            cover_url= game_cover,
            release_date= format_release_date(game["first_release_date"]) if game.get("first_release_date") else "Unknown",
            avg_rating= game.get("aggregated_rating", -1.0)
        )
    )