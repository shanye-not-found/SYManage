import datetime
from decimal import Decimal

from sqlmodel import SQLModel
from app.finance.model import FinanceDirection
import uuid

class FinanceRecordCreate(SQLModel):
    direction: FinanceDirection 
    amount: Decimal 
    description: str 
    created_by_username: str
    
class FinanceRecordPublic(SQLModel):
    direction: FinanceDirection 
    amount: Decimal 
    created_by_username: str
    is_deleted: bool 
    description: str 
    created_at: datetime.datetime
    current_treasurer_name: str 
    
class BalancePublic(SQLModel):
    balance: Decimal 
    current_treasurer_name: str | None
    last_updated_at: datetime.datetime