import { reactive } from "vue";

import api from "./axios";
import {
	UsernameAlreadyTakenException,
	WeakPasswordException,
	InternalServerError
} from "./apiErrors";
import login from "./login";

export default async function registerAndLogin(username, password) {
	const resp = await api.post(
		"/users/",
		{ username, password },
		{ headers: { "Content-Type": "application/json" } }
	);

	switch (resp.status) {
		case 200:
			await login(username, password);
			break;
		case 400:
			throw WeakPasswordException;
		case 409:
			throw UsernameAlreadyTakenException;
		default:
			throw InternalServerError;
	}
}
