import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from database import get_db

NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # We keep tokenUrl for swagger UI, but we won't use it directly

class User(BaseModel):
    name: str | None = None
    email: str | None = None
    image: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the NextAuth JWT
        payload = jwt.decode(token, NEXTAUTH_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = get_db()
    user_doc = await db["users"].find_one({"email": email})
    
    if user_doc is None:
        raise credentials_exception
        
    return User(**user_doc)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_optional_current_user(token: str = Depends(oauth2_scheme_optional)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, NEXTAUTH_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            return None
    except JWTError:
        return None
        
    db = get_db()
    user_doc = await db["users"].find_one({"email": email})
    if user_doc is None:
        return None
        
    return User(**user_doc)
