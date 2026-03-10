import asyncio

from db.repositories import CommentRepository, CommentLikeRepository
from db.entities import CommentModel, CommentLikeRelationship

from exceptions import AccessDeniedError, CommentNotFoundError
from model import Comment


class CommentService:
    comment_repo: CommentRepository
    like_repo: CommentLikeRepository

    def __init__(self, comment_repo: CommentRepository, like_repo: CommentLikeRepository) -> None:
        self.comment_repo = comment_repo
        self.like_repo = like_repo

    async def get_comment(self, comment_id: int) -> Comment:
        """
        Get a comment by its comment ID
        :param comment_id: comment ID
        :return: the comment, if it exists
        """
        if not (db_comment := self.comment_repo.find_by_id(comment_id)):
            raise CommentNotFoundError
        return Comment.model_validate(db_comment)

    async def create_comment(self, user_id: int, post_id: int, content: str) -> Comment:
        """
        Create a new comment
        :param user_id: user ID
        :param post_id: post ID
        :param content: comment content
        :return: the newly created comment
        """
        db_comment = CommentModel(user_id=user_id, post_id=post_id, content=content)
        await self.comment_repo.save(db_comment)
        return Comment.model_validate(db_comment)

    async def like_comment(self, user_id: int, comment_id: int) -> None:
        """
        Like a comment
        :param user_id: user ID
        :param comment_id: comment ID
        """
        if not await self.comment_repo.find_by_id(comment_id):
            raise CommentNotFoundError
        await self.like_repo.save(CommentLikeRelationship(user_id=user_id, comment_id=comment_id))

    async def unlike_comment(self, user_id: int, comment_id: int) -> None:
        """
        unlike a comment
        :param user_id: user ID
        :param comment_id: comment ID
        """
        await self.like_repo.delete(CommentLikeRelationship(user_id=user_id, comment_id=comment_id))
        if not await self.comment_repo.find_by_id(comment_id):
            raise CommentNotFoundError

    async def delete_comment(self, user_id: int, comment_id: int) -> None:
        """
        Delete a comment
        :param user_id: user ID
        :param comment_id: comment ID
        """
        if not (db_comment := await self.comment_repo.find_by_id(comment_id)):
            raise CommentNotFoundError
        if user_id != db_comment.author_id:
            raise AccessDeniedError
        await self.like_repo.delete(CommentLikeRelationship(user_id=user_id, comment_id=comment_id))
