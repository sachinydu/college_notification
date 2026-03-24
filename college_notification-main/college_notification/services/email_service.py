import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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


def send_otp_email(to_email, otp, validity_minutes=5):
    """
    Send OTP via email using Gmail SMTP
    
    Args:
        to_email: Recipient email address
        otp: 6-digit OTP code
        validity_minutes: OTP validity in minutes (default: 5)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Try to use environment variables first, fallback to app config
    smtp_user = os.environ.get('GMAIL_USER')
    smtp_pass = os.environ.get('GMAIL_PASS')
    
    # If environment variables not set, provide helpful message
    if not smtp_user or not smtp_pass:
        print("[WARN] Gmail credentials not configured in environment variables")
        print("[INFO] Set GMAIL_USER and GMAIL_PASS environment variables to enable email")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'ERP Password Reset OTP'
        msg['From'] = smtp_user
        msg['To'] = to_email
        
        # HTML email body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }}
                    .header h1 {{ color: #2563eb; margin: 0; font-size: 24px; }}
                    .content {{ color: #333; line-height: 1.6; }}
                    .otp-box {{ background-color: #f0f4ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; text-align: center; letter-spacing: 3px; font-family: monospace; }}
                    .warning {{ background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin-top: 20px; border-radius: 4px; color: #92400e; font-size: 13px; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1><i>🔐 Password Reset Request</i></h1>
                    </div>
                    
                    <div class="content">
                        <p>Hello,</p>
                        <p>We received a request to reset the password for your college ERP account.</p>
                        
                        <p><strong>Your One-Time Password (OTP) is:</strong></p>
                        
                        <div class="otp-box">
                            <div class="otp-code">{otp}</div>
                        </div>
                        
                        <p><strong>⏰ Validity:</strong> This OTP is valid for only <strong>{validity_minutes} minutes</strong></p>
                        
                        <p><strong>📌 Important:</strong></p>
                        <ul>
                            <li>Do not share this OTP with anyone</li>
                            <li>This is a one-time use code</li>
                            <li>If you did not request a password reset, please ignore this email</li>
                        </ul>
                        
                        <div class="warning">
                            <strong>⚠️ Security Warning:</strong> Never share your OTP with anyone, including college staff. The college will never ask for your OTP via email or phone.
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>If you have questions, contact IT Support at support@college.edu</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text body as fallback
        text_body = f"""
Password Reset OTP
==================

Your One-Time Password (OTP) is: {otp}

Validity: This OTP is valid for only {validity_minutes} minutes

IMPORTANT:
- Do not share this OTP with anyone
- This is a one-time use code
- If you did not request a password reset, please ignore this email

SECURITY WARNING:
Never share your OTP with anyone, including college staff. The college will never ask for your OTP via email or phone.

---
This is an automated message. Please do not reply to this email.
If you have questions, contact IT Support at support@college.edu
        """
        
        # Attach both HTML and text versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email using Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Use TLS
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        
        print(f"[OK] OTP email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"[ERROR] Gmail authentication failed. Check GMAIL_USER and GMAIL_PASS")
        return False
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email: {e}")
        import traceback
        traceback.print_exc()
        return False

