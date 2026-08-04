import { describe, it, expect, vi, beforeEach } from 'vitest'
import setUsername from '@/services/setUsername'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import {
	BadAuthException,
	InternalServerError,
	UsernameAlreadyTakenException
} from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('setUsername', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('resolves on 204', async () => {
		api.put.mockResolvedValue({ status: 204 })
		await expect(setUsername('newname')).resolves.toBeUndefined()
		expect(api.put).toHaveBeenCalledWith(
			'/users/me/username',
			JSON.stringify('newname'),
			{ headers: { 'Content-Type': 'application/json' } }
		)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.put.mockResolvedValue({ status: 401 })
		await expect(setUsername('newname')).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws UsernameAlreadyTakenException on 409', async () => {
		api.put.mockResolvedValue({ status: 409 })
		await expect(setUsername('newname')).rejects.toBe(UsernameAlreadyTakenException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.put.mockResolvedValue({ status: 500 })
		await expect(setUsername('newname')).rejects.toBe(InternalServerError)
	})
})
