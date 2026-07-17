# SYManage

社团管理系统。后端 Python / FastAPI,前端 React + TypeScript + Vite。
访问由**白名单**控制:只有邮箱预先加入白名单的人才能注册,身份和权限记录在白名单条目上(而不是登录账号上)。

## 当前功能

系统规划涵盖财务、活动、人员、固定资产四大模块,**目前只实现了登录系统和人员/白名单系统**,其余尚未开始。

### 登录与鉴权
- 白名单限制注册:邮箱不在白名单里无法注册
- 邮箱密码登录,签发 JWT token(Argon2 加密密码)
- 前端用 Context 管理登录态,路由守卫保护需要登录的页面,刷新后自动恢复登录
- 启动时按环境变量自动创建 superadmin 账号

### 人员 / 白名单
- 添加白名单:单条表单 + 批量 JSON 导入(限 superadmin / president)
- 批量导入时拒绝录入 superadmin / president / treasurer 等高权限
- 白名单列表页:卡片形式展示成员
- 5 种权限角色:vice_president、cocktail_minister、tea_minister、bar_manager、tea_manager

## 技术栈

| | |
|---|---|
| 后端 | FastAPI · SQLModel · PostgreSQL · Alembic · PyJWT · pwdlib(Argon2) |
| 前端 | React 19 · TypeScript · Vite · React Router |

## 快速开始

### 后端(`backend/`)
需要 Conda 环境 `SYManage`(不要用 `SYFIN`),以及一份 `backend/.env`
(必填:`APP_NAME`、`SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`、
`DATABASE_URL`、`SUPERADMIN_EMAIL`、`SUPERADMIN_PASSWORD`)。

```bash
conda activate SYManage
cd backend
pip install -e ".[dev]"     # 安装依赖
alembic upgrade head        # 建表 / 迁移
fastapi dev app/main.py     # 启动开发服务器
```

### 前端(`frontend/`)
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

## 目录结构

```
backend/app/
  users/        # 登录 + 白名单:model / schema / service / router / security
  core/         # 配置(Settings 从 .env 读取)
  db/           # 数据库 session
  main.py       # 入口、CORS、启动时初始化 superadmin
frontend/src/
  api/          # 请求封装(common_api)+ 白名单接口(UserManage_api)
  contexts/     # AuthContext:登录态
  components/   # RequireAuth 路由守卫、UserCard
  pages/        # 登录页、导航页、人员管理页、添加白名单模态框
```

> 更细的架构与开发约定见 [CLAUDE.md](CLAUDE.md),动态进度见 [.claude/current-phase.md](.claude/current-phase.md)。
