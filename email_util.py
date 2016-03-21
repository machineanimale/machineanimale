import smtplib

from app_secret import GMAIL_ADDR, GMAIL_PW

GMAIL_SMTP = 'smtp.gmail.com'
GMAIL_PORT = 587


def client():
    smtp_client = smtblib.SMTP(GMAIL_SMTP, GMAIL_PORT)
    smtp_client.starttls()
    smtp_client.login(GMAIL_ADDR, GMAIL_PW)

    return smtp_client

