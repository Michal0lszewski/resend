import os

os.environ.setdefault("RESEND_API_KEY", "test-key")
os.environ.setdefault("MAIL_FROM", "sender@example.com")
os.environ.setdefault("MAIL_FROM_NAME", "Test Sender")

import resend  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_index_returns_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "Send Mail as" in response.text
    assert 'name="to"' in response.text


def test_send_valid_email_calls_resend(monkeypatch):
    captured = {}

    def fake_send(params):
        captured.update(params)
        return {"id": "email_123"}

    monkeypatch.setattr(resend.Emails, "send", fake_send)

    response = client.post(
        "/send",
        data={
            "to": "friend@example.com",
            "cc": "",
            "bcc": "",
            "subject": "Hello",
            "message": "Just testing.",
        },
    )

    assert response.status_code == 200
    assert captured["from"] == "Test Sender <sender@example.com>"
    assert captured["to"] == ["friend@example.com"]
    assert captured["subject"] == "Hello"
    assert captured["text"] == "Just testing."
    assert "cc" not in captured
    assert "bcc" not in captured
    assert "Email sent to friend@example.com." in response.text


def test_send_with_cc_and_bcc(monkeypatch):
    captured = {}

    def fake_send(params):
        captured.update(params)
        return {"id": "email_456"}

    monkeypatch.setattr(resend.Emails, "send", fake_send)

    response = client.post(
        "/send",
        data={
            "to": "a@example.com, b@example.com",
            "cc": "c@example.com",
            "bcc": "d@example.com",
            "subject": "Hi",
            "message": "Body",
        },
    )

    assert response.status_code == 200
    assert captured["to"] == ["a@example.com", "b@example.com"]
    assert captured["cc"] == ["c@example.com"]
    assert captured["bcc"] == ["d@example.com"]


def test_send_missing_required_field_does_not_call_resend(monkeypatch):
    called = False

    def fake_send(params):
        nonlocal called
        called = True
        return {"id": "email_789"}

    monkeypatch.setattr(resend.Emails, "send", fake_send)

    response = client.post(
        "/send",
        data={"to": "   ", "cc": "", "bcc": "", "subject": "Hi", "message": "Body"},
    )

    assert response.status_code == 200
    assert called is False
    assert "required" in response.text.lower()


def test_send_invalid_email_rejected(monkeypatch):
    called = False

    def fake_send(params):
        nonlocal called
        called = True
        return {"id": "email_000"}

    monkeypatch.setattr(resend.Emails, "send", fake_send)

    response = client.post(
        "/send",
        data={"to": "not-an-email", "cc": "", "bcc": "", "subject": "Hi", "message": "Body"},
    )

    assert response.status_code == 200
    assert called is False
    assert "invalid email" in response.text.lower()
