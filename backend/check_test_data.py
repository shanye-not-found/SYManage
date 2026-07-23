"""
查看数据库中现有的测试数据
"""
from sqlmodel import Session, select
from app.db.session import engine
from app.users.model import WhiteList, User, Permission


def check_existing_data():
    """查看数据库中的测试数据"""

    with Session(engine) as session:
        # 查询所有 manager 权限的白名单记录
        managers = session.exec(
            select(WhiteList).where(
                (WhiteList.permission == Permission.tea_manager) |
                (WhiteList.permission == Permission.bar_manager)
            )
        ).all()

        if not managers:
            print("❌ 数据库中没有找到 manager 权限的记录")
            return

        print(f"📊 找到 {len(managers)} 条 manager 记录:\n")

        for wl in managers:
            # 检查是否有对应的 User 账户
            user = session.exec(
                select(User).where(User.whitelist_id == wl.id)
            ).first()

            status = "✅ 已退休" if wl.retired else "🟢 在职"
            has_account = "✅ 有账户" if user else "❌ 无账户"

            print(f"{status} | {has_account} | {wl.permission.value}")
            print(f"  姓名: {wl.username}")
            print(f"  邮箱: {wl.email}")
            print(f"  微信: {wl.wechat_account}")
            print(f"  创建时间: {wl.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if wl.retired and wl.retired_at:
                print(f"  退休时间: {wl.retired_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if wl.retired_description:
                    print(f"  退休原因: {wl.retired_description}")
            print()


if __name__ == "__main__":
    check_existing_data()
