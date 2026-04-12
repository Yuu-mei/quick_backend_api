from datetime import datetime


def build_image_url(image_id: str, size="t_cover_big") -> str:
    """Helper function that returns the full url of the cover image given an image_id and size parameters
    """
    return f"https://images.igdb.com/igdb/image/upload/{size}/{image_id}.jpg"

def format_release_date(date: int) -> str:
    """Helper function that formats unix timestamp into Y-M-D format
    """
    return datetime.fromtimestamp(date).strftime("%Y-%m-%d")