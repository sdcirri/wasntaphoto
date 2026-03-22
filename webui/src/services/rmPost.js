import {
    AccessDeniedException,
    BadAuthException,
    InternalServerError,
    PostNotFoundException
} from './apiErrors'
import api from './axios'

import { authStatus } from './login'

export default async function rmPost(postID) {
    if (authStatus.status == null) throw BadAuthException;
    let resp = await api.delete(`/posts/${postID}/delete`,
        { "headers": { "Authorization": `bearer ${authStatus.status}` } });
    switch (resp.status) {
        case 204:
            return;
        case 401:
            throw BadAuthException;
        case 403:
            throw AccessDeniedException;
        case 404:
            throw PostNotFoundException;
        default:
            throw InternalServerError;
    }
}
