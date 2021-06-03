import requests
from .constants import BACKEND_WEBHOOK_URL


def send_webhook(url, json):
    # no need now
    return None
    # return requests.post(url, json={**json, "allowed_mentions": {"parse": []}})


def get_webhook_json(title, description, color):
    return {"embeds": [{"title": title, "description": description, "color": color}]}


def send_email_verify_webhook(user):
    send_webhook(
        BACKEND_WEBHOOK_URL,
        get_webhook_json(
            "Email Verification", f"{user} has verified their email", 0x0000FF
        ),
    )


def send_password_reset_webhook(user):
    send_webhook(
        BACKEND_WEBHOOK_URL,
        get_webhook_json("Password reset", f"{user} reset their password", 0x0000FF),
    )


def send_admin_action_webhook(text):
    send_webhook(
        BACKEND_WEBHOOK_URL, get_webhook_json("Admin Action", "\n".join(text), 0xFF0000)
    )


def send_acount_creation_webhook(user, name, event):
    send_webhook(
        BACKEND_WEBHOOK_URL,
        {
            "embeds": [
                {
                    "title": "User Registration",
                    "description": f"`{user}` (`{name}`) just registered for the {event} event",
                    "color": 0x00FF00,
                }
            ]
        },
    )
