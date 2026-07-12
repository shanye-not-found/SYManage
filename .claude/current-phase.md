# 当前进度与下一步 (Current Phase)

> 这份文件记录**动态进度**——做到哪了、下一步做什么。长期架构和约定看 [CLAUDE.md](../CLAUDE.md)。
> 每完成一个阶段就更新这里。最后更新:2026-07-12。

## 当前阶段

只做**基础登录系统**和**人员/白名单系统**。财务、活动、固定资产模块未经批准不要动。

## 后端进度 (backend/)

已完成:
- 白名单限制注册:`POST /users/register`
- JSON 登录:`POST /users/login`
- Swagger OAuth2 登录:`POST /users/token`
- JWT token 创建与解码、`get_current_user` 登录依赖
- 获取当前用户:`GET /users/me`
- 添加白名单:`POST /users/add_whitelist`(限 superadmin/president)
- 获取白名单列表:`GET /users/whitelist`(限 superadmin/president)
- 启动时自动初始化 superadmin
- **已加 CORS 中间件**(`app/main.py`),允许 `localhost:5173` / `127.0.0.1:5173`
- Ruff / OpenAPI 检查曾通过
- Alembic 当前 head 曾为 `de43d891bb82`

技术债 / 待重构(不急,基础闭环跑通后再回来):
- `app/main.py` 用的是已废弃的 `@app.on_event("startup")`,应换成 `lifespan` 写法。

## 前端进度 (frontend/)

目标:最小登录闭环 —— 输入邮箱密码 → `POST /users/login` → 存 `access_token` →
带 `Authorization: Bearer <token>` 请求 `GET /users/me` → 展示当前用户 → 支持退出。

已完成:
- `src/types.ts`:`Permission` / `Token` / `CurrentUser`,`id` 已修正为 `string`(对应后端 UUID)
- `src/api.ts`:`login`、`getCurrentUser`、`logout`
- `src/App.tsx`:登录表单 + 已登录界面 + `useEffect` 恢复登录 + 错误提示

待确认 / 已知问题:
- `App.tsx` 里 `handleLogin` 的事件类型写成了 `React.SubmitEvent`(不存在),应改为
  `React.FormEvent<HTMLFormElement>`,否则 TS 编译报错。
- 整条链路尚未端到端验证(前后端一起启动、用 superadmin 账号实测登录)。

## 下一步

1. 修 `App.tsx` 事件类型:`React.SubmitEvent` → `React.FormEvent<HTMLFormElement>`。
2. 端到端验证登录闭环:
   - 后端 `conda activate SYManage` → `backend/` 下 `fastapi dev app/main.py`
   - 前端 `frontend/` 下 `npm run dev`,打开 `http://localhost:5173`
   - 用 `.env` 里的 `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD` 登录
   - F12 Network 确认 `/users/login`、`/users/me` 均 200、无 CORS 红字
   - 测退出、刷新后自动恢复登录
3. 闭环跑通后,候选方向(需 owner 确认再做):
   - 人员系统前端页面:白名单列表展示 / 添加白名单表单
   - 后端把 inline 权限检查抽成可复用的依赖
   - 收技术债:`on_event` → `lifespan`
