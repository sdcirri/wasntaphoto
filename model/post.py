from pydantic import BaseModel, Field, Base64Bytes, ConfigDict
from datetime import datetime
from typing import Optional


class Comment(BaseModel):
    """
    A comment on a post
    """
    model_config = ConfigDict(from_attributes=True)

    comment_id: int = Field(..., ge=0)
    author_id: int = Field(..., ge=0)
    pub_time: datetime
    content: str = Field(..., max_length=2048)
    like_cnt: int = Field(..., ge=0)


class Post(BaseModel):
    """
    A user post
    """
    post_id: int = Field(..., ge=0)
    author_id: int = Field(..., ge=0)
    pub_time: datetime
    image: Base64Bytes
    caption: Optional[str] = Field(None, max_length=2048)
    like_cnt: int = Field(..., ge=0)
    comments: list[int]


class PostRequest(BaseModel):
    """
    A user request to create a new post
    """
    caption: Optional[str] = Field(None, max_length=2048)
    image: Base64Bytes
