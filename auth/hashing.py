from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(passwrod: str) -> str:
    return pwd_cxt.hash(passwrod)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_cxt.verify(plain_password, hashed_password)