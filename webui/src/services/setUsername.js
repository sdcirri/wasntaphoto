import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	InternalServerError,
	UsernameAlreadyTakenException
} from "./apiErrors";

export default async function setUsername(username) {
	await ensureAuthenticated();
	const resp = await api.put("/users/me/username",
		JSON.stringify(username),
		{ headers: authHeaders({ "Content-Type": "application/json" }) }
	);
	switch (resp.status) {
		case 204:
			return;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 409:
			throw UsernameAlreadyTakenException;
		default:
			throw InternalServerError;
	}
}
