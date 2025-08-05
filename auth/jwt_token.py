from datetime import datetime, timedelta , timezone
from jose import jwt , JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.schemas.user import TokenData
from database.db_config import user
from dotenv import load_dotenv
import os
from pydantic import EmailStr
from loguru import logger

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALOGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
REFRESH_TOKEN_EXPIRE_DAY = 7

def create_access_token(data: dict , expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    logger.info(f"Creating access token with expiration time: {expire}")
    to_encode = data.copy()
    to_encode.update({
            "exp": int(expire.timestamp()),
            "type" : "access"
            
        })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
    to_encode = data.copy()
    to_encode.update({
            "exp": int(expire.timestamp()),
            "type": "refresh" 
        })
    encoded_jwt = jwt.encode(to_encode , SECRET_KEY, algorithm=ALOGORITHM)
    return encoded_jwt

def get_user(email: EmailStr):
    user_data = user.find_one({"email": email})
    if user_data:
        return {
            "id" : user_data.get('id'),
            "full_name": user_data.get('full_name'),
            "email": user_data.get('email')
        }
    return None


def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token , SECRET_KEY, algorithms=[ALOGORITHM])
        email: str = payload.get("sub")
        if email is None :
            raise credential_exception
        token_data = TokenData(email=email)
        user = get_user(token_data.email)
        if not user:
            raise credential_exception
        return user
    except JWTError:
        return credential_exception
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise credential_exception from e
    
