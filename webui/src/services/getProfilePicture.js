import api from "./axios";
import { authHeaders, authStatus, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from "./apiErrors";

function propicPath(uid) {
	if (uid == null || uid === "me")
		return "me";
	const parsedUid = Number(uid);
	if (Number.isInteger(parsedUid) && parsedUid === authStatus.userId)
		return "me";
	return uid;
}

export default async function getProfilePicture(uid) {
	await ensureAuthenticated();
	const resp = await api.get(`/users/${propicPath(uid)}/propic`, {
		headers: authHeaders(),
		responseType: "blob"
	});

	switch (resp.status) {
		case 200:
			if (resp.data.size === 0)
				return null;
			return URL.createObjectURL(resp.data);
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw BlockedException;
		case 404:
			return UserNotFoundException;
		default:
			throw InternalServerError;
	}
}
