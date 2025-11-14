# ChatKit Embed Host

This project hosts embeddable ChatKit apps. Admins configure apps with FastAPI-Admin, and end users drop in a single `<script>` to use the widget on approved domains.

## Features

- FastAPI backend with SQLAlchemy models for `ChatApp`.
- FastAPI-Admin UI to create/edit chat apps, including custom parsing for ChatKit options.
- Encryption helpers to safely store OpenAI API keys.
- Domain locked endpoints for serving cleaned ChatKit configuration and minting client secrets via the OpenAI ChatKit Sessions API.
- Static `embed.js` loader that bootstraps the ChatKit widget on the client.

## Getting Started

### 1. Configure Environment

Create a `.env` file derived from `.env.example` and fill in:

- `APP_ENCRYPTION_KEY` (generate via `python - <<<'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`).
- Optional overrides for admin credentials, allowed hosts, etc.

> **Note:** The FastAPI-Admin stack currently relies on Python 3.10 due to upstream `aioredis` constraints. The Docker image already pins 3.10; if you run locally, use a 3.10 interpreter.

### 2. Run with Docker (recommended for POC)

`docker-compose.yml` spins up the FastAPI app with SQLite (file stored in a named volume) plus the required Redis instance FastAPI-Admin uses for sessions:

```bash
docker compose up --build
```

That’s it—no external database needed. The API is exposed on [http://localhost:8000](http://localhost:8000) and FastAPI-Admin lives at `/admin`.

### 3. Local Poetry Workflow (optional)

If you prefer a local virtual environment:

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

Update `.env` so `DATABASE_URL`/`TORTOISE_DATABASE_URL` point to a path accessible on your machine (e.g. `sqlite+aiosqlite:///./chatkit.db`).

### 4. Create Chat Apps

Log into `/admin` with the configured credentials and create Chat Apps. Each saved app will expose a script snippet:

   ```html
   <script src="https://yourhost/static/embed.js" data-app-id="app_12345" async></script>
   ```

## Project Structure

- `app/config.py` – Settings management via `pydantic-settings`.
- `app/database.py` – SQLAlchemy engine + session utilities.
- `app/models.py` – `ChatApp` ORM model definition.
- `app/security.py` – Encryption helpers for OpenAI keys.
- `app/parsing.py` – ChatKit option extraction/validation logic (JSON5 powered).
- `app/admin.py` – FastAPI-Admin registration with custom form hooks.
- `app/routes` – API routers for embed config and ChatKit sessions.
- `app/static/embed.js` – Client loader that fetches config and obtains secrets.
- `app/main.py` – FastAPI app factory wiring everything together.

## Tests

Basic tests can be run with `pytest`. Install dev deps (`poetry install`) and execute `python -m pytest`.

## Demo Mode

For a zero-setup test, visit `/demo` (locally or on your Render deployment). It loads `static/embed.js` with `data-app-id="app_demo"`, which hits the API’s built-in demo ChatApp. You can use that to confirm the widget renders before touching the admin UI. The same `app_demo` ID works if you paste the script snippet into any HTML page pointing to your deployment.
