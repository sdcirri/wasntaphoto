import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	AccessDeniedException,
	BadAuthException,
	InternalServerError,
	PostNotFoundException
} from "./apiErrors";

export default async function rmPost(postID) {
	await ensureAuthenticated();
	const resp = await api.delete(`/users/me/posts/${postID}`, {
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
			throw PostNotFoundException;
		default:
			throw InternalServerError;
	}
}
