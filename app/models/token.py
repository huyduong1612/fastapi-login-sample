from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI()

# Define the request model


class Token(BaseModel):
    access_token: Optional[str] = None
    email: Optional[str] = None
    expired_time: Optional[datetime] = None
    userid: Optional[int] = None
    app_code: Optional[str] = None


class TokenValidate(BaseModel):
    access_token: str
