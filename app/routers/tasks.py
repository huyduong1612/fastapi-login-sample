from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


fake_task_db = [
    {
        "id": 1,
        "name": "Rh incompat reaction NEC"
    },
    {
        "id": 2,
        "name": "Acc poison-freon"
    },
    {
        "id": 3,
        "name": "Chorioretinal scar NOS"
    },
    {
        "id": 4,
        "name": "Cl skull fx NEC-concuss"
    },
]


@router.get("/")
async def read_tasks():
    return fake_task_db
