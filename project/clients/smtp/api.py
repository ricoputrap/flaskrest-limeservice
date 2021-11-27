import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

from project.clients.abstract import AbstractClient

EMAIL_SENDER_NAME = os.environ.get('EMAIL_SENDER_NAME')
EMAIL_BCC = os.environ.get('EMAIL_BCC')
SMTP_ADDRESS = os.getenv('EMAIL_SMTP_ADDRESS')
SMTP_USERNAME = os.environ.get('EMAIL_SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('EMAIL_SMTP_PASSWORD')
EMAIL_BODY_FORMAT = "html"
EMAIL_BODY_CHARSET = "utf-8"


def client_factory():
    smtp_ssl = smtplib.SMTP_SSL(SMTP_ADDRESS)
    smtp_ssl.login(SMTP_USERNAME, SMTP_PASSWORD)
    return smtp_ssl


def _construct_mime_object(recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER_NAME
    msg['Bcc'] = EMAIL_BCC
    msg['Subject'] = subject
    msg['To'] = recipient
    body = MIMEText(body, EMAIL_BODY_FORMAT, EMAIL_BODY_CHARSET)
    msg.attach(body)
    return msg


class SmtpClient(AbstractClient):
    client = client_factory()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls_name = self.__class__.__name__
        self.logger = logging.getLogger(cls_name)

    def send_message(self, recipient, subject, body, dry_run=False):
        mime_object = _construct_mime_object(recipient, subject, body)
        if not dry_run:
            self.get_client().send_message(mime_object)
        else:
            logging.info(mime_object.values())
