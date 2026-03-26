import api from "./axios";

import { authHeaders, clearAuth, ensureAuthenticated } from "./login";
import {
	BadAuthException,
	BlockedException,
	CommentNotFoundException,
	InternalServerError,
	PostNotFoundException
} from "./apiErrors";

const postAuthorCache = new Map();
const commentPostCache = new Map();

function normalizeId(value) {
	const parsed = Number(value);
	return Number.isInteger(parsed) && parsed >= 0 ? parsed : null;
}

export function cacheAuthorPosts(authorId, postIds = []) {
	const parsedAuthorId = normalizeId(authorId);
	if (parsedAuthorId == null)
		return;
	for (const postId of postIds) {
		const parsedPostId = normalizeId(postId);
		if (parsedPostId != null)
			postAuthorCache.set(parsedPostId, parsedAuthorId);
	}
}

export function cacheCommentIds(postId, commentIds = []) {
	const parsedPostId = normalizeId(postId);
	if (parsedPostId == null)
		return;
	for (const commentId of commentIds) {
		const parsedCommentId = normalizeId(commentId);
		if (parsedCommentId != null)
			commentPostCache.set(parsedCommentId, parsedPostId);
	}
}

export function cachePostPayload(post) {
	const postId = normalizeId(post?.post_id);
	const authorId = normalizeId(post?.author_id);
	if (postId != null && authorId != null)
		postAuthorCache.set(postId, authorId);
	cacheCommentIds(post?.post_id, post?.comments ?? []);
}

export function normalizePost(post) {
	cachePostPayload(post);
	return {
		postID: post.post_id,
		author: post.author_id,
		pubTime: post.pub_time,
		imageB64: post.image,
		caption: post.caption ?? "",
		likeCount: post.like_cnt,
		comments: post.comments ?? []
	};
}

async function getCandidateAuthors() {
	const userId = await ensureAuthenticated();
	const resp = await api.get("/users/me/following", {
		headers: authHeaders()
	});
	switch (resp.status) {
		case 200:
			return [userId, ...resp.data.filter(id => id !== userId)];
		case 401:
			clearAuth();
			throw BadAuthException;
		default:
			throw InternalServerError;
	}
}

async function refreshPostAuthorCache() {
	const authorIds = await getCandidateAuthors();
	const responses = await Promise.all(
		authorIds.map(authorId =>
			api.get(`/users/${authorId}/posts/`, {
				headers: authHeaders()
			})
		)
	);

	for (let i = 0; i < responses.length; i++) {
		const resp = responses[i];
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
}

export async function resolvePostAuthorId(postId, refresh = false) {
	const parsedPostId = normalizeId(postId);
	if (parsedPostId == null)
		throw PostNotFoundException;
	if (refresh)
		postAuthorCache.delete(parsedPostId);
	if (postAuthorCache.has(parsedPostId))
		return postAuthorCache.get(parsedPostId);

	// The backend nests post routes under `/users/{author}/posts/{post}` while
	// the existing UI often only knows the post id, so we memoize author ids.
	await refreshPostAuthorCache();
	if (postAuthorCache.has(parsedPostId))
		return postAuthorCache.get(parsedPostId);
	throw PostNotFoundException;
}

export async function resolveCommentContext(commentId) {
	const parsedCommentId = normalizeId(commentId);
	if (parsedCommentId == null || !commentPostCache.has(parsedCommentId))
		throw CommentNotFoundException;
	const postId = commentPostCache.get(parsedCommentId);
	const authorId = await resolvePostAuthorId(postId);
	return { postId, authorId };
}

export default async function getPost(pid) {
	await ensureAuthenticated();
	let authorId = await resolvePostAuthorId(pid);
	let resp = await api.get(`/users/${authorId}/posts/${pid}`, {
		headers: authHeaders()
	});

	if (resp.status === 404) {
		authorId = await resolvePostAuthorId(pid, true);
		resp = await api.get(`/users/${authorId}/posts/${pid}`, {
			headers: authHeaders()
		});
	}

	switch (resp.status) {
		case 200:
			return normalizePost(resp.data);
		case 401:
			clearAuth();
			throw BadAuthException;
		case 403:
			throw BlockedException;
		case 404:
			throw PostNotFoundException;
		default:
			throw InternalServerError;
	}
}
