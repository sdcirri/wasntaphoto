import { describe, it, expect, vi, beforeEach } from 'vitest'
import getFeed from '@/services/getFeed'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { cacheAuthorPosts } from '@/services/getPost'
import { BadAuthException, InternalServerError } from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ cacheAuthorPosts: vi.fn() }))

describe('getFeed', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('returns feed and caches author posts on 200', async () => {
		const feed = [1, 2]
		api.get
			.mockResolvedValueOnce({ status: 200, data: feed })
			.mockResolvedValueOnce({ status: 200, data: [2] })
			.mockResolvedValueOnce({ status: 200, data: [1] })
			.mockResolvedValueOnce({ status: 200, data: [2] })

		await expect(getFeed()).resolves.toEqual(feed)
		expect(cacheAuthorPosts).toHaveBeenCalledWith(1, [1])
		expect(cacheAuthorPosts).toHaveBeenCalledWith(2, [2])
	})

	it('clears auth and throws BadAuthException on feed 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValueOnce({ status: 401 })
		await expect(getFeed()).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws InternalServerError on feed unknown status', async () => {
		api.get.mockResolvedValueOnce({ status: 500 })
		await expect(getFeed()).rejects.toBe(InternalServerError)
	})

	it('clears auth and throws BadAuthException on following 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 401 })
		await expect(getFeed()).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws InternalServerError on following unknown status', async () => {
		api.get
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 500 })
		await expect(getFeed()).rejects.toBe(InternalServerError)
	})

	it('clears auth and throws BadAuthException on author posts 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 401 })
		await expect(getFeed()).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('ignores 403/404 on individual author post lists', async () => {
		api.get
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 200, data: [99] })
			.mockResolvedValueOnce({ status: 403 })
			.mockResolvedValueOnce({ status: 404 })
		await expect(getFeed()).resolves.toEqual([])
	})

	it('throws InternalServerError on author posts unknown status', async () => {
		api.get
			.mockResolvedValueOnce({ status: 200, data: [] })
			.mockResolvedValueOnce({ status: 200, data: [99] })
			.mockResolvedValueOnce({ status: 500 })
		await expect(getFeed()).rejects.toBe(InternalServerError)
	})
})
