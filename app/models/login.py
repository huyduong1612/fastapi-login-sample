from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define the request model


class LoginRequest(BaseModel):
    Email: str
    Password: str
    AppCode: str

# Define the response model


class LoginResponse(BaseModel):
    message: str
