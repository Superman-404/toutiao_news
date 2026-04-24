from fastapi import APIRouter, Depends, Query, HTTPException, status

from crud import news
from config.db_config import AsyncSession, get_db

# 创建APIRouter实例
# prefix 路由前缀 (API 接口规范)
# tags 分组 标签
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # 首先要到数据库查到数据 才能在前端显示
    # curd 创建查询方法
    # 路由端 调用curd实现
    category = await news.get_category(db, skip, limit)
    return {
        "code": 200,
        "msg": "获取新闻分类成功",
        "data": category
    }


@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    # 更多:(跳过的页数+ 当前页面总数)
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "has_more": has_more
        }
    }


@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_db)
):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
