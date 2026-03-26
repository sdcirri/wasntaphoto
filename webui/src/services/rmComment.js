import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	AccessDeniedException,
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from "./apiErrors";
import { resolveCommentContext } from "./getPost";

export default async function rmComment(cid) {
	await ensureAuthenticated();
	const { postId, authorId } = await resolveCommentContext(cid);
	const resp = await api.delete(`/users/${authorId}/posts/${postId}/comments/${cid}`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 204:
			return;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw AccessDeniedException;
		case 404:
			throw CommentNotFoundException;
		default:
			throw InternalServerError;
	}
}
