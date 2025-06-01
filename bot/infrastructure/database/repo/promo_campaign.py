from typing import Optional, List
from sqlalchemy import select, insert, update

from api.infrastructure.database.models import PromoCampaign
from api.infrastructure.database.repo.base import BaseRepo


class PromoCampaignRepo(BaseRepo):
    async def create_campaign(
        self,
        title: str,
        message_text: str,
        media: Optional[dict] = None,
        keyboard: Optional[list] = None,
        total_sent: int = 0,
    ) -> PromoCampaign:
        stmt = (
            insert(PromoCampaign)
            .values(
                title=title,
                message_text=message_text,
                media=media,
                keyboard=keyboard,
                total_sent=total_sent
            )
            .returning(PromoCampaign)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[PromoCampaign]:
        return await self.session.get(PromoCampaign, campaign_id)

    async def get_all_campaigns(self) -> List[PromoCampaign]:
        result = await self.session.execute(select(PromoCampaign))
        return result.scalars().all()

    async def increment_sent_count(self, campaign_id: int, increment: int = 1) -> None:
        await self.session.execute(
            update(PromoCampaign)
            .where(PromoCampaign.id == campaign_id)
            .values(total_sent=PromoCampaign.total_sent + increment)
        )
        await self.session.commit()