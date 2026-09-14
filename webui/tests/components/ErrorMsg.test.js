import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorMsg from '@/components/ErrorMsg.vue'

describe('ErrorMsg', () => {
	it('renders the message in an alert', () => {
		const wrapper = mount(ErrorMsg, { props: { msg: 'login failed' } })

		expect(wrapper.get('[role="alert"]').text()).toBe('login failed')
		expect(wrapper.classes()).toContain('alert-danger')
	})
})
