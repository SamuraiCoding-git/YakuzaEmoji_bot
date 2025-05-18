from sqlalchemy import Integer, String, Boolean, ForeignKey, BIGINT
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class User(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, unique=True, nullable=False)
    full_name = mapped_column(String(255), nullable=False)
    username = mapped_column(String(255), nullable=True)
    referred_by = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    is_premium = mapped_column(Boolean, default=False)

    referred_by_user = relationship("User", remote_side=[id], backref="referrals")
    payments = relationship("Payment", back_populates="user")
    gate_entries = relationship("UserGateEntry", back_populates="user", cascade="all, delete-orphan")
    owned_gate_bots = relationship("GateBot", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    referral_transactions = relationship(
        "ReferralTransaction",
        foreign_keys="[ReferralTransaction.referral_user_id]",
        back_populates="referral_user",
        cascade="all, delete-orphan"
    )

    referred_transactions = relationship(
        "ReferralTransaction",
        foreign_keys="[ReferralTransaction.referred_user_id]",
        back_populates="referred_user",
        cascade="all, delete-orphan"
    )