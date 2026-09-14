import { vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMsg from '@/components/ErrorMsg.vue'
import ProCard from '@/components/ProCard.vue'
import ProfileControls from '@/components/ProfileControls.vue'
import * as loginService from '@/services/login'

export function installViewer(userId) {
	loginService.loggedInUserId.value = userId
	vi.spyOn(loginService, 'getCachedUserId').mockReturnValue(userId)
}

export function mountWithGlobals(Component, options = {}) {
	const { global = {}, ...rest } = options
	const { components = {}, stubs = {}, mocks = {}, ...globalRest } = global

	return mount(Component, {
		...rest,
		global: {
			components: {
				LoadingSpinner,
				ErrorMsg,
				ProCard,
				ProfileControls,
				...components
			},
			stubs: {
				RouterLink: {
					name: 'RouterLink',
					props: ['to'],
					template: '<a class="router-link-stub"><slot /></a>'
				},
				...stubs
			},
			mocks,
			...globalRest
		}
	})
}
