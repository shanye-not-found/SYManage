"""
测试数据注入脚本
生成 WhiteList 和 User 测试数据
"""
import datetime
import random
from sqlmodel import Session, select

from app.db.session import engine
from app.users.model import WhiteList, User, Permission, utc_now
from app.users.security import hash_password


def generate_test_data():
    """生成测试数据并注入数据库"""

    # 测试用户数据配置
    test_users = [
        {
            "email": "tea_manager1@example.com",
            "username": "茶室经理张三",
            "permission": Permission.tea_manager,
            "wechat_account": "tea_mgr_001",
            "password": "Password123!",
            "retired": False,
            "retired_at": None,
        },
        {
            "email": "tea_manager2@example.com",
            "username": "茶室经理李四",
            "permission": Permission.tea_manager,
            "wechat_account": "tea_mgr_002",
            "password": "Password123!",
            "retired": True,
            "retired_at": datetime.datetime(2025, 12, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
            "retired_description": "毕业离职"
        },
        {
            "email": "bar_manager1@example.com",
            "username": "酒吧经理王五",
            "permission": Permission.bar_manager,
            "wechat_account": "bar_mgr_001",
            "password": "Password123!",
            "retired": False,
            "retired_at": None,
        },
        {
            "email": "bar_manager2@example.com",
            "username": "酒吧经理赵六",
            "permission": Permission.bar_manager,
            "wechat_account": "bar_mgr_002",
            "password": "Password123!",
            "retired": False,
            "retired_at": None,
        },
        {
            "email": "tea_manager3@example.com",
            "username": "茶室经理孙七",
            "permission": Permission.tea_manager,
            "wechat_account": "tea_mgr_003",
            "password": "Password123!",
            "retired": True,
            "retired_at": datetime.datetime(2026, 3, 20, 14, 0, 0, tzinfo=datetime.timezone.utc),
            "retired_description": "转岗其他部门"
        },
        {
            "email": "bar_manager3@example.com",
            "username": "酒吧经理周八",
            "permission": Permission.bar_manager,
            "wechat_account": "bar_mgr_003",
            "password": "Password123!",
            "retired": True,
            "retired_at": datetime.datetime(2026, 6, 1, 9, 0, 0, tzinfo=datetime.timezone.utc),
            "retired_description": "个人原因离职"
        },
    ]

    # 时间范围：2024-08-01 到现在
    start_date = datetime.datetime(2024, 8, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    now = utc_now()

    with Session(engine) as session:
        created_count = 0
        skipped_count = 0

        for user_data in test_users:
            # 检查邮箱是否已存在
            existing_whitelist = session.exec(
                select(WhiteList).where(WhiteList.email == user_data["email"])
            ).first()

            if existing_whitelist:
                print(f"⚠️  跳过: {user_data['email']} 已存在于白名单")
                skipped_count += 1
                continue

            # 生成随机的 created_at (在 2024-08-01 到现在之间)
            time_diff = (now - start_date).total_seconds()
            random_seconds = random.uniform(0, time_diff)
            created_at = start_date + datetime.timedelta(seconds=random_seconds)

            # 如果是已退休用户，确保 retired_at 在 created_at 之后且不晚于当前时间
            retired_at = user_data.get("retired_at")
            if retired_at and retired_at < created_at:
                # 如果指定的 retired_at 早于 created_at，调整为 created_at 之后
                retired_at = created_at + datetime.timedelta(days=random.randint(30, 365))
                if retired_at > now:
                    retired_at = now

            # 创建 WhiteList 记录
            whitelist = WhiteList(
                email=user_data["email"],
                username=user_data["username"],
                permission=user_data["permission"],
                wechat_account=user_data["wechat_account"],
                retired=user_data["retired"],
                created_at=created_at,
                retired_at=retired_at,
                retired_description=user_data.get("retired_description"),
                highest_permission=user_data["permission"],  # 设置为当前权限
            )

            session.add(whitelist)
            session.flush()  # 刷新以获取 whitelist.id

            # 创建 User 账户（只为未退休的用户创建，或者你也可以为所有人创建）
            # 这里我为所有人都创建账户
            hashed_pwd = hash_password(user_data["password"])
            user = User(
                email=user_data["email"],
                hashed_password=hashed_pwd,
                whitelist_id=whitelist.id,
                created_at=created_at,
                updated_at=created_at,
            )

            session.add(user)
            created_count += 1

            status = "已退休" if user_data["retired"] else "在职"
            print(f"✅ 创建: {user_data['username']} ({user_data['email']}) - {user_data['permission'].value} - {status}")
            print(f"   创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if retired_at:
                print(f"   退休时间: {retired_at.strftime('%Y-%m-%d %H:%M:%S')}")

        session.commit()
        print(f"\n📊 总结: 成功创建 {created_count} 条记录, 跳过 {skipped_count} 条")
        print(f"💡 所有账户的默认密码: Password123!")


if __name__ == "__main__":
    print("开始注入测试数据...\n")
    generate_test_data()
    print("\n✨ 完成!")
