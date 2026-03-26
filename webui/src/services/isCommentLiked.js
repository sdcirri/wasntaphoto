import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from "./apiErrors";
import { resolveCommentContext } from "./getPost";

export default async function isCommentLiked(cid) {
	await ensureAuthenticated();
	const { postId, authorId } = await resolveCommentContext(cid);
	const resp = await api.get(`/users/${authorId}/posts/${postId}/comments/${cid}/like`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 200:
			return resp.data;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw CommentNotFoundException;
		default:
			throw InternalServerError;
	}
}
