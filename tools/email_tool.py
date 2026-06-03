# tools/email_tool.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_email_notification(booking_details: str) -> str:
    try:
        sender    = os.getenv("EMAIL_ADDRESS")
        password  = os.getenv("EMAIL_PASSWORD")
        recipient = os.getenv("ADMIN_EMAIL")

        if not all([sender, password, recipient]):
            return (
                "Email credentials missing. "
                "Check your .env file."
            )

        msg            = MIMEMultipart()
        msg["From"]    = sender
        msg["To"]      = recipient
        msg["Subject"] = "New Booking - Paw Connect AI"

        body = f"""
Hello Admin,

A new booking has been received via
Paw Connect AI Receptionist:

----------------------------------------
{booking_details}
----------------------------------------

Please confirm the appointment with
the customer at your earliest convenience.

Thank you,
Paw Connect AI System
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465
        ) as server:
            server.login(sender, password)
            server.sendmail(
                sender,
                recipient,
                msg.as_string()
            )

        return (
            "Email notification sent to "
            "admin successfully!"
        )

    except smtplib.SMTPAuthenticationError:
        return (
            "Email authentication failed. "
            "Check your Gmail App Password in .env"
        )

    except Exception as e:
        return (
            f"Email failed. "
            f"Error Type: {type(e).__name__} "
            f"Error: {str(e)}"
        )