import api from "./axios";
import { clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from "./apiErrors";

function propicPath(uid, meId) {
	if (uid == null || uid === "me")
		return "me";
	const parsedUid = Number(uid);
	if (Number.isInteger(parsedUid) && parsedUid === meId)
		return "me";
	return uid;
}

export default async function getProfilePicture(uid) {
	const meId = await ensureAuthenticated();
	const resp = await api.get(`/users/${propicPath(uid, meId)}/propic`, {
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
