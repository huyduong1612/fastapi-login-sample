from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def update_amin():
    return {"message":"Admin getting schwifty"}