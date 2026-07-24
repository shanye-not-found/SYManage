from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from app.db.session import get_db
from app.users.model import User
from app.dependencies import require_handover_capable
from app.finance.schema import BalancePublic, FinanceRecordCreate, FinanceRecordPublic
from app.finance.service import create_finance_record, get_balance, get_finance_records
from app.users.service import get_current_user

finance_router = APIRouter(prefix="/finance", tags=["Finance"])

@finance_router.get("/balance", response_model=BalancePublic)
def balance(db: Session = Depends(get_db),curr_user: User = Depends(require_handover_capable)) -> BalancePublic:
    balancepublic: BalancePublic = get_balance(db)
    return balancepublic



@finance_router.post("/finance_record", response_model=FinanceRecordPublic)
def create_f_record(
    finance_record: FinanceRecordCreate,
    db: Session = Depends(get_db),
    curr_user: User = Depends(require_handover_capable),
    ) -> FinanceRecordPublic:
    try:
        new_finance_record = create_finance_record(db, finance_record)
        return new_finance_record
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@finance_router.get("/finance_record", response_model=list[FinanceRecordPublic])
def get_f_records(db: Session = Depends(get_db),curr_user: User = Depends(get_current_user)) -> list[FinanceRecordPublic]:
    try:
        finance_records = get_finance_records(db)
        return finance_records
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))