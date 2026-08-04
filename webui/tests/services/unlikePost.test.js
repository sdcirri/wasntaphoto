import { describe, it, expect, vi, beforeEach } from 'vitest'
import unlikePost from '@/services/unlikePost'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolvePostAuthorId } from '@/services/getPost'
import { BadAuthException, InternalServerError, PostNotFoundException } from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolvePostAuthorId: vi.fn() }))

describe('unlikePost', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolvePostAuthorId.mockResolvedValue(7)
	})

	it('resolves on 204', async () => {
		api.delete.mockResolvedValue({ status: 204 })
		await expect(unlikePost(10)).resolves.toBeUndefined()
		expect(resolvePostAuthorId).toHaveBeenCalledWith(10)
		expect(api.delete).toHaveBeenCalledWith('/users/7/posts/10/like')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.delete.mockResolvedValue({ status: 401 })
		await expect(unlikePost(10)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws PostNotFoundException on 404', async () => {
		api.delete.mockResolvedValue({ status: 404 })
		await expect(unlikePost(10)).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.delete.mockResolvedValue({ status: 500 })
		await expect(unlikePost(10)).rejects.toBe(InternalServerError)
	})
})
