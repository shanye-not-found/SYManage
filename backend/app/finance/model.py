# 抽象一个FinanceRecord，关联唯一event_id
# 一个FinanceRecord对应一个可能的InvoiceReceipt
# 单个record只能增加或减少
# 每次新增record都更新对应financeRecord的盈亏情况
# 根据financeRecord的盈亏情况，实时计算当前余额

from sqlmodel import Field, Relationship, SQLModel
import uuid
from enum import Enum
from sqlalchemy import Column, Numeric
from decimal import Decimal
import datetime
from sqlalchemy.types import DateTime

def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

class FinanceDirection(str, Enum):
    income = "income"
    expense = "expense"
    
class FinanceRecord(SQLModel, table=True):
    __tablename__ = "finance_record"  # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    direction: FinanceDirection = Field(nullable=False)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    description: str = Field()
    created_by_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")
    created_at: datetime.datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    is_deleted: bool = Field(default=False)
    current_treasurer_id: uuid.UUID = Field(nullable=False)
    current_treasurer_name: str = Field(nullable=False)
    
    invoice_receipt: "InvoiceReceipt" | None = Relationship(back_populates="finance_record")  # type: ignore
    
        
        
    # event_id: uuid.UUID = Field(nullable=False, foreign_key="event.id")


class InvoiceReceipt(SQLModel, table=True):
    __tablename__ = "invoice_receipt"  # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=True))
    direction: FinanceDirection = Field(nullable=True)

    finance_record_id: uuid.UUID = Field(nullable=False, foreign_key="finance_record.id")
    finance_record: 'FinanceRecord' = Relationship(back_populates="invoice_receipts")