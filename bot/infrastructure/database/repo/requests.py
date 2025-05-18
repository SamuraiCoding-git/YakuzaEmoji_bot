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
    def audit_log(self) -> AuditLogRepo:
        return AuditLogRepo(self.session)

    @property
    def discount(self) -> DiscountRepo:
        return DiscountRepo(self.session)

    @property
    def gate_bot(self) -> GateBotRepo:
        return GateBotRepo(self.session)

    @property
    def payment(self) -> PaymentRepo:
        return PaymentRepo(self.session)

    @property
    def product_category(self) -> ProductCategoryRepo:
        return ProductCategoryRepo(self.session)

    @property
    def product_discount(self) -> ProductDiscountRepo:
        return ProductDiscountRepo(self.session)

    @property
    def product(self) -> ProductRepo:
        return ProductRepo(self.session)

    @property
    def referral_transaction(self) -> ReferralTransactionRepo:
        return ReferralTransactionRepo(self.session)

    @property
    def report(self) -> ReportRepo:
        return ReportRepo(self.session)

    @property
    def user_gate_entry(self) -> UserGateEntryRepo:
        return UserGateEntryRepo(self.session)

    @property
    def user(self) -> UserRepo:
        return UserRepo(self.session)