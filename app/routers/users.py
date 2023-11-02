from fastapi import APIRouter, Depends, HTTPException, status
from ..models.login import LoginRequest
from ..models.token import Token, TokenValidate
from ..repositories.unit_of_work import IUnitOfWork
from ..dependencies import get_uow
from ..redis_client import RedisClient
from fastapi.responses import Response
import jwt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import pandas as pd

router = APIRouter()


async def no_dependency():
    pass


@router.post("/users/login", tags=["users"], dependencies=[Depends(no_dependency)])
async def login(request: LoginRequest, uow: IUnitOfWork = Depends(get_uow)):
    email = request.Email
    password = request.Password
    app_code = request.AppCode

    # Check if email and password are not empty
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="email or password is incorrect"
        )

    df = uow.users.login(request)
    if 'msg_code' in df.columns:
        return {
            "message": df.loc[0, 'message'],
            "msg_code": df.loc[0, 'msg_code']
        }

    uow.users.removeToken(email, app_code)

    expire_date = datetime.now()+relativedelta(months=1)

    payload = {"email": email, "app_code": app_code, "create_date": datetime.now(
    ).strftime('%Y-%m-%d %H:%M:%S'), "expired": expire_date.strftime('%Y-%m-%d %H:%M:%S')}

    secret_key = 'ERMN05OPLoDvbTTa/QkqLNMI7cPLguaRyHzyg7n5qNBVjQmtBhz4SzYh4NBVCXi3KJHlSXKP+oi2+bXr6CUYTR=='

    access_token = jwt.encode(payload, secret_key, algorithm="HS256")

    token = Token(
        access_token=access_token,
        email=email,
        expired_time=expire_date,
        userid=df.loc[0, 'id'],
        app_code=app_code
    )
    created_token = uow.users.createToken(token)
    redisClient = RedisClient()
    redisClient.remove_record_by_email(email, app_code)

    redisClient.redis.set(access_token, redisClient.serialize_object(token))

    return {
        "message": 'login successfully',
        "msg_code": 200,
        "content": {
            "access_token": access_token,
            "email": email,
            "expired_time": expire_date
        }
    }


@router.post("/token/validate", tags=["token"], dependencies=[Depends(no_dependency)])
async def validate(request: TokenValidate, uow: IUnitOfWork = Depends(get_uow)):
    redisClient = RedisClient()
    serialized_token = redisClient.redis.get(request.access_token)
    if (serialized_token):
        token = redisClient.deserialize_object(serialized_token)
        return {
            "msg_code": 200,
            "content": token
        }

    stored_token = uow.users.getToken(request.access_token)
    if (stored_token is None or stored_token.empty):
        ret = json.dumps({
            "msg_code": 404,
            "message": "the access token is invalid"
        })
        return Response(content=ret, status_code=403, media_type='application/json')

    expiredtime_str = stored_token.loc[0, 'expiredtime']
    expiredtime = pd.to_datetime(expiredtime_str, format='%Y-%m-%d %H:%M:%S')

    if (expiredtime < datetime.now()):
        return Response(
            content=json.dumps(
                {
                    "msg_code": 404,
                    "message": "the access token is expired"
                }
            ), status_code=403, media_type='application/json'
        )
    else:
        token = Token()
        token.access_token = stored_token.loc[0, 'access_token']
        token.app_code = stored_token.loc[0, 'app_code']
        token.email = stored_token.loc[0, 'email']
        token.expired_time = expiredtime
        token.userid = int(stored_token.loc[0, 'userid'])

        redisClient = RedisClient()

        redisClient.redis.set(token.access_token,
                              redisClient.serialize_object(token))

        return {
            "msg_code": 200,
            "message": "validated",
            "content":  token.dict()
        }
