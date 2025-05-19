from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from bot.infrastructure.database.repo.audit_logs import AuditLogRepo
from bot.infrastructure.database.repo.discounts import DiscountRepo
from bot.infrastructure.database.repo.gate_bot_repo import GateBotRepo
from bot.infrastructure.database.repo.payments import PaymentRepo
from bot.infrastructure.database.repo.product_categories import ProductCategoryRepo
from bot.infrastructure.database.repo.product_discounts import ProductDiscountRepo
from bot.infrastructure.database.repo.products import ProductRepo
from bot.infrastructure.database.repo.referral_transactions import ReferralTransactionRepo
from bot.infrastructure.database.repo.reports import ReportRepo
from bot.infrastructure.database.repo.user_gate_entries import UserGateEntryRepo
from bot.infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def audit_logs(self) -> AuditLogRepo:
        return AuditLogRepo(self.session)

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
    def reports(self) -> ReportRepo:
        return ReportRepo(self.session)

    @property
    def user_gate_entries(self) -> UserGateEntryRepo:
        return UserGateEntryRepo(self.session)

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)