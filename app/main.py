import os
import re
from pathlib import Path

import resend
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", MAIL_FROM)

resend.api_key = RESEND_API_KEY

app = FastAPI(title="Resend Mailer")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _split_addresses(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _invalid_addresses(addresses: list[str]) -> list[str]:
    return [addr for addr in addresses if not EMAIL_RE.match(addr)]


def _render(request: Request, **context):
    return templates.TemplateResponse(request, "index.html", {"mail_from": MAIL_FROM, **context})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return _render(request)


@app.post("/send", response_class=HTMLResponse)
async def send(
    request: Request,
    to: str = Form(...),
    cc: str = Form(""),
    bcc: str = Form(""),
    subject: str = Form(...),
    message: str = Form(...),
):
    form_values = {"to": to, "cc": cc, "bcc": bcc, "subject": subject, "message": message}

    to_list = _split_addresses(to)
    cc_list = _split_addresses(cc)
    bcc_list = _split_addresses(bcc)

    if not to_list or not subject.strip() or not message.strip():
        return _render(
            request,
            error="To, Subject, and Message are required.",
            form=form_values,
        )

    invalid = _invalid_addresses(to_list + cc_list + bcc_list)
    if invalid:
        return _render(
            request,
            error=f"Invalid email address(es): {', '.join(invalid)}",
            form=form_values,
        )

    params: resend.Emails.SendParams = {
        "from": f"{MAIL_FROM_NAME} <{MAIL_FROM}>",
        "to": to_list,
        "subject": subject,
        "text": message,
    }
    if cc_list:
        params["cc"] = cc_list
    if bcc_list:
        params["bcc"] = bcc_list

    try:
        resend.Emails.send(params)
    except Exception as exc:
        return _render(
            request,
            error=f"Failed to send email: {exc}",
            form=form_values,
        )

    return _render(request, success=f"Email sent to {', '.join(to_list)}.")
