import { ref } from "vue";

import api from "./axios";
import {
	BadAuthException,
	FailedLoginException,
	InternalServerError
} from "./apiErrors";

let cachedUserId = null;
let syncPromise = null;

export const loggedInUserId = ref(null);

function setUserId(userId) {
	cachedUserId = userId;
	loggedInUserId.value = userId;
}

export function getCachedUserId() {
	return cachedUserId;
}

export function clearAuth() {
	if (cachedUserId != null)
		api.delete("/session/current");
	setUserId(null);
}

export async function currentUserId(force = false) {
	if (!force && cachedUserId != null)
		return cachedUserId;
	if (syncPromise != null)
		return syncPromise;

	syncPromise = (async function () {
		const resp = await api.get("/users/me");
		switch (resp.status) {
			case 200:
				setUserId(resp.data.user_id);
				return cachedUserId;
			case 401:
				clearAuth();
				return null;
			default:
				throw InternalServerError;
		}
	})();

	try {
		return await syncPromise;
	} finally {
		syncPromise = null;
	}
}

export async function ensureAuthenticated() {
	const userId = await currentUserId();
	if (userId == null)
		throw BadAuthException;
	return userId;
}

export default async function login(username, password) {
	const resp = await api.post(
		"/session/",
		{ username, password },
		{ headers: { "Content-Type": "application/json" } }
	);

	switch (resp.status) {
		case 200:
			setUserId(null);
			return await currentUserId(true);
		case 403:
		case 422:
			throw FailedLoginException;
		default:
			throw InternalServerError;
	}
}

currentUserId().catch(() => {});
