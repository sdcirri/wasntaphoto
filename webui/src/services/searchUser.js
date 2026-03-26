import api from "./axios";

import { InternalServerError } from "./apiErrors";

export default async function searchUser(query) {
	const trimmed = query?.trim() ?? "";
	if (trimmed.length < 3)
		return [];

	const resp = await api.get("/users/", {
		params: { q: trimmed, limit: 10 }
	});

	if (resp.status === 200)
		return resp.data;
	throw InternalServerError;
}
