from pydantic import BaseModel
from typing import Optional

class GeneratePackResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    status_url: Optional[str] = None
    message: Optional[str] = None


class ProgressResponse(BaseModel):
    status: str
    progress: int
    message: str
    sticker_pack_url: Optional[str] = None