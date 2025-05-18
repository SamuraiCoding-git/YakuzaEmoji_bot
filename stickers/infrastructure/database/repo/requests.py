from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from stickers.infrastructure.database.repo.stickers import StickerRepo
from stickers.infrastructure.database.repo.telethon_sessions import TelethonSessionRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def telethon_sessions(self) -> TelethonSessionRepo:
        return TelethonSessionRepo(self.session)

    @property
    def stickers(self) -> StickerRepo:
        return StickerRepo(self.session)