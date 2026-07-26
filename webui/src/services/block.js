import api from "./axios";

import { clearAuth, ensureAuthenticated } from "./login";
import {
	BadFollowOperation,
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from "./apiErrors";

export default async function block(toBlock) {
	await ensureAuthenticated();
	const resp = await api.post(`/users/me/blocked/${toBlock}`);
	switch (resp.status) {
		case 200:
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
