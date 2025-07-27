from datetime import datetime, timedelta , timezone
from jose import jwt , JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from loguru import logger
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALOGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict , expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    logger.info(f"Creating access token with expiration time: {expire}")
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGORITHM)
    return encoded_jwt

def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms=[ALOGORITHM])
        username: str = payload.get("sub")
        if username is None :
            raise credential_exception
        return payload
    except:
        return JWTError