import { describe, it, expect, vi, beforeEach } from 'vitest'
import likePost from '@/services/likePost'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolvePostAuthorId } from '@/services/getPost'
import { BadAuthException, InternalServerError, PostNotFoundException } from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolvePostAuthorId: vi.fn() }))

describe('likePost', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolvePostAuthorId.mockResolvedValue(7)
	})

	it('resolves on 204', async () => {
		api.put.mockResolvedValue({ status: 204 })
		await expect(likePost(10)).resolves.toBeUndefined()
		expect(resolvePostAuthorId).toHaveBeenCalledWith(10)
		expect(api.put).toHaveBeenCalledWith('/users/7/posts/10/like', null)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.put.mockResolvedValue({ status: 401 })
		await expect(likePost(10)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws PostNotFoundException on 404', async () => {
		api.put.mockResolvedValue({ status: 404 })
		await expect(likePost(10)).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.put.mockResolvedValue({ status: 500 })
		await expect(likePost(10)).rejects.toBe(InternalServerError)
	})
})
