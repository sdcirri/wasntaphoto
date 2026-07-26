<script>
import { ref } from 'vue'

import login from '@/services/login'

export default {
	data: function () {
		return {
			errormsg: null,
			username: ref(),
			password: ref(),
			userID: null
		}
	},
	methods: {
		async login() {
			try {
				this.userID = await login(this.username, this.password);
				this.$emit("loggedIn");
				if (this.$router.options.history.state.back == null)
					this.$router.replace("/");
				else this.$router.back();
			} catch (e) {
				this.errormsg = e.toString();
			}
		}
	}
}
</script>

<template>
	<div>
		<div
			class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
			<h1 class="h2">Login</h1>
		</div>
		<div class="d-flex flex-wrap flex-md-nowrap flex-column align-items-center pt-3 pb-2 mb-3 centerDiv">
			<img class="wasa-big" src="../assets/wasaphoto.svg" />
			<h5>Login to continue to this site</h5>
		</div>
		<div class="d-flex flex-column gap-3 flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 centerDiv">
			<input class="w-15" v-model="username" placeholder="username" @keyup.enter="this.login" />
			<input class="w-15" v-model="password" type="password" placeholder="password" @keyup.enter="this.login" />
			<button type="button" class="btn btn-sm btn-outline-primary w-15" @click="this.login">
				Login
			</button>
			<RouterLink to="/register">New here? Register!</RouterLink>
		</div>

		<ErrorMsg v-if="errormsg" :msg="errormsg"></ErrorMsg>
	</div>
</template>

<style>
.wasa-big {
	height: 20vh;
}
</style>
