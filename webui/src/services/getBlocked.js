import api from "./axios";

import { clearAuth, ensureAuthenticated } from "./login";
import { AccessDeniedException, BadAuthException, InternalServerError } from "./apiErrors";

export default async function getBlocked() {
	await ensureAuthenticated();
	const resp = await api.get("/users/me/blocked");
	switch (resp.status) {
		case 200:
			return resp.data;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw AccessDeniedException;
		default:
			throw InternalServerError;
	}
}
