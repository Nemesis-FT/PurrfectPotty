"""
Questo modulo contiene utility di autenticazione.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from data_proxy.backend.web.configuration import JWT_KEY, ADMIN_PASSWORD, ADMIN_USERNAME

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class Token(BaseModel):
    """
    Schema di risposta del token
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema contenuti token
    """
    email: Optional[str] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(password):
    """
    Funzione di hashing
    :param password: password
    :return: un hash
    """
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str) -> bool:
    """
    Data una combinazione di email e password, verifica se questa combinazione corrisponde ad un utente valido.
    :param email: la mail dell'utente
    :param password: password
    :return: a boolean or an user
    """
    if email == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    else:
        return False


def create_token(data: dict):
    """
    Crea un token JWT
    :param data: dict contenente i dati da codificare
    :return: il token JWT
    """
    encode = data.copy()
    encode.update({"exp": datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(encode, JWT_KEY, ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Partendo dal token, rintraccia l'utente a cui corrisponde
    :param token: il token JWT
    :return: l'utente
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = token_data.email
    if user is None:
        raise credentials_exception
    return user
