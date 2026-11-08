import os
import smtplib
from email.message import EmailMessage


class SmtpMailer:
    """Sends through the provider's SMTP relay; a send takes 2-3 seconds."""

    def send(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = "hello@tidepool.example"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(os.environ["SMTP_HOST"], 587, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            smtp.send_message(msg)
