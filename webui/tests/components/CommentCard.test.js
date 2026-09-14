import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import CommentCard from '@/components/CommentCard.vue'
import ProfileControls from '@/components/ProfileControls.vue'

import getComment from '@/services/getComment'
import isCommentLiked from '@/services/isCommentLiked'
import likeComment from '@/services/likeComment'
import unlikeComment from '@/services/unlikeComment'
import rmComment from '@/services/rmComment'
import getProfile from '@/services/getProfile'
import getProfilePicture from '@/services/getProfilePicture'
import getFollowing from '@/services/getFollowing'
import getFollowers from '@/services/getFollowers'
import getBlocked from '@/services/getBlocked'
import follow from '@/services/follow'

import { ALICE, BOB, ALICE_COMMENT, BOB_COMMENT, ME } from '../fixtures/users'
import { mountWithGlobals, installViewer } from './mount'

vi.mock('@/services/getComment')
vi.mock('@/services/isCommentLiked')
vi.mock('@/services/likeComment')
vi.mock('@/services/unlikeComment')
vi.mock('@/services/rmComment')
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

function mountComment(comment, { liked = false } = {}) {
	getComment.mockResolvedValue({ ...comment })
	let likedState = liked
	isCommentLiked.mockImplementation(async () => likedState)
	likeComment.mockImplementation(async () => { likedState = true })
	unlikeComment.mockImplementation(async () => { likedState = false })
	getProfile.mockResolvedValue(comment.author === ME ? ALICE : BOB)

	return mountWithGlobals(CommentCard, {
		props: { commentID: comment.commentID }
	})
}

describe('CommentCard', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		installViewer(ME)
		getProfilePicture.mockResolvedValue(null)
		getFollowing.mockResolvedValue([])
		getFollowers.mockResolvedValue([])
		getBlocked.mockResolvedValue([])
		follow.mockResolvedValue()
		rmComment.mockResolvedValue()
	})

	afterEach(() => {
		vi.restoreAllMocks()
	})

	it('renders comment content and like count after load', async () => {
		const wrapper = mountComment(BOB_COMMENT)
		await flushPromises()

		expect(wrapper.get('.caption').text()).toBe('cool pic')
		expect(wrapper.get('.postCtrl button').text()).toContain('2')
	})

	it('own comment shows delete and hides author follow controls', async () => {
		const wrapper = mountComment(ALICE_COMMENT)
		await flushPromises()

		expect(wrapper.find('.delBtn').exists()).toBe(true)
		expect(wrapper.findComponent(ProfileControls).exists()).toBe(false)
	})

	it('foreign comment shows author follow and hides delete', async () => {
		const wrapper = mountComment(BOB_COMMENT)
		await flushPromises()

		expect(wrapper.find('.delBtn').exists()).toBe(false)
		expect(wrapper.findComponent(ProfileControls).exists()).toBe(true)
		expect(wrapper.get('button.btn-outline-primary').text()).toBe('Follow')
	})

	it('liking an unliked comment increments the count', async () => {
		const wrapper = mountComment(BOB_COMMENT, { liked: false })
		await flushPromises()

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(likeComment).toHaveBeenCalledWith(BOB_COMMENT.commentID)
		expect(wrapper.get('.postCtrl button').text()).toContain('3')
		expect(wrapper.get('.postCtrl svg').classes()).toContain('heartFilled')
	})

	it('unliking a liked comment decrements the count', async () => {
		const wrapper = mountComment(BOB_COMMENT, { liked: true })
		await flushPromises()

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(unlikeComment).toHaveBeenCalledWith(BOB_COMMENT.commentID)
		expect(wrapper.get('.postCtrl button').text()).toContain('1')
		expect(wrapper.get('.postCtrl svg').classes()).not.toContain('heartFilled')
	})

	it('like failure is emitted as renderError', async () => {
		const wrapper = mountComment(BOB_COMMENT)
		await flushPromises()
		likeComment.mockReset()
		likeComment.mockRejectedValue(new Error('like failed'))
		isCommentLiked.mockImplementation(async () => false)

		await wrapper.get('.postCtrl button').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('like failed')
	})

	it('like-status failure after load is emitted as renderError', async () => {
		getComment.mockResolvedValue({ ...BOB_COMMENT })
		isCommentLiked.mockRejectedValue(new Error('status down'))
		getProfile.mockResolvedValue(BOB)

		const wrapper = mountWithGlobals(CommentCard, {
			props: { commentID: BOB_COMMENT.commentID }
		})
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('status down')
	})

	it('delete emits commentDeleted', async () => {
		const wrapper = mountComment(ALICE_COMMENT)
		await flushPromises()

		await wrapper.get('.delBtn').trigger('click')
		await flushPromises()

		expect(rmComment).toHaveBeenCalledWith(ALICE_COMMENT.commentID)
		expect(wrapper.emitted('commentDeleted')).toHaveLength(1)
	})

	it('delete failure is emitted as renderError', async () => {
		rmComment.mockRejectedValue(new Error('nope'))
		const wrapper = mountComment(ALICE_COMMENT)
		await flushPromises()

		await wrapper.get('.delBtn').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('nope')
		expect(wrapper.emitted('commentDeleted')).toBeFalsy()
	})

	it('getComment failure emits renderError without the card', async () => {
		getComment.mockRejectedValue(new Error('missing'))
		const wrapper = mountWithGlobals(CommentCard, {
			props: { commentID: 99 }
		})
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0].message).toBe('missing')
		expect(wrapper.find('.caption').exists()).toBe(false)
	})

	it('ProCard error is unwrapped and re-emitted as renderError', async () => {
		follow.mockRejectedValue(new Error('boom'))
		const wrapper = mountComment(BOB_COMMENT)
		await flushPromises()

		await wrapper.get('button.btn-outline-primary').trigger('click')
		await flushPromises()

		expect(wrapper.emitted('renderError')[0][0]).toBe('Error: boom')
	})
})
