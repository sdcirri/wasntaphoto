from db.entities.post import PostModel
from model import Post

from image_utils import get_post_bytes


class PostService:
    @staticmethod
    async def post_to_object(post: PostModel) -> Post:
        return Post(
            post_id=post.post_id,
            author_id=post.author_id,
            pub_time=post.pub_time,
            image=await get_post_bytes(post.post_id),
            caption=post.caption,
            like_cnt=post.like_cnt,
            comments=post.comments
        )
