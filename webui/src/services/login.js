import { reactive } from "vue";

import api from "./axios";
import {
	BadAuthException,
	FailedLoginException,
	InternalServerError
} from "./apiErrors";

const SESSION_COOKIE = "WASASESSIONID";
const USER_COOKIE = "WASAUSERID";

function readCookie(name) {
	const cookies = decodeURIComponent(document.cookie).split(";");
	for (let i = 0; i < cookies.length; i++) {
		let cookie = cookies[i];
		while (cookie.charAt(0) === " ")
			cookie = cookie.substring(1);
		if (cookie.indexOf(`${name}=`) === 0)
			return cookie.substring(name.length + 1);
	}
	return null;
}

function writeCookie(name, value) {
	document.cookie = `${name}=${value}; path=/; SameSite=Strict;`;
}

function clearCookie(name) {
	document.cookie = `${name}=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT`;
}

function parseUserId(raw) {
	const parsed = Number(raw);
	return Number.isInteger(parsed) && parsed >= 0 ? parsed : null;
}

let syncCurrentUserPromise = null;

export const authStatus = reactive({
	status: readCookie(SESSION_COOKIE),
	userId: parseUserId(readCookie(USER_COOKIE))
});

export function authHeaders(extraHeaders = {}) {
	if (authStatus.status == null)
		return extraHeaders;
	return {
		Authorization: `Bearer ${authStatus.status}`,
		...extraHeaders
	};
}

export function clearAuth() {
	clearCookie(SESSION_COOKIE);
	clearCookie(USER_COOKIE);
	authStatus.status = null;
	authStatus.userId = null;
}

export async function syncCurrentUserId(force = false) {
	if (authStatus.status == null) {
		authStatus.userId = null;
		clearCookie(USER_COOKIE);
		return null;
	}
	if (!force && authStatus.userId != null)
		return authStatus.userId;
	if (syncCurrentUserPromise != null)
		return syncCurrentUserPromise;

	// The backend session token is opaque, so the UI keeps the numeric user id
	// separately after resolving `/users/me`.
	syncCurrentUserPromise = (async function () {
		const resp = await api.get("/users/me", {
			headers: authHeaders()
		});
		switch (resp.status) {
			case 200:
				authStatus.userId = resp.data.user_id;
				writeCookie(USER_COOKIE, resp.data.user_id);
				return authStatus.userId;
			case 401:
				clearAuth();
				throw BadAuthException;
			default:
				throw InternalServerError;
		}
	})();

	try {
		return await syncCurrentUserPromise;
	} finally {
		syncCurrentUserPromise = null;
	}
}

export async function ensureAuthenticated() {
	if (authStatus.status == null)
		throw BadAuthException;
	const userId = await syncCurrentUserId();
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
			authStatus.status = resp.data;
			authStatus.userId = null;
			writeCookie(SESSION_COOKIE, resp.data);
			clearCookie(USER_COOKIE);
			return await syncCurrentUserId(true);
		case 403:
		case 422:
			throw FailedLoginException;
		default:
			throw InternalServerError;
	}
}

if (authStatus.status != null && authStatus.userId == null)
	syncCurrentUserId().catch(() => clearAuth());
