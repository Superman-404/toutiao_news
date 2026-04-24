from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }

    """
    jsonable_encoder 会将 ORM 对象转换为普通字典
    JSONResponse 再将整个字典转为 JSON 字符串返回给前端
    这样就能确保无论 content 中包含什么类型的复杂对象,都能正确地转换为 JSON 格式返回。
    """
    return JSONResponse(content=jsonable_encoder(content))
