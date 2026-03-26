import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BadCommentException,
	InternalServerError,
	PostNotFoundException
} from "./apiErrors";
import { cacheCommentIds, resolvePostAuthorId } from "./getPost";

export default async function commentPost(pid, text) {
	await ensureAuthenticated();
	const authorId = await resolvePostAuthorId(pid);
	const resp = await api.post(`/users/${authorId}/posts/${pid}/comments/`,
		JSON.stringify(text),
		{ headers: authHeaders({ "Content-Type": "application/json" }) }
	);
	switch (resp.status) {
		case 200:
			cacheCommentIds(pid, [resp.data.comment_id]);
			return resp.data.comment_id;
		case 400:
		case 422:
			throw BadCommentException;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw PostNotFoundException;
		default:
			throw InternalServerError;
	}
}
