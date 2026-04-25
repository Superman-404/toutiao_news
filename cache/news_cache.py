from typing import Dict, Any

from config.cache_config import get_json_cache, set_cache

# 获取新闻分类缓存
# redis存储格式是：key:value
CATEGORIES_CACHE_KEY = "news:categories"


async def get_categories_cache():
    # 获取缓存
    categories_cache = await get_json_cache(CATEGORIES_CACHE_KEY)
    return categories_cache


# 写入新闻分类缓存
# 分类、配置 7200;列表:600; 详情: 1800; 验证码: 120 -- 数据越稳定,缓存越持久
async def set_categories_cache(data: list[Dict[str, Any]], expire: int = 7200):
    # 写入缓存
    return await set_cache(CATEGORIES_CACHE_KEY, data, expire)
