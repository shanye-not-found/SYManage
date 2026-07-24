from decimal import Decimal

from sqlmodel import col, Session, select, func
from app.finance.schema import BalancePublic, FinanceRecordCreate, FinanceRecordPublic
from app.finance.model import FinanceDirection, FinanceRecord, utc_now
from app.users.model import WhiteList, Permission
from app.users.service import get_whitelist_by_username



def get_current_treasurer(session: Session) -> WhiteList | None:
    statement = select(WhiteList).where(col(WhiteList.permission) == Permission.treasurer)
    return session.exec(statement).first()
    
    
    
def create_finance_record(session: Session, finance_record: FinanceRecordCreate) -> FinanceRecordPublic:
    if finance_record.created_by_username is None:
        raise ValueError("created_by_id cannot be None")
    whitelist_create= get_whitelist_by_username(session, finance_record.created_by_username)
    if whitelist_create is None:
        raise ValueError("created_by_username not found")
    whitelist = get_current_treasurer(session)
    if whitelist is None:
        raise ValueError("current_treasurer not found")
    new_record = FinanceRecord(
        direction=finance_record.direction,
        amount=finance_record.amount,
        description=finance_record.description,
        created_by_username=finance_record.created_by_username,
        current_treasurer_name=whitelist.username,  
    )
    session.add(new_record)  
    session.commit()   # 提交事务
    session.refresh(new_record)   # 刷新对象，使其包含数据库中的最新数据
    
    public = FinanceRecordPublic(
        direction=new_record.direction,
        amount=new_record.amount,
        created_by_username=whitelist_create.username,
        is_deleted=new_record.is_deleted,
        description=new_record.description,
        created_at=new_record.created_at,
        current_treasurer_name=whitelist.username,  
    )
    return public

def get_balance(session: Session) -> BalancePublic:
    # 分别求收入总和、支出总和
    income = session.exec(
        select(func.coalesce(func.sum(FinanceRecord.amount), 0))
        .where(FinanceRecord.direction == FinanceDirection.income)
        .where(col(FinanceRecord.is_deleted) == False)
    ).one()

    expense = session.exec(
        select(func.coalesce(func.sum(FinanceRecord.amount), 0))
        .where(FinanceRecord.direction == FinanceDirection.expense)
        .where(col(FinanceRecord.is_deleted) == False) 
    ).one()

    balance = Decimal(income) - Decimal(expense)

    whitelist = get_current_treasurer(session)
    if whitelist is None:
        name ='None'
    else:
        name = whitelist.username

    # 最晚更新时间：未删除记录里最新一条的 created_at（表里没有 updated_at 字段）
    last_updated_at = session.exec(
        select(func.max(FinanceRecord.created_at))
        .where(col(FinanceRecord.is_deleted) == False)
    ).one()
    if last_updated_at is None:
        last_updated_at = utc_now()

    return BalancePublic(
        balance=balance,
        current_treasurer_name=name,
        last_updated_at=last_updated_at,
    )


def get_finance_records(session: Session) -> list[FinanceRecordPublic]:
    # 取出所有财务记录，按创建时间倒序（最新的排在最前）
    records = session.exec(
        select(FinanceRecord).order_by(col(FinanceRecord.created_at).desc())
    ).all()

    result: list[FinanceRecordPublic] = []
    for record in records:
        result.append(
            FinanceRecordPublic(
                direction=record.direction,
                amount=record.amount,
                created_by_username=record.created_by_username,
                is_deleted=record.is_deleted,
                description=record.description,
                created_at=record.created_at,
                current_treasurer_name=record.current_treasurer_name,
            )
        )
    return result
