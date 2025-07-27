from fastapi import APIRouter , Depends , HTTPException , status
from database.schemas.user import UserRegister , LoginRequest , TokenResponse , TokenData
from auth.hashing import hash_password , verify_password
from auth.jwt_token import create_access_token
from database.db_config import db , user
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from loguru import logger

router = APIRouter()

# /api/user/register
@router.post("/register")
def register_user(request: UserRegister):
    try:
        # find email already registered or not
        existing_email = user.find_one({'email': request.email})
        if existing_email :
            return HTTPException(
                status_code=400 , detail="Email already exists"
            )        
        hashed_pass = hash_password(request.password)
        user_object = dict(request)
        user_object["password"] = hashed_pass
        res = db.user.insert_one(user_object)
        return {"status": status.HTTP_201_CREATED , "detail": "usercreated successfully"}
    
    except Exception as e :
        return HTTPException(
            status_code=500 , detail=f"error occurs on register {str(e)}"
        )
        
# /api/users/login
@router.post('/login')
async def login(request: Annotated[ OAuth2PasswordRequestForm , Depends()]):
    logger.info(f"created login : {request.username} , {request.password}")
    valid_user = user.find_one({"email" : request.username})    
    if not valid_user :
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="invalid credentials")

    if not verify_password(request.password , valid_user["password"]):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="password is incorrect")
    
    access_token = create_access_token(data={"sub" : request.username})
    return {"access_token" : access_token , "token_type" : "bearer"}