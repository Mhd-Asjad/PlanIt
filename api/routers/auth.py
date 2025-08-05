from fastapi import APIRouter , Depends , HTTPException , status , Request
from fastapi.responses import JSONResponse
from database.schemas.user import UserRegister , LoginRequest , TokenResponse , TokenData
from auth.hashing import hash_password , verify_password
from auth.jwt_token import create_access_token
from database.db_config import db , user
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated 
from pydantic import EmailStr
from loguru import logger
from .deps import current_user  
from  auth.utils.otp_handler import get_otp , set_otp
from auth.utils.counter import get_next_sequence
from jose import JWTError , jwt
from auth.jwt_token import SECRET_KEY , ALOGORITHM , ACCESS_TOKEN_EXPIRE_MINUTES, get_user, create_access_token, create_refresh_token
from datetime import timedelta
router = APIRouter()

# /api/user/register
@router.post("/register")
def register_user(request: UserRegister):
    logger.info(f"Registering user: {request.full_name}, {request.email} {request.password}")
    try:
        # find email already registered or not
        existing_email = user.find_one({'email': request.email})
        if existing_email :
            return HTTPException(
                status_code=400 , detail="Email already exists"
            )
        hashed_pass = hash_password(request.password)
        # create user object
        user_id = get_next_sequence("user_id")
        user_data = {
            "id" : user_id,
            "full_name": request.full_name,
            "email": request.email,
            "password": hashed_pass
        }
        logger.info(f"User registered: {user_data}")
        user.insert_one(user_data)
        return {"status": status.HTTP_200_OK, "detail": "OTP Sent to your email"}
    except Exception as e :
        return HTTPException(
            status_code=500 , detail=f"error occurs on register {str(e)}"
        )
        
@router.post("/refresh")
async def refresh_token(
    request: Request
  ):
    try:
        refresh_token = request.cookies.get("refresh_token")
        logger.info(f"refresh token from coockie : {refresh_token}")
        if not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Refresh Token is missing"
            )
            
        payload = jwt.decode(refresh_token ,SECRET_KEY , algorithms=[ALOGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=403,
                detail="invalid Token Type"
            )
        email = payload.get("sub")
        if not email :
            raise HTTPException(status_code=403, detail="Invalid token")
        
        user = get_user(email)
        if not user :
            raise HTTPException(status_code=404, detail="User not found")
        
        new_access_token = create_access_token({"sub":email})
        return {"status":201, "access_token": new_access_token, "token_type":"Bearer"}
    except JWTError as e:
        raise HTTPException(
            status_code=403,
            detail=f"jwt refresh token error : {str(e)}"
        )

@router.post('/sent-otp')
def send_otp(email: EmailStr):
    current_user = user.find_one({"email": email})
    if not current_user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )
        
    user_data = set_otp(email)
    logger.info(f"otp was sent : {user_data}")
    return {"message": "OTP sent to email" ,"status":201 }
    
@router.post("/otp-login")
def login_with_otp(otp: str):
    stored_otp = get_otp(otp)

    logger.info(f"stored_otp with data : {stored_otp}")
    if not stored_otp or stored_otp["otp"] != otp:
        raise HTTPException(400, "Invalid or expired OTP")
    email = stored_otp["email"]
    user = get_user(email)
    if not user:
        raise HTTPException(404, "User not found")

    access_token = create_access_token({"sub": email})
    refresh_token = create_refresh_token({"sub": email})

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "Bearer"
    })
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return response

# /api/users/login
@router.post('/login')
async def login(request: Annotated[ OAuth2PasswordRequestForm , Depends()]):
    logger.info(f"created login : {request.username} , {request.password}")
    valid_user = user.find_one({"email" : request.username})
    if not valid_user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    if not verify_password(request.password , valid_user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="password is incorrect")
    
    access_token_expires = timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={
        "sub" : request.username},
        expires_delta=access_token_expires
    )
    
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "Bearer"
    })
    refresh_token = create_refresh_token(data={"sub": request.username})
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7*24*60*60
    )
    logger.info(f"this is refresh for access token ")
    return response

@router.get('/me')
def get_loggedin_user(current_user: Annotated[LoginRequest, Depends(current_user)]):
    
    logger.info(f"current user: {current_user}")
    return current_user