import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import { BadAuthException, InternalServerError, PostNotFoundException } from "./apiErrors";
import { resolvePostAuthorId } from "./getPost";

export default async function isLiked(pid) {
	await ensureAuthenticated();
	const authorId = await resolvePostAuthorId(pid);
	const resp = await api.get(`/users/${authorId}/posts/${pid}/like`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 200:
			return resp.data;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw PostNotFoundException;
		default:
			throw InternalServerError;
	}
}
