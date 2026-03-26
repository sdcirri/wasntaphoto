import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import { BadAuthException, InternalServerError, PostNotFoundException } from "./apiErrors";
import { resolvePostAuthorId } from "./getPost";

export default async function unlikePost(pid) {
	await ensureAuthenticated();
	const authorId = await resolvePostAuthorId(pid);
	const resp = await api.delete(`/users/${authorId}/posts/${pid}/like`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 204:
			return;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 404:
			throw PostNotFoundException;
		default:
			throw InternalServerError;
	}
}
