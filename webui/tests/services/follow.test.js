import { describe, it, expect, vi, beforeEach } from 'vitest'
import follow from '@/services/follow'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import {
	BadFollowOperation,
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('follow', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('resolves on 200', async () => {
		api.post.mockResolvedValue({ status: 200 })
		await expect(follow(42)).resolves.toBeUndefined()
		expect(api.post).toHaveBeenCalledWith('/users/me/following/42')
	})

	it('throws BadFollowOperation on 400', async () => {
		api.post.mockResolvedValue({ status: 400 })
		await expect(follow(42)).rejects.toBe(BadFollowOperation)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.post.mockResolvedValue({ status: 401 })
		await expect(follow(42)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on 403', async () => {
		api.post.mockResolvedValue({ status: 403 })
		await expect(follow(42)).rejects.toBe(BlockedException)
	})

	it('throws UserNotFoundException on 404', async () => {
		api.post.mockResolvedValue({ status: 404 })
		await expect(follow(42)).rejects.toBe(UserNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.post.mockResolvedValue({ status: 500 })
		await expect(follow(42)).rejects.toBe(InternalServerError)
	})

	it('checks auth before making the request', async () => {
		loginService.ensureAuthenticated.mockRejectedValue(new Error('not logged in'))
		await expect(follow(42)).rejects.toThrow('not logged in')
		expect(api.post).not.toHaveBeenCalled()
	})
})
