import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import SearchView from '@/views/SearchView.vue'
import NewPostView from '@/views/NewPostView.vue'
import ProfileView from '@/views/ProfileView.vue'
import FollowersView from '@/views/FollowersView.vue'
import FollowingView from '@/views/FollowingView.vue'
import BlockedView from '@/views/BlockedView.vue'
import EditProfileView from '@/views/EditProfileView.vue'
import PostLikesView from '@/views/PostLikesView.vue'
import CommentsView from '@/views/CommentsView.vue'
import { ensureAuthenticated } from '@/services/login'

const router = createRouter({
	history: createWebHashHistory(import.meta.env.BASE_URL),
	routes: [
		{ path: '/', component: HomeView, meta: { requiresAuth: true } },
		{ path: '/register', component: RegisterView },
		{ path: '/login', component: LoginView },
		{ path: '/search', component: SearchView },
		{ path: '/newpost', component: NewPostView, meta: { requiresAuth: true } },
		{ path: '/profile/:id', component: ProfileView, meta: { requiresAuth: true } },
		{ path: '/profile/:id/followers', component: FollowersView, meta: { requiresAuth: true } },
		{ path: '/profile/:id/following', component: FollowingView, meta: { requiresAuth: true } },
		{ path: '/profile/:id/blocked', component: BlockedView, meta: { requiresAuth: true } },
		{ path: '/profile/:id/edit', component: EditProfileView, meta: { requiresAuth: true } },
		{ path: '/posts/:id/likes', component: PostLikesView, meta: { requiresAuth: true } },
		{ path: '/posts/:id/comments', component: CommentsView, meta: { requiresAuth: true } }
	]
})

router.beforeEach(async (to) => {
	if (!to.meta.requiresAuth) return true;
	try {
		await ensureAuthenticated();
		return true;
	} catch (error) {
		console.error(error);
		return { path: '/login', query: { redirect: to.fullPath } };
	}
})

export default router
