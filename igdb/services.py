from typing import List

from igdb.client import igdb_request
from igdb.helpers import build_image_url, format_release_date
from models.game import GameResponseBase, PopularityTypes

async def get_latest_games(limit: int) -> List[GameResponseBase]:
    """ Returns the latest games with the release date formated and the image url already built
    """
    res: List[GameResponseBase] = [];

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
    res: List[GameResponseBase] = [];
    
    #List of game ids of popular games
    popular_games = await igdb_request("popularity_primitives", f"fields game_id, value, popularity_type; sort value desc; limit ${limit}; where popularity_type={popularity_type.value};")
    
    #List of games from the previous popularity
    for popular_game in popular_games:
        game = await get_game_base(popular_game.get("game_id"))
        await add_game_base_data(game_list=res, game=game)
        
    return res

async def simple_search_games(limit: int, search_query: str):
    """Simple search method that accepts search by name parameter and sorts them by the rating
    """
    res: List[GameResponseBase] = [];
    
    games = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; search \"{search_query}\"; limit ${limit};")
    
    for game in games:
        await add_game_base_data(game_list=res, game=game)
        
    return res;
    
async def get_game_base(game_id: int) -> dict:
    """Returns general base result for the main discovery page based on a given game id
    """ 
    game = await igdb_request("games", f"fields id, name, age_ratings, aggregated_rating, cover, genres, tags, first_release_date; where id={game_id};");
    return game[0]

async def get_game_cover(cover_id: int) -> str:
    """Returns image url by a given cover_id
    """ 
    cover = await igdb_request("covers", f"fields image_id; where id = {cover_id};")
    image_id = cover[0]["image_id"]
    return build_image_url(image_id=image_id)

async def add_game_base_data(game_list:List[GameResponseBase], game: object):
    """Appends the game from the await to the given list
    """
    game_cover = await get_game_cover(game["cover"]) if game.get("cover") is not None else ""
    game_list.append(
        GameResponseBase(
            id=game.get("id"),
            name=game.get("name", "???"),
            cover_url=game_cover,
            release_date=format_release_date(game["first_release_date"]) if game.get("first_release_date") else "Unknown",
            avg_rating=game.get("aggregated_rating", -1.0)
        )
    )