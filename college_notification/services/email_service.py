import os
import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_notification_email(to_email, subject, body):
    smtp_user = os.environ.get('GMAIL_USER')
    smtp_pass = os.environ.get('GMAIL_PASS')
    if not smtp_user or not smtp_pass:
        return False
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except Exception:
        return False
