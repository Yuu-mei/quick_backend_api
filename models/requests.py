from typing import List, Optional

from pydantic import BaseModel


class AdditionalContentRequest(BaseModel):
    dlc_ids: Optional[List[int]] = None
    expansion_ids: Optional[List[int]] = None