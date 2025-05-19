from sqlalchemy.future import select
from sqlalchemy import insert
from typing import Optional, List
from api.infrastructure.database.models import Sticker
from .base import BaseRepo


class StickerRepo(BaseRepo):
    async def create_sticker(
        self,
        user_id: int,
        sticker_name: str,
        sticker_type: str,
        file_id: str,
        width: int,
        height: int,
        durations: Optional[dict] = None
    ) -> Sticker:
        """Создать новый стикер с дополнительными аттрибутами и таймингами"""
        insert_stmt = (
            insert(Sticker)
            .values(
                user_id=user_id,
                sticker_name=sticker_name,
                sticker_type=sticker_type,
                file_id=file_id,
                width=width,
                height=height,
                durations=durations or {}
            )
            .returning(Sticker)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_sticker_by_id(self, sticker_id: int) -> Optional[Sticker]:
        return await self.session.get(Sticker, sticker_id)

    async def get_stickers_by_user(self, user_id: int) -> List[Sticker]:
        result = await self.session.execute(select(Sticker).filter_by(user_id=user_id))
        return result.scalars().all()

    async def get_all_stickers(self) -> List[Sticker]:
        result = await self.session.execute(select(Sticker))
        return result.scalars().all()

    async def update_sticker(
        self,
        sticker_id: int,
        sticker_name: Optional[str] = None,
        sticker_type: Optional[str] = None,
        file_id: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        durations: Optional[dict] = None
    ) -> Optional[Sticker]:
        sticker = await self.get_sticker_by_id(sticker_id)
        if sticker:
            if sticker_name: sticker.sticker_name = sticker_name
            if sticker_type: sticker.sticker_type = sticker_type
            if file_id: sticker.file_id = file_id
            if width: sticker.width = width
            if height: sticker.height = height
            if durations: sticker.durations = durations
            await self.session.commit()
            return sticker
        return None

    async def delete_sticker(self, sticker_id: int) -> bool:
        sticker = await self.get_sticker_by_id(sticker_id)
        if sticker:
            await self.session.delete(sticker)
            await self.session.commit()
            return True
        return False