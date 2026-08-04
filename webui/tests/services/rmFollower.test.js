import { describe, it, expect, vi, beforeEach } from 'vitest'
import rmFollower from '@/services/rmFollower'
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

describe('rmFollower', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('resolves on 204', async () => {
		api.delete.mockResolvedValue({ status: 204 })
		await expect(rmFollower(42)).resolves.toBeUndefined()
		expect(api.delete).toHaveBeenCalledWith('/users/me/followers/42')
	})

	it('throws BadFollowOperation on 400', async () => {
		api.delete.mockResolvedValue({ status: 400 })
		await expect(rmFollower(42)).rejects.toBe(BadFollowOperation)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.delete.mockResolvedValue({ status: 401 })
		await expect(rmFollower(42)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on 403', async () => {
		api.delete.mockResolvedValue({ status: 403 })
		await expect(rmFollower(42)).rejects.toBe(BlockedException)
	})

	it('throws UserNotFoundException on 404', async () => {
		api.delete.mockResolvedValue({ status: 404 })
		await expect(rmFollower(42)).rejects.toBe(UserNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.delete.mockResolvedValue({ status: 500 })
		await expect(rmFollower(42)).rejects.toBe(InternalServerError)
	})

	it('checks auth before making the request', async () => {
		loginService.ensureAuthenticated.mockRejectedValue(new Error('not logged in'))
		await expect(rmFollower(42)).rejects.toThrow('not logged in')
		expect(api.delete).not.toHaveBeenCalled()
	})
})
