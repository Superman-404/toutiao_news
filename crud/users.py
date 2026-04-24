import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UpdateUserInfo
from utils.security import get_password_hash, verify_password


# 1.查询用户输入
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 2.创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 用户密码加密
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.flush()
    # await db.commit()
    # await db.refresh(user)
    return user


# 3. Token
async def creat_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_token = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_token
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_token)
        db.add(user_token)
        # await db.commit()
    return token


# 4. 验证用户
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


# 5. 根据 token 获取用户信息
async def get_user_by_token(db: AsyncSession, token: str) -> User | None:
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token:
        return None

    # 检查 token 是否过期
    expires_at = db_token.expires_at
    if expires_at < datetime.now():
        return None

    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 更新用户信息
async def update_user_info(db: AsyncSession, username: str, user_data: UpdateUserInfo):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)
    # await db.commit()

    # 检查是否命中数据库
    if result.rowcount == 0:
        raise ValueError("用户不存在")
    updated_user = await get_user_by_username(db, username)
    return updated_user


async def update_user_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not verify_password(old_password, user.password):
        return False
    # 新密码加密
    hashed_new_password = get_password_hash(new_password)
    # 更新密码
    user.password = hashed_new_password
    # 使用ORM对象方式 执行数据库sql语句，需要user对象 select * from user;
    db.add(user)
    # 灵码推荐让get_db提交commit()
    # await db.commit()
    # await db.refresh(user)
    return True
