import os
import sys
import time

import smtplib, ssl
import imghdr

from bs4 import BeautifulSoup as bs
from email.utils import formatdate, formataddr
from email.message import EmailMessage
from email.header import Header

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from email.mime.base import MIMEBase
from email.utils import make_msgid
from email import encoders

from app import app


class SendMail:
    def __init__(self, subject):
        self.subject = subject
        # mail setup
        self.mail           = MIMEMultipart()
        self.host           = app.config["EMAIL_HOST"]
        self.EMAIL_PASSWORD = app.config["EMAIL_PASS"]
        self.REPLY_TO       = app.config["EMAIL_NOREPLY_USER"]
        self.port           = 2525 if self.host == 'smtp.mailtrap.io' else 465

    def set_sender(self, sender):
        self.EMAIL_ADDRESS = sender
    
    def set_sender_id(self, sender_id):
        self.SENDER_NAME = sender_id

    def set_receiver(self, receiver):
        self.receiving = receiver   

    def set_content(self, filename, placeholders):
        UFile = open(filename, 'r')
        htmlContent = ''

        with UFile as file_content:
            htmlContent = file_content.read()

        for placeholder in placeholders:
            htmlContent = f"""\
                {htmlContent}
                """.replace(placeholder['key'], placeholder['value'])
        plainContent = bs(htmlContent, "html.parser").text

        self.htmlContent = MIMEText(htmlContent, 'html')
        self.plainContent = MIMEText(plainContent, 'plain')
        self.mail.attach(self.htmlContent)
        self.mail.attach(self.plainContent)

    def send(self):
        self.mail['Subject']    = self.subject
        self.mail['From']       = formataddr((str(Header(self.SENDER_NAME, 'utf-8')), self.EMAIL_ADDRESS))
        self.mail['To']         = self.receiving
        self.mail['Reply-to']   = self.REPLY_TO
        self.mail["Date"]       = formatdate(localtime=True)
        self.mail["Message-id"] = make_msgid()

        # with smtplib.SMTP_SSL(self.host, self.port) as smtp: ---------> Use this for SSL
        # with smtplib.SMTP(self.host, self.port) as smtp: ---------> Use this for non-SSL
        with app.config["EMAIL_SMTP_SECURITY"](self.host, self.port) as smtp:
            # context=ssl.create_default_context()
            try:
                smtp.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                smtp.ehlo()
                # smtp.starttls(context=context)
                smtp.sendmail(self.EMAIL_ADDRESS, self.receiving, self.mail.as_string())
                return {'status':True}
            except Exception as err:
                return {'status':False, 'err':err}
