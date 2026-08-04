import { describe, it, expect, vi, beforeEach } from 'vitest'
import rmPost from '@/services/rmPost'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import {
	AccessDeniedException,
	BadAuthException,
	InternalServerError,
	PostNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('rmPost', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('resolves on 204', async () => {
		api.delete.mockResolvedValue({ status: 204 })
		await expect(rmPost(10)).resolves.toBeUndefined()
		expect(api.delete).toHaveBeenCalledWith('/users/me/posts/10')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.delete.mockResolvedValue({ status: 401 })
		await expect(rmPost(10)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws AccessDeniedException on 403', async () => {
		api.delete.mockResolvedValue({ status: 403 })
		await expect(rmPost(10)).rejects.toBe(AccessDeniedException)
	})

	it('throws PostNotFoundException on 404', async () => {
		api.delete.mockResolvedValue({ status: 404 })
		await expect(rmPost(10)).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.delete.mockResolvedValue({ status: 500 })
		await expect(rmPost(10)).rejects.toBe(InternalServerError)
	})
})
