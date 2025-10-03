import os
from jose import JWTError, jwt
from fastapi import WebSocket, HTTPException, status

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("SECRET_KEY_ALGORITHM")

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
