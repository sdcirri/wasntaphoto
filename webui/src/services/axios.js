import axios from "axios";

const instance = axios.create({
	baseURL: __API_URL__,
	timeout: 1000 * 5
});

instance.interceptors.response.use(
	function (response) {
		return response;
	},
	function (error) {
		if (error.response != null)
			return Promise.resolve(error.response);
		return Promise.reject(error);
	}
);

export default instance;
