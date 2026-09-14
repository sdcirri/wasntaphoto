import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

describe('LoadingSpinner', () => {
	it('shows the spinner when loading', () => {
		const wrapper = mount(LoadingSpinner, {
			props: { loading: true },
			slots: { default: '<p>ready</p>' }
		})

		expect(wrapper.find('.spinner-border').exists()).toBe(true)
		expect(wrapper.text()).toContain('Loading...')
		expect(wrapper.text()).not.toContain('ready')
	})

	it('shows the slot when not loading', () => {
		const wrapper = mount(LoadingSpinner, {
			props: { loading: false },
			slots: { default: '<p>ready</p>' }
		})

		expect(wrapper.find('.spinner-border').exists()).toBe(false)
		expect(wrapper.text()).toBe('ready')
	})
})
