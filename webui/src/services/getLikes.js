import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	AccessDeniedException,
	BadAuthException,
	InternalServerError,
	PostNotFoundException
} from "./apiErrors";

export default async function getLikes(postID) {
	await ensureAuthenticated();
	const resp = await api.get(`/users/me/posts/${postID}/likes`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 200:
			return resp.data;
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
