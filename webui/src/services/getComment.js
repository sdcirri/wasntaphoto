import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from "./apiErrors";
import { resolveCommentContext } from "./getPost";

function normalizeComment(comment, postId) {
	return {
		commentID: comment.comment_id,
		postID: postId,
		author: comment.author_id,
		time: comment.pub_time,
		content: comment.content,
		likes: comment.like_cnt
	};
}

export default async function getComment(cid) {
	await ensureAuthenticated();
	const { postId, authorId } = await resolveCommentContext(cid);
	const resp = await api.get(`/users/${authorId}/posts/${postId}/comments/${cid}`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 200:
			return normalizeComment(resp.data, postId);
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw CommentNotFoundException;
		default:
			throw InternalServerError;
	}
}
