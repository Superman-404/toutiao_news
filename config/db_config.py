from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
import os

app = FastAPI()

# 创建数据库引擎
ASYNC_DATABASE_URI = os.getenv("ASYNC_DATABASE_URI")
# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URI,
    echo=True,  # 可选:输出sql日志
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20)  # 设置连接池允许创建的额外连接数

# # # 定义基类+模型类
# class Base(DeclarativeBase):pass
# class moxing(Base): pass
# # 建表:定义函数建表 -> FastAPI 启动的时候调用建表的函数
# async def create_tables():
#     # 获取异步数据库引擎,创建事务,建表
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
# # 启动应用时建表
# @app.on_event('startup')
# async def startup_event():
#     await create_tables()

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 依赖项,用于获取数据库会话
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
