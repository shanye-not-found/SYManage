from app.db.session import get_db
from schema import FinanceRecordCreate
from model import FinanceRecord
from sqlalchemy.orm import Session

def create_finance_record(session: Session, finance_record: FinanceRecordCreate):
    