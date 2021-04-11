from server.constants import MAIL_PASS, MAIL_USER
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
