from pydantic import BaseModel, Field
from typing import Literal, Optional

class GeneratePackRequest(BaseModel):
    media_type: Literal["photo", "video", "document"]
    file_id: str
    width: Optional[int] = Field(default=100, ge=100, le=1200)
    height: Optional[int] = Field(default=100, ge=100, le=10000)
    user_id: int
    referral_bot_name: Optional[str] = None
    # priority: int = Field(default=5, ge=0, le=9, description="0 - наивысший, 9 - низший приоритет")