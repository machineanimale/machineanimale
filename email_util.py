import smtplib

from app_secret import GMAIL_ADDR, GMAIL_PW

GMAIL_SMTP = 'smtp.gmail.com'
GMAIL_PORT = 587


def client():

    """
    Creates and returns an SMTP client for the Gmail account provided
    in app_secret.py.

    Returns:
        smtplib.SMTP: the client to use for sending mail
    """

    smtp_client = smtplib.SMTP(GMAIL_SMTP, GMAIL_PORT)
    smtp_client.starttls()
    smtp_client.login(GMAIL_ADDR, GMAIL_PW)

    return smtp_client


def send(to_addr, body):

    """
    Sends the paylaod to the Game player addressed by `to_addr`.

    Args:
        to_addr (str): the number to which the body should be sent
        body (str): the list of animals to send to the player
    """

    mail_client = client()
    mail_client.sendmail(GMAIL_ADDR, to_addr, body)
    mail_client.quit()

