from pydantic import BaseModel
from typing import Optional

class GeneratePackResponse(BaseModel):
    success: bool
    link: str


class ProgressResponse(BaseModel):
    status: str
    progress: int
    message: str
    sticker_pack_url: Optional[str] = None