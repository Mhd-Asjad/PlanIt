from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_token import verify_token , oauth2_scheme
from loguru import logger



def current_user(token: str = Depends(oauth2_scheme)):
    logger.info(f"verifying token: {token}")
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate" : "Bearer"}
    )
    return verify_token(token , credentials_exeption)

