import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path
from pathlib import Path

from app.internal.constants import MAIL_PASS, MAIL_USER

EMAIL_TEMPLATE = Path(
    path.dirname(path.realpath(__file__)), "email_template.txt"
).read_text()


def send_email(
    email, subject, content, plaintext="If you see this, there has been an error"
):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = MAIL_USER
    message["To"] = email
    message.attach(MIMEText(plaintext, "plain"))
    message.attach(MIMEText(content, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(MAIL_USER, MAIL_PASS)
        return server.sendmail(MAIL_USER, email, message.as_string())


def send_confirmation_email(email: str, url: str):
    return send_email(
        email,
        "Confirm Email",
        EMAIL_TEMPLATE.replace(r"{url}", url)
        .replace(r"{message}", "Click the button below to verify your email")
        .replace(r"{action}", "Verify Email"),
        f"Confirm your email here {url}",
    )


def send_password_reset_email(email: str, url: str):
    return send_email(
        email,
        "Reset password",
        EMAIL_TEMPLATE.replace(r"{url}", url)
        .replace(
            r"{message}",
            "Our records indicate that you have requested a password reset. You can do so by clicking the button below",
        )
        .replace(r"{action}", "Reset Password"),
        f"Reset your password here: {url}",
    )