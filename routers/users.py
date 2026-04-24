from fastapi import APIRouter, Depends, HTTPException, status

from crud import users
from models.users import User
from schemas.users import UserRequest, UserInfoResponse, UserAuthResponse, UpdateUserInfo, UserChangePasswordRequest
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register", response_model=UserAuthResponse)
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 1.查询用户输入名字是否存在
    exist_user = await users.get_user_by_username(db, user_data.username)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)
    token = await users.creat_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登陆逻辑: 验证用户是否存在 -> 验证密码是否正确 -> 生成token -> 返回token和用户信息
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.creat_token(db, user.id)
    return success_response(message="登录成功",
                            data=UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user)))


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    # 获取用户信息
    # 思路:验证令牌 -> 获取用户信息
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(user_data: UpdateUserInfo, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    # 更新用户信息
    # 思路:验证令牌 -> 获取用户信息 -> 更新用户信息 -> 返回用户信息
    updated_user_info = await users.update_user_info(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(updated_user_info))


@router.put("/password")
async def update_user_password(password_data: UserChangePasswordRequest, user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    # 更新用户密码
    # 思路:验证令牌 -> 获取用户信息 -> 验证旧密码是否正确 -> 更新用户密码 -> 返回用户信息
    # 1.验证旧密码是否正确 CRUD层写了
    updated_user_pwd = await users.update_user_password(db, user, password_data.old_password,
                                                        password_data.new_password)
    if not updated_user_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
    return success_response(message="密码修改成功")
