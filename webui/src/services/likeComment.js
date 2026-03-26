import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from "./apiErrors";
import { resolveCommentContext } from "./getPost";

export default async function likeComment(cid) {
	await ensureAuthenticated();
	const { postId, authorId } = await resolveCommentContext(cid);
	const resp = await api.put(`/users/${authorId}/posts/${postId}/comments/${cid}/like`, null, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 204:
			return;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw CommentNotFoundException;
		default:
			throw InternalServerError;
	}
}
