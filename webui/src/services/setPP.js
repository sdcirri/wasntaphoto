import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	ImageTooBigException,
	InternalServerError
} from "./apiErrors";

function bytesFromBase64(base64) {
	const binary = window.atob(base64);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++)
		bytes[i] = binary.charCodeAt(i);
	return bytes;
}

export default async function setPP(imgB64) {
	await ensureAuthenticated();
	const resp = await api.put("/users/me/pp",
		bytesFromBase64(imgB64),
		{ headers: authHeaders({ "Content-Type": "application/octet-stream" }) }
	);
	switch (resp.status) {
		case 204:
			return;
		case 400:
			throw ImageTooBigException;
		case 401:
			clearAuth();
			throw BadAuthException;
		default:
			throw InternalServerError;
	}
}
