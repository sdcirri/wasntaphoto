import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadFollowOperation,
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from "./apiErrors";

export default async function unfollow(toUnfollow) {
	await ensureAuthenticated();
	const resp = await api.delete(`/users/me/following/${toUnfollow}`, {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 204:
			return;
		case 400:
			throw BadFollowOperation;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw BlockedException;
		case 404:
			throw UserNotFoundException;
		default:
			throw InternalServerError;
	}
}
