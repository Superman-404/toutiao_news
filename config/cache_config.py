import json
from typing import Any

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),  # "redis"服务器地址
    port=int(os.getenv("REDIS_PORT", 6379)),  # "redis"端口号
    db=int(os.getenv("REDIS_DB", 0)),  # "redis"数据库编号, 0~15
    decode_responses=True  # 是否将字节数据解码为字符串
)


# 设置 和 读取 (字符串 和 列表或字典) "[{}]"
# 读取 字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None


# 读取; 列表/字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取json缓存失败: {e}")
        return None


# 设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
