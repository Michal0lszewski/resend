# Architecture

## Overview

Single-process FastAPI app, server-rendered (Jinja2 + Bootstrap 5 via CDN, no client-side JS framework). One page, one form, one POST endpoint that calls the Resend API.

```
Browser (Bootstrap form)
   │  GET /            → render empty form
   │  POST /send       → validate, call Resend, re-render form with result
   ▼
FastAPI app (app/main.py)
   │
   ▼
resend Python SDK (resend.Emails.send)
   │
   ▼
Resend API (api.resend.com) → delivers mail from MAIL_FROM
```

## Files

- `app/main.py` — FastAPI app. Two routes:
  - `GET /` — renders `index.html` with an empty form.
  - `POST /send` — reads `to`/`cc`/`bcc` (comma-separated) `subject`/`message` form fields, validates required fields and email format, builds the Resend `SendParams` dict (`from` is fixed to `MAIL_FROM`/`MAIL_FROM_NAME` from the environment — never user-supplied), calls `resend.Emails.send`, and re-renders the same template with a success or error alert. There is no redirect-after-POST; the result is rendered directly in the POST response.
- `app/templates/index.html` — the entire UI: a Bootstrap 5 card with the form and an alert placeholder. Field values are re-populated from `form` context on validation/send errors so nothing is lost.
- `tests/test_main.py` — FastAPI `TestClient` tests. `resend.Emails.send` is monkeypatched in every test that would otherwise send mail, so the suite never hits the real Resend API.
- `.env` — `RESEND_API_KEY`, `MAIL_FROM`, `MAIL_FROM_NAME`. Loaded via `python-dotenv` at import time in `app/main.py`. Git-ignored.
- `run.sh` / `stop.sh` — start/stop the local uvicorn server.

## Design decisions

- **No auth, no database, no queue.** This is a single-user local tool; the sender address is fixed by the environment, so the only thing a form submission can do is send mail from an address you already control.
- **Server-rendered, not an SPA.** The form has one meaningful state transition (submit → result), which a plain POST-and-re-render handles without any client-side JS.
- **`from` is never user input.** The form only lets the caller choose recipients/subject/body; the sender identity comes solely from `MAIL_FROM`/`MAIL_FROM_NAME` env vars, so the app cannot be used to spoof arbitrary sender addresses even if someone else reaches it on your machine.
- **uv-managed environment.** Dependencies, dev tools (`pytest`, `ruff`, `httpx`), and the virtualenv are all managed via `uv`/`pyproject.toml`; all commands run through `uv run` for reproducibility.
