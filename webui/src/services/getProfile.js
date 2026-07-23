import api from "./axios";

import { authHeaders, authStatus, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BadIdsException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from "./apiErrors";
import { cacheAuthorPosts } from "./getPost";

function profilePath(uid) {
	if (uid == null || uid === "me")
		return "me";
	const parsedUid = Number(uid);
	if (Number.isInteger(parsedUid) && parsedUid === authStatus.userId)
		return "me";
	return uid;
}

function normalizeProfile(profile, posts) {
	cacheAuthorPosts(profile.user_id, posts);
	return {
		userID: profile.user_id,
		username: profile.username,
		followers: profile.followers_cnt,
		following: profile.following_cnt,
		posts
	};
}

export default async function getProfile(uid) {
	await ensureAuthenticated();
	const path = profilePath(uid);

	const [profileResp, postsResp] = await Promise.all([
		api.get(`/users/${path}`, { headers: authHeaders() }),
		api.get(`/users/${path}/posts/`, { headers: authHeaders() })
	]);

	switch (profileResp.status) {
		case 200:
			break;
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw BlockedException;
		case 404:
			throw UserNotFoundException;
		case 422:
			throw BadIdsException;
		default:
			throw InternalServerError;
	}

	switch (postsResp.status) {
		case 200:
			return normalizeProfile(profileResp.data, postsResp.data);
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
