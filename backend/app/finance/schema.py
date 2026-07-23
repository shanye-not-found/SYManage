from decimal import Decimal

from sqlmodel import SQLModel
from model import FinanceDirection

class FinanceRecordCreate(SQLModel):
    direction: FinanceDirection 
    amount: Decimal 
    description: str 
    created_by_id: str
    
    