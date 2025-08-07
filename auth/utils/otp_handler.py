import random
import time
import ssl
import smtplib
from email.message import EmailMessage
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

stored_otp: dict = {}

GMAIL_SENDER = os.getenv("GMAIL_SENDER")      
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def generate_otp():
    return str(random.randint( 100000 ,999999))

def sent_otp_email(recipient_email: str , otp: str):
    subject = "Your OTP Code"
    body = f"Your One-Time Password (OTP) is: {otp}\n\nThis OTP will expire in 5 minutes."
    
    message = EmailMessage()
    message["from"] = GMAIL_SENDER
    message["to"] = recipient_email
    message["subject"] = subject
    message.set_content(body)
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.send_message(message)
            logger.info(f"OTP sent to {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise

def set_otp(email: str , ttl: int = 300):
    otp = generate_otp()
    expiry_time =  time.time() + ttl
    stored_otp[otp] = {
        "otp" : otp,
        "email": email,
        "expiry_time": expiry_time,
    }
    
    sent_otp_email(email , otp)
    return stored_otp[otp]

def get_otp(otp: str):
    entry = stored_otp.get(otp) 
    if entry and time.time() < entry['expiry_time']:
        return entry
    return None