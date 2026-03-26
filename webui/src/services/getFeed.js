import api from "./axios";

import { authHeaders, authStatus, clearAuth, ensureAuthenticated } from "./login";
import { BadAuthException, InternalServerError } from "./apiErrors";
import { cacheAuthorPosts } from "./getPost";

export default async function getFeed() {
	await ensureAuthenticated();

	const feedResp = await api.get("/feed/", {
		headers: authHeaders()
	});

	switch (feedResp.status) {
		case 200:
			break;
		case 401:
			clearAuth();
			throw BadAuthException;
		default:
			throw InternalServerError;
	}

	// Seed post -> author lookups for feed cards by enumerating followed users'
	// post id lists. The backend feed itself only returns bare post ids.
	const followingResp = await api.get("/users/me/following", {
		headers: authHeaders()
	});

	switch (followingResp.status) {
		case 200:
			break;
		case 401:
			clearAuth();
			throw BadAuthException;
		default:
			throw InternalServerError;
	}

	const authorIds = [authStatus.userId, ...followingResp.data.filter(id => id !== authStatus.userId)];
	const postsResponses = await Promise.all(
		authorIds.map(authorId =>
			api.get(`/users/${authorId}/posts/`, {
				headers: authHeaders()
			})
		)
	);

	for (let i = 0; i < postsResponses.length; i++) {
		const resp = postsResponses[i];
		switch (resp.status) {
			case 200:
				cacheAuthorPosts(authorIds[i], resp.data);
				break;
			case 401:
				clearAuth();
				throw BadAuthException;
			case 403:
			case 404:
				break;
			default:
				throw InternalServerError;
		}
	}

	return feedResp.data;
}
