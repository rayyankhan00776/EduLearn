import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_otp_email(to_email: str, otp: str):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Debug print to ensure environment variables are loaded
    print(f"SMTP_USER: {smtp_user}, SMTP_PASSWORD: {smtp_password}, SMTP_SERVER: {smtp_server}, SMTP_PORT: {smtp_port}")

    if not smtp_user or not smtp_password:
        print('SMTP_USER or SMTP_PASSWORD is not set!')
        return False

    subject = 'Your EduLearn Password Reset OTP'
    body = f'Your OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes.'

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f'Failed to send email: {e}')
        return False
