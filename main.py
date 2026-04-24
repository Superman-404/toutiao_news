from fastapi import FastAPI
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handler import register_exception_handler

app = FastAPI()
# 注册全局异常处理器
register_exception_handler(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
