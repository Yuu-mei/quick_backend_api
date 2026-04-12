from typing import List

from igdb.client import igdb_request
from igdb.helpers import build_image_url, format_release_date
from models.game import FranchiseResponse, GameAdditionalContentResponse, GameDetailResponse, GameResponseBase, PopularityTypes, WebsiteResponse

async def get_latest_games(limit: int) -> List[GameResponseBase]:
    """ Returns the latest games with the release date formated and the image url already built
    """
    res: List[GameResponseBase] = []

    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; limit {limit}; sort first_release_date desc;")
    if(not games):
        return res
    
    #Cover images
    for game in games:
        await add_game_base_data(game_list=res, game=game)

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
    popular_games = await igdb_request("popularity_primitives", f"fields game_id, value, popularity_type; sort value desc; limit ${limit}; where popularity_type={popularity_type.value};")
    
    #List of games from the previous popularity
    for popular_game in popular_games:
        game = await get_game_base(popular_game.get("game_id"))
        await add_game_base_data(game_list=res, game=game)
        
    return res

async def simple_search_games(limit: int, search_query: str) -> List[GameResponseBase]:
    """Simple search method that accepts search by name parameter and sorts them by the rating
    """
    res: List[GameResponseBase] = []
    
    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; search \"{search_query}\"; limit ${limit};")
    
    for game in games:
        await add_game_base_data(game_list=res, game=game)
        
    return res;

async def get_game_details(game_id: int) -> GameDetailResponse:
    """Returns a more detailed view of the game, leaving the dlcs, expansion and franchises to other calls in order to avoid connection timeouts 
    (retaining the ids so that the app can them do the calls without retrieving the game again)
    """
    game_res = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date, dlcs, expansions, franchises, parent_game, websites; where id = {game_id};")
    game = game_res[0]
    
    #Cover
    game_cover = await get_game_cover(game["cover"]) if game.get("cover") else ""

    #Get dlc ids
    dlcs: List[int] = game.get("dlcs", [])
            
    #Get expansion ids
    expansions: List[int] = game.get("expansions", [])
            
    #Get franchise ids
    franchises: List[int] = game.get("franchises", [])
    
    #Find the parent game if any
    parent_game: GameResponseBase|None = None
    if(game.get("parent_game")):
        parent_game_res = await get_game_base(game["parent_game"])
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
        parent_game= parent_game
    )
    
async def get_game_additional_content(dlc_ids: List[int], expansion_ids: List[int]) -> GameAdditionalContentResponse:
    #Find dlcs if any
    dlcs: List[GameResponseBase] = []
    if(dlc_ids):
        dlc_list = await get_game_base(dlc_ids)
        for dlc in dlc_list:
            await add_game_base_data(game_list=dlcs, game=dlc)
            
    #Find expansions if any
    expansions: List[GameResponseBase] = []
    if(expansion_ids):
        expansion_list = await get_game_base(expansion_ids)
        for expansion in expansion_list:
            await add_game_base_data(game_list=expansions, game=expansion)
            
    return GameAdditionalContentResponse(
        dlcs= dlcs,
        expansions= expansions
    )
    
async def get_franchise_games(franchise_game_ids: List[int]) -> List[GameResponseBase]:
    franchise_games: List[GameResponseBase] = []
    if(franchise_game_ids):
        franchise_game_list = await get_game_base(franchise_game_ids)
        
        for franchise_game in franchise_game_list:
            await add_game_base_data(game_list=franchise_games, game=franchise_game)
            
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

async def get_game_cover(cover_id: int) -> str:
    """Returns image url by a given cover_id
    """ 
    cover = await igdb_request("covers", f"fields image_id; where id = {cover_id};")
    image_id = cover[0]["image_id"]
    return build_image_url(image_id=image_id)

async def get_game_franchise_data(franchise_id: int):
    """Returns the franchise related to the game
    """
    return await igdb_request("franchises", f"fields id, name, games; where id = {franchise_id};")

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