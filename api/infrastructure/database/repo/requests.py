from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from api.infrastructure.database.repo.promo_campaign import PromoCampaignRepo
from api.infrastructure.database.repo.promo_interaction_log import PromoInteractionLogRepo
from api.infrastructure.database.repo.referral import ReferralRepo
from api.infrastructure.database.repo.referral_stats import ReferralStatsRepo
from api.infrastructure.database.repo.stickers import StickerRepo
from api.infrastructure.database.repo.discounts import DiscountRepo
from api.infrastructure.database.repo.gate_bot import GateBotRepo
from api.infrastructure.database.repo.payments import PaymentRepo
from api.infrastructure.database.repo.product_categories import ProductCategoryRepo
from api.infrastructure.database.repo.product_discounts import ProductDiscountRepo
from api.infrastructure.database.repo.products import ProductRepo
from api.infrastructure.database.repo.referral_transactions import ReferralTransactionRepo
from api.infrastructure.database.repo.user_gate_entries import UserGateEntryRepo
from api.infrastructure.database.repo.user_subscriptions import UserSubscriptionRepo
from api.infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def discounts(self) -> DiscountRepo:
        return DiscountRepo(self.session)

    @property
    def gate_bots(self) -> GateBotRepo:
        return GateBotRepo(self.session)

    @property
    def payments(self) -> PaymentRepo:
        return PaymentRepo(self.session)

    @property
    def product_categories(self) -> ProductCategoryRepo:
        return ProductCategoryRepo(self.session)

    @property
    def product_discounts(self) -> ProductDiscountRepo:
        return ProductDiscountRepo(self.session)

    @property
    def products(self) -> ProductRepo:
        return ProductRepo(self.session)

    @property
    def referral_transactions(self) -> ReferralTransactionRepo:
        return ReferralTransactionRepo(self.session)

    @property
    def user_gate_entries(self) -> UserGateEntryRepo:
        return UserGateEntryRepo(self.session)

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def stickers(self) -> StickerRepo:
        return StickerRepo(self.session)

    @property
    def referrals(self) -> ReferralRepo:
        return ReferralRepo(self.session)

    @property
    def referral_stats(self) -> ReferralStatsRepo:
        return ReferralStatsRepo(self.session)

    @property
    def promo_campaigns(self) -> PromoCampaignRepo:
        return PromoCampaignRepo(self.session)

    @property
    def promo_interactions(self) -> PromoInteractionLogRepo:
        return PromoInteractionLogRepo(self.session)

    @property
    def user_subscriptions(self) -> UserSubscriptionRepo:
        return UserSubscriptionRepo(self.session)