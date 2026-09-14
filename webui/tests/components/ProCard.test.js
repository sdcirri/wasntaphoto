import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import ProCard from '@/components/ProCard.vue'
import ProfileControls from '@/components/ProfileControls.vue'

import getProfile from '@/services/getProfile'
import getProfilePicture from '@/services/getProfilePicture'
import getFollowing from '@/services/getFollowing'
import getFollowers from '@/services/getFollowers'
import getBlocked from '@/services/getBlocked'
import follow from '@/services/follow'
import { BlockedException } from '@/services/apiErrors'

import { ALICE, BOB, ME, OTHER } from '../fixtures/users'
import { mountWithGlobals, installViewer } from './mount'

vi.mock('@/services/getProfile')
vi.mock('@/services/getProfilePicture')
vi.mock('@/services/getFollowing')
vi.mock('@/services/getFollowers')
vi.mock('@/services/getBlocked')
vi.mock('@/services/follow')
vi.mock('@/services/unfollow')
vi.mock('@/services/rmFollower')
vi.mock('@/services/block')
vi.mock('@/services/unblock')

describe('ProCard', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		installViewer(ME)
		getProfile.mockResolvedValue(BOB)
		getProfilePicture.mockResolvedValue(null)
		getFollowing.mockResolvedValue([])
		getFollowers.mockResolvedValue([])
		getBlocked.mockResolvedValue([])
		follow.mockResolvedValue()
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	it('shows the username and links to the profile', async () => {
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: false }
		})
		await flushPromises()

		expect(wrapper.get('h3').text()).toBe('bob')
		expect(wrapper.getComponent({ name: 'RouterLink' }).props('to')).toBe(`/profile/${OTHER}`)
		expect(wrapper.get('img.propic').attributes('src')).toBe('/propic_default.jpg')
	})

	it('hides controls on the viewer own profile even when asked', async () => {
		getProfile.mockResolvedValue(ALICE)
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: ME, showControls: true }
		})
		await flushPromises()

		expect(wrapper.findComponent(ProfileControls).exists()).toBe(false)
	})

	it('shows nested follow controls for another user when asked', async () => {
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()

		expect(wrapper.findComponent(ProfileControls).exists()).toBe(true)
		expect(wrapper.get('button.btn-outline-primary').text()).toBe('Follow')
	})

	it('omits controls when showControls is false', async () => {
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: false }
		})
		await flushPromises()

		expect(wrapper.findComponent(ProfileControls).exists()).toBe(false)
	})

	it('follow from nested controls refetches the profile', async () => {
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()
		const callsBefore = getProfile.mock.calls.length

		await wrapper.get('button.btn-outline-primary').trigger('click')
		await flushPromises()

		expect(follow).toHaveBeenCalledWith(OTHER)
		expect(getProfile.mock.calls.length).toBeGreaterThan(callsBefore)
	})

	it('wraps nested control errors as profileError with userID', async () => {
		follow.mockRejectedValue(new Error('boom'))
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()

		await wrapper.get('button.btn-outline-primary').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('profileError')[0][0]).toEqual({
			error: 'Error: boom',
			userID: OTHER
		})
	})

	it('emits profileError with BlockedException shape used by list views', async () => {
		getProfile.mockRejectedValue(BlockedException)
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()

		expect(wrapper.emitted('profileError')[0][0]).toEqual({
			error: BlockedException.toString(),
			userID: OTHER
		})
		expect(wrapper.find('h3').exists()).toBe(false)
	})

	it('forwards followerRm, unfollowed and unblock from nested controls', async () => {
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()

		const controls = wrapper.getComponent(ProfileControls)
		controls.vm.$emit('followerRm', OTHER)
		controls.vm.$emit('unfollowed', OTHER)
		controls.vm.$emit('unblock', OTHER)
		await flushPromises()

		expect(wrapper.emitted('followerRm')[0]).toEqual([OTHER])
		expect(wrapper.emitted('unfollowed')[0]).toEqual([OTHER])
		expect(wrapper.emitted('unblock')[0]).toEqual([OTHER])
	})

	it('revokes a stale blob propic before fetching a new one on refresh', async () => {
		getProfilePicture.mockResolvedValue('blob:http://localhost/stale')
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: true }
		})
		await flushPromises()

		getProfilePicture.mockResolvedValue('blob:http://localhost/fresh')
		await wrapper.get('button.btn-outline-primary').trigger('click')
		await flushPromises()

		expect(revokeSpy).toHaveBeenCalledWith('blob:http://localhost/stale')
		expect(wrapper.get('img.propic').attributes('src')).toBe('blob:http://localhost/fresh')
	})

	it('revokes a blob propic URL on unmount', async () => {
		getProfilePicture.mockResolvedValue('blob:http://localhost/abc')
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: false }
		})
		await flushPromises()

		wrapper.unmount()
		expect(revokeSpy).toHaveBeenCalledWith('blob:http://localhost/abc')
	})

	it('does not revoke a non-blob propic URL on unmount', async () => {
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
		const wrapper = mountWithGlobals(ProCard, {
			props: { userID: OTHER, showControls: false }
		})
		await flushPromises()

		wrapper.unmount()
		expect(revokeSpy).not.toHaveBeenCalled()
	})
})
