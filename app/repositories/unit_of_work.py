from abc import ABC, abstractmethod
import psycopg2
from ..repositories.user_repository import IUsers, UsersRepository

host = "localhost"
user = "postgres"
password = "postgres"
database = "px-login"


class IUnitOfWork(ABC):
    @abstractmethod
    def execute(self, query, params=None):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @property
    @abstractmethod
    def users(self) -> IUsers:
        pass


class Psycopg2UnitOfWork(IUnitOfWork):
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self._users = UsersRepository(connection)

    def execute(self, query, params=None):
        self.cursor.execute(query, params)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    @property
    def users(self) -> IUsers:
        return self._users


class UnitOfWorkFactory:
    @staticmethod
    def create_unit_of_work():
        connection = psycopg2.connect(
            database=database, user=user, password=password, host=host)
        return Psycopg2UnitOfWork(connection)


""" # Example usage
unit_of_work = UnitOfWorkFactory.create_unit_of_work()

# Use the unit_of_work instance to execute queries and perform transactions

# Commit the changes
unit_of_work.commit()

# Close the database cursor and connection
unit_of_work.cursor.close()
unit_of_work.connection.close()
 """
