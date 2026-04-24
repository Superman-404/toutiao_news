from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import favorite
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response
from schemas.favorite import FavoriteRequest, FavoriteAddRequest, FavoriteResponse

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    is_favorite = await favorite.is_news_favorite(db, user.id, news_id)
    return success_response(message="获取收藏状态成功", data=FavoriteRequest(isFavorite=is_favorite))


@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    favorite_news = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="收藏成功", data=favorite_news)


@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    取消收藏
    :param news_id: 新闻ID
    :param user: 当前用户
    :param db: 数据库连接
    :return:
    """
    result = await favorite.remove_news_favorite(db, user.id, news_id)
    if result:
        return success_response(message="取消收藏成功")
    else:
        return success_response(message="取消收藏失败")


@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """

    :param page:
    :param page_size:
    :param user:
    :param db:
    :return:
    """
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    # rows是一个ORM对象不能直接返回给前端，需要转换成字典
    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id
        } for news, favorite_time, favorite_id in rows
    ]
    has_more = total > page * page_size
    data = FavoriteResponse(list=favorite_list, total=total, has_more=has_more)
    return success_response(message="获取收藏列表成功", data=data)

@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    清空收藏
    :param user:
    :param db:
    :return:
    """
    rowcount =await favorite.clear_user_favorite(db, user.id)
    return success_response(message=f"清空{rowcount}条收藏记录")