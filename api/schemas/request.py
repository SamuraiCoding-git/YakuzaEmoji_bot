from pydantic import BaseModel, Field
from typing import Literal, Optional

class GeneratePackRequest(BaseModel):
    media_type: Literal["photo", "video", "document"]
    file_id: str
    width: Optional[int] = Field(default=100, ge=100, le=1200)
    height: Optional[int] = Field(default=100, ge=100, le=10000)
    user_id: int