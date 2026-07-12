# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Current progress & next steps live in [.claude/current-phase.md](.claude/current-phase.md).**
> Read it at the start of each session to see what's done and what's next, and update it as work progresses.
> This CLAUDE.md holds the stable architecture & conventions; `current-phase.md` holds the moving progress log.

## Overview

SYManage is a club management system with a Python/FastAPI backend and a React/TypeScript frontend. Access is gated by a **whitelist**: users can only register if their email was pre-added to the whitelist, and the whitelist entry (not the user row) carries the person's role and profile data.

## Roadmap & Current Scope

Long-term the system is planned to cover four business modules. **None of these should be built until explicitly requested** — see Working Style.

- **财务管理 (Finance)** — 记账 (bookkeeping), 报账 (reimbursement).
- **活动管理 (Activities)** — 活动创建, 策划案/预算案记录, 照片收集, 发票 OCR, 报销表生成, 一键拉群.
- **人员系统 (Personnel)** — 白名单, 权限, 工时记录 (work-hour logging), 社员记录 (member records).
- **固定资产管理 (Assets)** — 物资明细, 借出/收回, 存放记录.

"opt" (optional / nice-to-have) features are explicitly out of scope for now.

**Current phase:** only the foundational **login system** and the **personnel / whitelist system**. Do not start Finance, Activities, or Assets modules yet.


## Commands

### Backend (`backend/`)
The backend uses `pyproject.toml` (PEP 621) with dev extras. Commands assume you are in `backend/`.

**Always use the Conda env `SYManage`, never `SYFIN`.** `SYFIN` runs Python 3.14 with an old SQLModel and fails to import the models with `Field 'id' requires a type annotation`; `SYManage` imports them fine. Activate with `conda activate SYManage` before running any backend command.

- Install: `pip install -e ".[dev]"`
- Run dev server: `fastapi dev app/main.py` (or `uvicorn app.main:app --reload`)
- Lint: `ruff check .`
- Test: `pytest` — single test: `pytest path/to/test_file.py::test_name`
- Migrations: `alembic revision --autogenerate -m "message"` then `alembic upgrade head`

Alembic reads `DATABASE_URL` from settings (see `alembic/env.py`), not from `alembic.ini`. `SQLModel.metadata` is the autogenerate target, so any new table model must be imported in `alembic/env.py` for autogenerate to detect it.

### Frontend (`frontend/`)
- Install: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build` (runs `tsc -b` then `vite build`)
- Lint: `npm run lint` (Oxlint, not ESLint)

## Configuration

The backend requires a `backend/.env` file. `Settings` (`app/core/config.py`) has no defaults for the core fields, so the app fails to start if any are missing: `APP_NAME`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`, `SUPERADMIN_EMAIL`, `SUPERADMIN_PASSWORD`. Database is PostgreSQL (via `psycopg`).

## Architecture

### Whitelist-gated auth model
The two core tables (`app/users/model.py`) are intentionally split:
- `WhiteList` — the source of truth for a person's identity and role: `email`, `username`, `permission`, `wechat_account`, `retired`, `working_year`. Entries exist *before* an account does.
- `User` — the actual login account: `email` + `hashed_password`, linked to a `WhiteList` row via `whitelist_id`.

Consequences to keep in mind:
- Registration (`create_user`) only succeeds if the email already exists in the whitelist; otherwise it raises `ValueError`.
- A user's role is read through the relationship as `user.whitelist.permission` — `User` itself has no permission field.
- On startup (`init_superadmin` in `main.py`), a superadmin whitelist entry + account are created from the `SUPERADMIN_*` env vars if absent.

### Permissions
`Permission` (`app/users/model.py`) is a string enum: `superadmin`, `president`, `vice_president`, `cocktail_minister`, `tea_minister`, `treasurer`, `manager`. Authorization is currently inline in route handlers (e.g. only `superadmin`/`president` may add to the whitelist or list it), not a reusable dependency.

### Auth flow
`app/users/security.py` handles JWT (PyJWT) and Argon2 password hashing (pwdlib). Tokens carry the user's **email** as `sub`. `get_current_user` (in `service.py`) is the FastAPI dependency that decodes the token and loads the `User`. Two login endpoints exist: `/users/login` (JSON body) and `/users/token` (OAuth2 password form, used as the `tokenUrl` for Swagger auth).

### Backend layering
Each feature lives under `app/<feature>/` split into `model.py` (SQLModel tables), `schema.py` (request/response SQLModel DTOs), `service.py` (DB logic + business rules, raises `ValueError`), `router.py` (endpoints that catch `ValueError` → `HTTPException`). `security.py` is auth-specific. DB sessions come from the `get_db` dependency in `app/db/session.py`.

### Frontend
Minimal React 19 + Vite SPA. `src/types.ts` mirrors the backend's `Permission` enum and token/user shapes — keep it in sync when backend schemas change.

## Conventions

- Service functions signal business errors by raising `ValueError`; routers translate these into `HTTPException` with `HTTP_400_BAD_REQUEST`. Follow this pattern rather than raising `HTTPException` inside services.
- Code comments in this repo are frequently in Chinese; match the surrounding language when editing a file.

## Working Style

The owner is a **beginner** learning full-stack development by building this project. When working here:

- Multiple related steps can be output together in one response (the owner asked for this); still explain each step's "why" as you go. Don't scaffold huge numbers of unrelated files at once — keep it coherent and reviewable.
- **Explain the "why"** behind each step, how the pieces fit together, and unpack FastAPI / SQLModel / Alembic concepts as they come up — don't assume prior knowledge.
- **Before editing code, state what you're going to change and where.** Get alignment first.
- **Do not implement business modules that haven't been approved.** Stay within the current phase (login + personnel/whitelist). Suggestions are welcome, but wait for a yes before building.
- Respond in Chinese (the owner's working language) when practical.
