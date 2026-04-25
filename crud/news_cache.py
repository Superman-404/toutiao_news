from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache import news_cache
from cache.news_cache import CATEGORIES_CACHE_KEY
from models.news import Category, News


async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先查询redis
    categories_cache = await news_cache.get_json_cache(CATEGORIES_CACHE_KEY)
    if categories_cache:
        print("✅ [缓存命中] 从 Redis 获取分类数据")
        return categories_cache

    # 查询数据库
    print("❌ [缓存未命中] 从数据库查询分类数据")
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories_cache = result.scalars().all()

    # 写入缓存
    if categories_cache:
        categories_cache=jsonable_encoder(categories_cache)
        await news_cache.set_categories_cache(categories_cache)

    return categories_cache


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0,
                        limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(
        skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果,否则报错


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()  # 提交事务

    # 判断更新是否命中数据库,命中则返回Ture
    # return db.execute(stmt) > 0  # db.execute(stmt)返回的是对象不能比较大小
    return result.rowcount > 0


async def get_related_news(db: AsyncSession, news_id: int, category_id: int,
                           limit: int = 5):
    stmt = select(News).where(News.id != news_id,
                              News.category_id == category_id).order_by(
        News.views.desc(),
        News.publish_time.desc()).limit(
        limit)
    result = await db.execute(stmt)
    # return result.scalars().all()

    related_news = result.scalars().all()
    return [
        {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views
        } for news_detail in related_news]
