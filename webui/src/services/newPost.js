import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BadUploadException,
	InternalServerError
} from "./apiErrors";
import { cachePostPayload, normalizePost } from "./getPost";

export default async function newPost(image, caption) {
	await ensureAuthenticated();
	const resp = await api.post("/users/me/posts/", {
		image,
		caption
	}, {
		headers: authHeaders({ "Content-Type": "application/json" })
	});
	switch (resp.status) {
		case 200:
			cachePostPayload(resp.data);
			return normalizePost(resp.data);
		case 400:
		case 422:
			throw BadUploadException;
		case 401:
			clearAuth();
			throw BadAuthException;
		default:
			throw InternalServerError;
	}
}
