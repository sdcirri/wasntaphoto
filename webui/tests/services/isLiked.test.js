import { describe, it, expect, vi, beforeEach } from 'vitest'
import isLiked from '@/services/isLiked'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolvePostAuthorId } from '@/services/getPost'
import { BadAuthException, InternalServerError, PostNotFoundException } from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolvePostAuthorId: vi.fn() }))

describe('isLiked', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolvePostAuthorId.mockResolvedValue(7)
	})

	it('returns data on 200', async () => {
		api.get.mockResolvedValue({ status: 200, data: true })
		await expect(isLiked(10)).resolves.toBe(true)
		expect(resolvePostAuthorId).toHaveBeenCalledWith(10)
		expect(api.get).toHaveBeenCalledWith('/users/7/posts/10/like')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(isLiked(10)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws PostNotFoundException on 404', async () => {
		api.get.mockResolvedValue({ status: 404 })
		await expect(isLiked(10)).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(isLiked(10)).rejects.toBe(InternalServerError)
	})
})
