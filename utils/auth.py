from fastapi import Depends, status, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud import users
from config.db_config import get_db
from models.users import User


# 获取当前用户信息
async def get_current_user(
        db: AsyncSession = Depends(get_db),
        authorization: str = Header(..., alias="Authorization")) -> User:
    # token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或令牌已过期")
    return user
