# email_notifier.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_email(subject: str, body: str, to_addr: str = None):
    to_addr = to_addr or config.GMAIL_USER
    if not config.GMAIL_USER or not config.GMAIL_PASS:
        print("⚠️ Email not sent: Gmail credentials not set in .env")
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = config.GMAIL_USER
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(config.GMAIL_USER, config.GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"📧 Notification sent to {to_addr}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")
        return False
