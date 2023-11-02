from abc import ABC, abstractmethod

from app.models.token import Token
from .base_services import BaseService
from ..models.login import LoginRequest
from ..models.token import Token
import hashlib
from pandas import DataFrame


class IUsers(ABC):
    @abstractmethod
    def login(self, request: LoginRequest) -> DataFrame:
        pass

    @abstractmethod
    def createToken(self, token: Token) -> DataFrame:
        pass

    @abstractmethod
    def removeToken(self, email: str, app_code: str):
        pass

    @abstractmethod
    def getToken(self, access_token: str) -> DataFrame:
        pass


class UsersRepository(BaseService, IUsers):
    def __init__(self, connection):
        super().__init__(connection)
        pass

    def login(self, request: LoginRequest) -> DataFrame:
        password = hashlib.md5(request.Password.encode('utf-8')).hexdigest()
        params = [request.Email, password]
        result = self.callproc_dataframe('users_check_login', params)
        return result

    def createToken(self, token: Token) -> DataFrame:
        params = (token.access_token, token.email,
                  token.expired_time, token.userid, token.app_code)
        return self.callproc_dataframe('tokens_create_new', params)

    def removeToken(self, email: str, app_code: str):
        query = 'delete from tokens where email=%s and app_code=%s;'
        params = (email, app_code)
        return self.execute_query(query, params)

    def getToken(self, access_token: str) -> DataFrame:
        query = 'select * from tokens where access_token=%s'
        params = (access_token,)
        return self.execute_dataframe(query, params)
