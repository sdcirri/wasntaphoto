import { describe, it, expect, vi, beforeEach } from 'vitest'
import getProfile from '@/services/getProfile'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { cacheAuthorPosts } from '@/services/getPost'
import {
	BadAuthException,
	BadIdsException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ cacheAuthorPosts: vi.fn() }))

describe('getProfile', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('returns normalized profile on 200', async () => {
		const profile = { user_id: 2, username: 'alice', followers_cnt: 1, following_cnt: 2 }
		const posts = [10, 11]
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 200, data: posts })

		await expect(getProfile(2)).resolves.toEqual({
			userID: 2,
			username: 'alice',
			followers: 1,
			following: 2,
			posts
		})
		expect(cacheAuthorPosts).toHaveBeenCalledWith(2, posts)
	})

	it('maps own uid to "me" path', async () => {
		const profile = { user_id: 1, username: 'me', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 200, data: [] })

		await getProfile(1)
		expect(api.get).toHaveBeenCalledWith('/users/me')
		expect(api.get).toHaveBeenCalledWith('/users/me/posts/')
	})

	it('maps "me" uid to "me" path', async () => {
		const profile = { user_id: 1, username: 'me', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 200, data: [] })

		await getProfile('me')
		expect(api.get).toHaveBeenCalledWith('/users/me')
	})

	it('clears auth and throws BadAuthException on profile 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValueOnce({ status: 401 })
		await expect(getProfile(2)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on profile 403', async () => {
		api.get.mockResolvedValueOnce({ status: 403 })
		await expect(getProfile(2)).rejects.toBe(BlockedException)
	})

	it('throws UserNotFoundException on profile 404', async () => {
		api.get.mockResolvedValueOnce({ status: 404 })
		await expect(getProfile(2)).rejects.toBe(UserNotFoundException)
	})

	it('throws BadIdsException on profile 422', async () => {
		api.get.mockResolvedValueOnce({ status: 422 })
		await expect(getProfile(2)).rejects.toBe(BadIdsException)
	})

	it('throws InternalServerError on profile unknown status', async () => {
		api.get.mockResolvedValueOnce({ status: 500 })
		await expect(getProfile(2)).rejects.toBe(InternalServerError)
	})

	it('clears auth and throws BadAuthException on posts 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		const profile = { user_id: 2, username: 'alice', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 401 })
		await expect(getProfile(2)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on posts 403', async () => {
		const profile = { user_id: 2, username: 'alice', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 403 })
		await expect(getProfile(2)).rejects.toBe(BlockedException)
	})

	it('throws UserNotFoundException on posts 404', async () => {
		const profile = { user_id: 2, username: 'alice', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 404 })
		await expect(getProfile(2)).rejects.toBe(UserNotFoundException)
	})

	it('throws InternalServerError on posts unknown status', async () => {
		const profile = { user_id: 2, username: 'alice', followers_cnt: 0, following_cnt: 0 }
		api.get
			.mockResolvedValueOnce({ status: 200, data: profile })
			.mockResolvedValueOnce({ status: 500 })
		await expect(getProfile(2)).rejects.toBe(InternalServerError)
	})
})
