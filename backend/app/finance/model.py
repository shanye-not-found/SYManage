from sqlmodel import Field, Relationship, SQLModel
import uuid
from enum import Enum
from sqlalchemy import Column, Numeric
from decimal import Decimal
import datetime
from sqlalchemy.types import DateTime
from typing import Optional

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
    created_by_username: str = Field(nullable=False) #只接受社长财务部长和superuser
    is_deleted: bool = Field(default=False)
    description: str = Field()
    created_at: datetime.datetime = Field(
            default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable=False)
        )
    current_treasurer_name: str = Field(nullable=False)
    
    
    single_records: list['SingleRecord'] = Relationship(back_populates="finance_record")  # type: ignore
    
    
    # event_id: uuid.UUID = Field(nullable=False, foreign_key="event.id")
    
# 接受财务部成员的创建，用于报销审批和生成报销表，一段账可以没有single_record。
class SingleRecord(SQLModel, table=True):
    __tablename__ = "single_record"  # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    direction: FinanceDirection = Field(nullable=False)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    description: str = Field()
    created_by_id: uuid.UUID = Field(nullable=False)
    created_at: datetime.datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    is_deleted: bool = Field(default=False)
    
    invoice_receipt_id: uuid.UUID = Field(nullable=True, foreign_key="invoice_receipt.id")
    invoice_receipt:  Optional["InvoiceReceipt"] = Relationship(back_populates="single_record")  # type: ignore
    finance_record_id: uuid.UUID = Field(nullable=False, foreign_key="finance_record.id")
    finance_record: 'FinanceRecord' = Relationship(back_populates="single_records")  # type: ignore
        
        


class InvoiceReceipt(SQLModel, table=True):
    __tablename__ = "invoice_receipt"  # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=True))
    direction: FinanceDirection = Field(nullable=True)

    single_record: 'SingleRecord' = Relationship(back_populates="invoice_receipt")  # type: ignore