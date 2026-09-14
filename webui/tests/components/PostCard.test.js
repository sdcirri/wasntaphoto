import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import PostCard from '@/components/PostCard.vue'
import ProfileControls from '@/components/ProfileControls.vue'

import getPost from '@/services/getPost'
import getPostMedia from '@/services/getPostMedia'
import isLiked from '@/services/isLiked'
import likePost from '@/services/likePost'
import unlikePost from '@/services/unlikePost'
import rmPost from '@/services/rmPost'
import getProfile from '@/services/getProfile'
import getProfilePicture from '@/services/getProfilePicture'
import getFollowing from '@/services/getFollowing'
import getFollowers from '@/services/getFollowers'
import getBlocked from '@/services/getBlocked'
import follow from '@/services/follow'

import { ALICE, BOB, ALICE_POST, BOB_POST, ME, OTHER } from '../fixtures/users'
import { mountWithGlobals, installViewer } from './mount'

vi.mock('@/services/getPost')
vi.mock('@/services/getPostMedia')
vi.mock('@/services/isLiked')
vi.mock('@/services/likePost')
vi.mock('@/services/unlikePost')
vi.mock('@/services/rmPost')
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

function mountPost(post, { liked = false, router } = {}) {
	getPost.mockResolvedValue({ ...post })
	getPostMedia.mockResolvedValue('/media.jpg')
	let likedState = liked
	isLiked.mockImplementation(async () => likedState)
	likePost.mockImplementation(async () => { likedState = true })
	unlikePost.mockImplementation(async () => { likedState = false })
	getProfile.mockResolvedValue(post.author === ME ? ALICE : BOB)

	return mountWithGlobals(PostCard, {
		props: { ppostID: post.postID },
		global: {
			mocks: router ? { $router: router } : { $router: { push: vi.fn() } }
		}
	})
}

describe('PostCard', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		installViewer(ME)
		getProfilePicture.mockResolvedValue(null)
		getFollowing.mockResolvedValue([])
		getFollowers.mockResolvedValue([])
		getBlocked.mockResolvedValue([])
		follow.mockResolvedValue()
		rmPost.mockResolvedValue()
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	it('renders caption and like count after load', async () => {
		const wrapper = mountPost(BOB_POST)
		await flushPromises()

		expect(wrapper.get('.caption').text()).toBe('hello from bob')
		expect(wrapper.get('.postCtrl button').text()).toContain('3')
		expect(wrapper.get('img.postImg').attributes('src')).toBe('/media.jpg')
	})

	it('own post shows delete and hides author follow controls', async () => {
		const wrapper = mountPost(ALICE_POST)
		await flushPromises()

		expect(wrapper.find('.delBtn').exists()).toBe(true)
		expect(wrapper.findComponent(ProfileControls).exists()).toBe(false)
		const links = wrapper.findAllComponents({ name: 'RouterLink' })
		expect(links.map((l) => l.props('to'))).toContain('/posts/10/likes')
	})

	it('foreign post shows author follow and hides delete', async () => {
		const wrapper = mountPost(BOB_POST)
		await flushPromises()

		expect(wrapper.find('.delBtn').exists()).toBe(false)
		expect(wrapper.findComponent(ProfileControls).exists()).toBe(true)
		expect(wrapper.get('button.btn-outline-primary').text()).toBe('Follow')
	})

	it('liking an unliked post increments the count', async () => {
		const wrapper = mountPost(BOB_POST, { liked: false })
		await flushPromises()

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(likePost).toHaveBeenCalledWith(BOB_POST.postID)
		expect(wrapper.get('.postCtrl button').text()).toContain('4')
		expect(wrapper.get('.postCtrl svg').classes()).toContain('heartFilled')
	})

	it('unliking a liked post decrements the count', async () => {
		const wrapper = mountPost(BOB_POST, { liked: true })
		await flushPromises()

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(unlikePost).toHaveBeenCalledWith(BOB_POST.postID)
		expect(wrapper.get('.postCtrl button').text()).toContain('2')
		expect(wrapper.get('.postCtrl svg').classes()).not.toContain('heartFilled')
	})

	it('like failure is emitted as renderError', async () => {
		const wrapper = mountPost(BOB_POST)
		await flushPromises()
		likePost.mockReset()
		likePost.mockRejectedValue(new Error('like failed'))
		isLiked.mockImplementation(async () => false)

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('like failed')
	})

	it('like-status failure after load is emitted as renderError', async () => {
		getPost.mockResolvedValue({ ...BOB_POST })
		getPostMedia.mockResolvedValue('/media.jpg')
		isLiked.mockRejectedValue(new Error('status down'))
		getProfile.mockResolvedValue(BOB)

		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: BOB_POST.postID },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('status down')
	})

	it('like is ignored while the card is still loading', async () => {
		let resolvePost
		getPost.mockReturnValue(new Promise((resolve) => { resolvePost = resolve }))
		getPostMedia.mockResolvedValue('/media.jpg')
		isLiked.mockResolvedValue(false)
		getProfile.mockResolvedValue(BOB)

		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: BOB_POST.postID },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await wrapper.vm.toggleLike()
		expect(likePost).not.toHaveBeenCalled()

		resolvePost({ ...BOB_POST })
		await flushPromises()
	})

	it('delete emits postDeleted', async () => {
		const wrapper = mountPost(ALICE_POST)
		await flushPromises()

		await wrapper.get('.delBtn').trigger('click')
		await flushPromises()

		expect(rmPost).toHaveBeenCalledWith(ALICE_POST.postID)
		expect(wrapper.emitted('postDeleted')).toHaveLength(1)
	})

	it('delete failure is emitted as renderError', async () => {
		rmPost.mockRejectedValue(new Error('nope'))
		const wrapper = mountPost(ALICE_POST)
		await flushPromises()

		await wrapper.get('.delBtn').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('nope')
		expect(wrapper.emitted('postDeleted')).toBeFalsy()
	})

	it('comment button pushes the comments route', async () => {
		const push = vi.fn()
		const wrapper = mountPost(BOB_POST, { router: { push } })
		await flushPromises()

		const buttons = wrapper.findAll('.postCtrl button')
		await buttons[buttons.length - 1].trigger('click')

		expect(push).toHaveBeenCalledWith(`/posts/${BOB_POST.postID}/comments`)
	})

	it('getPost returning null is treated as a renderError', async () => {
		getPost.mockResolvedValue(null)
		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: 99 },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		expect(wrapper.emitted('renderError')).toBeTruthy()
		expect(wrapper.find('.caption').exists()).toBe(false)
	})

	it('getPost failure emits renderError without the card', async () => {
		getPost.mockRejectedValue(new Error('missing'))
		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: 99 },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('missing')
		expect(wrapper.find('.caption').exists()).toBe(false)
	})

	it('ProCard error is unwrapped and re-emitted as renderError', async () => {
		follow.mockRejectedValue(new Error('boom'))
		const wrapper = mountPost(BOB_POST)
		await flushPromises()

		await wrapper.get('button.btn-outline-primary').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0]).toBe('Error: boom')
	})

	it('revokes the previous media URL when the card refreshes', async () => {
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
		getPost.mockResolvedValue({ ...BOB_POST })
		getPostMedia
			.mockResolvedValueOnce('blob:http://localhost/old')
			.mockResolvedValueOnce('blob:http://localhost/new')
		isLiked.mockResolvedValue(false)
		getProfile.mockResolvedValue(BOB)

		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: BOB_POST.postID },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		await wrapper.vm.refresh()
		await flushPromises()

		expect(revokeSpy).toHaveBeenCalledWith('blob:http://localhost/old')
		expect(wrapper.get('img.postImg').attributes('src')).toBe('blob:http://localhost/new')
	})

	it('does not revoke media on unmount when none was loaded', async () => {
		getPost.mockRejectedValue(new Error('missing'))
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: 99 },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		wrapper.unmount()
		expect(revokeSpy).not.toHaveBeenCalled()
	})

	it('revokes media URL on unmount', async () => {
		getPost.mockResolvedValue({ ...BOB_POST })
		getPostMedia.mockResolvedValue('blob:http://localhost/media')
		isLiked.mockResolvedValue(false)
		getProfile.mockResolvedValue(BOB)
		const revokeSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

		const wrapper = mountWithGlobals(PostCard, {
			props: { ppostID: BOB_POST.postID },
			global: { mocks: { $router: { push: vi.fn() } } }
		})
		await flushPromises()

		wrapper.unmount()
		expect(revokeSpy).toHaveBeenCalledWith('blob:http://localhost/media')
	})
})
