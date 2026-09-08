# Resend Mailer

A small local web UI for sending one-off emails as a sender address you control via [Resend](https://resend.com), with a Bootstrap form for To/CC/BCC, Subject, and Message.

Runs locally only — no authentication, intended for use on your own machine.

## Setup

Requires [`uv`](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in your Resend API key and sender address (a real `.env` with the working key already exists in this project and is git-ignored):

```
RESEND_API_KEY=re_your_api_key_here
MAIL_FROM=you@yourdomain.com
MAIL_FROM_NAME=Your Name
```

`MAIL_FROM` must be an address on a domain verified for sending in your Resend account.

## Run

```bash
./run.sh
```

(equivalent to `uv run uvicorn app.main:app --reload --port 8000`)

Open http://localhost:8000, fill in the form, and send.

Stop it with:

```bash
./stop.sh
```

## Test & lint

```bash
uv run pytest
uv run ruff check .
```

Tests monkeypatch `resend.Emails.send`, so running them never sends real email.

## Project layout

See [ARCHITECTURE.md](ARCHITECTURE.md).
