import { authHeaders, clearAuth, ensureAuthenticated } from "@/services/login";
import api from "@/services/axios";
import {
    BadAuthException,
    BlockedException,
    InternalServerError,
    PostNotFoundException
} from "@/services/apiErrors";
import { resolvePostAuthorId } from "@/services/getPost";


export default async function getPostMedia(postId) {
	await ensureAuthenticated();
	const authorId = await resolvePostAuthorId(postId);
	const resp = await api.get(`/users/${authorId}/posts/${postId}/media`, {
		headers: authHeaders(),
		responseType: "blob"
	});

	switch (resp.status) {
		case 200:
			return URL.createObjectURL(resp.data);
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
