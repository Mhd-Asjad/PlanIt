import random
import time

stored_otp: dict = {}

def generate_otp():
    return str(random.randint( 100000,999999))

def set_otp(email: str , ttl: int = 300):
    otp = generate_otp()
    expiry_time =  time.time() + ttl
    # send_otp_tomail()
    stored_otp[otp] = {
        "otp" : otp,
        "email": email,
        "expiry_time": expiry_time,
    }
    return stored_otp[otp]

def get_otp(otp: str):
    entry = stored_otp.get(otp) 
    if entry and time.time() < entry['expiry_time']:
        return entry
    return None