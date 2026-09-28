"""
FinancialTransaction — central ledger entry for the Finance module.

Each row represents a single financial event that affected a FinancialAccount.

Key design rules (Phase 2):
  - amount is always > 0.  Direction carries the sign (IN / OUT).
  - account_id is required; every transaction must reference a real account.
  - transaction_type is a controlled string value — validated in the schema layer.
  - reference_number is optional, indexed but NOT unique (Phase 4 will link multiple
    transaction types that may share reference prefixes).
  - Transactions are immutable after posting.  No update/delete is exposed on the API.
    A future Reversal mechanism will be introduced when needed.

Balance formula (implemented in Phase 5 reporting):
  current_balance = opening_balance
                  + SUM(amount WHERE direction='IN')
                  - SUM(amount WHERE direction='OUT')
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)

    # The financial account this transaction affects (required)
    account_id = Column(
        Integer,
        ForeignKey("financial_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # When the financial event occurred (defaults to now; can be set to a past date)
    transaction_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Type of financial event — controlled vocabulary validated in schema layer.
    # Possible values: SALE, PURCHASE, EXPENSE, PAYROLL, ASSET_PURCHASE,
    #                  OWNER_INVESTMENT, OTHER_INCOME, ADJUSTMENT
    transaction_type = Column(String(50), nullable=False, index=True)

    # Money direction — IN (money received by account) or OUT (money leaving account)
    direction = Column(String(10), nullable=False)

    # Always positive.  direction carries the sign semantics.
    amount = Column(Numeric(15, 2), nullable=False)

    # Human-readable explanation of the transaction
    description = Column(Text, nullable=True)

    # External or internal reference (invoice number, payroll run ID, etc.)
    # Optional, non-unique, indexed for fast lookup.
    reference_number = Column(String(100), nullable=True, index=True)

    # Audit trail
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    # Relationships
    account = relationship("FinancialAccount", back_populates="transactions")
    user = relationship("Users")
