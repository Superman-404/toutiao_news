from sqlalchemy import select, delete, func

from models.favorite import Favorite
from models.news import News


async def is_news_favorite(db, user_id: int, news_id: int):
    """
    检查新闻是否已收藏
    :param user_id: 用户ID
    :param news_id: 新闻ID
    :param db: 数据库连接
    :return:
    """
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def add_news_favorite(db, user_id: int, news_id: int):
    """
    添加新闻到收藏
    :param user_id: 用户ID
    :param news_id: 新闻ID
    :param db: 数据库连接
    :return:
    """
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    # await db.commit()
    await db.flush()
    await db.refresh(favorite)
    return favorite


async def remove_news_favorite(db, user_id: int, news_id: int):
    """
    取消收藏
    :param user_id: 用户ID
    :param news_id: 新闻ID
    :param db: 数据库连接
    :return:
    """
    # query = select(Favorite).where(Favorite.user_id==user_id, Favorite.news_id==news_id)
    # result = await db.execute(query)
    # favorite = result.scalar_one_or_none()
    # if favorite:
    #     await db.delete(favorite)
    #     return True
    # return False

    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.rowcount > 0


async def get_favorite_list(
        db,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    """
    获取用户收藏的新闻
    :param user_id: 用户ID
    :param db: 数据库连接
    :return:
    """
    # 先查询总量
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    offset = (page - 1) * page_size

    # 连表分页查询新闻的收藏列表
    # 查询结果
    # [
    #  (News, favorite_time, favorite_id),
    # ]
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
             .order_by(Favorite.created_at.desc())
             .offset(offset)
             .limit(page_size)
             )
    #   result 不是 ORM 对象，而是一个 查询结果集对象（类似于数据库游标），它包含了执行 SQL 查询后返回的所有数据。
    result = await db.execute(query)
    rows = result.all()
    return rows, total
