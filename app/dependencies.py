from typing import Annotated

from fastapi import Header, HTTPException

from .repositories.unit_of_work import UnitOfWorkFactory


async def get_token_header(x_token: Annotated[str, Header(default='')]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "specific":
        raise HTTPException(
            status_code=400, detail="No specific token provided")


def get_uow():
    uow = UnitOfWorkFactory.create_unit_of_work()
    try:
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise
