from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str


class UserInfoOptional(BaseModel):
    """
    用户信息可选数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoOptional):
    id: int
    username: str

    # 模型设置
    model_config = ConfigDict(
        from_attributes=True,  # 可以提取ORM对象属性值
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    # 模型设置
    model_config = ConfigDict(
        from_attributes=True,  # 可以提取ORM对象属性值
        populate_by_name=True  # 允许使用alias别名对应前后端字段
    )


# 更新用户信息
class UpdateUserInfo(BaseModel):
    """
    更新用户信息数据模型
    """
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None


class UserChangePasswordRequest(BaseModel):
    """
    用户修改密码数据模型
    """
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")
