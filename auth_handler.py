from fastapi import HTTPException

from constants import STATIC_TOKEN


def authenticate(token: str):
    if token != STATIC_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
