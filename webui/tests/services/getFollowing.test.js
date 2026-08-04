import { describe, it, expect, vi, beforeEach } from 'vitest'
import getFollowing from '@/services/getFollowing'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { AccessDeniedException, BadAuthException, InternalServerError } from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('getFollowing', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('returns data on 200', async () => {
		const data = [2, 3, 4]
		api.get.mockResolvedValue({ status: 200, data })
		await expect(getFollowing()).resolves.toEqual(data)
		expect(api.get).toHaveBeenCalledWith('/users/me/following')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(getFollowing()).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws AccessDeniedException on 403', async () => {
		api.get.mockResolvedValue({ status: 403 })
		await expect(getFollowing()).rejects.toBe(AccessDeniedException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(getFollowing()).rejects.toBe(InternalServerError)
	})
})
