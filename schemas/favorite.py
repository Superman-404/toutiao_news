from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FavoriteRequest(BaseModel):
    is_favorite: bool = Field(
        ..., alias="isFavorite",
        description="收藏状态"
    )


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(
        ..., alias="newsId",
        description="新闻ID"
    )


class FavoriteListBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    category_id: int = Field(alias="categoryId")
    views: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class FavoriteNewsItemResponse(FavoriteListBase):
    favorite_time: datetime = Field(alias="favoriteTime"
                                    )
    favorite_id: int = Field(alias="favoriteId"
                             )
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class FavoriteResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(
        ..., alias="hasMore")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
