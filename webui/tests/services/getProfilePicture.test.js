import { describe, it, expect, vi, beforeEach } from 'vitest'
import getProfilePicture from '@/services/getProfilePicture'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import {
	BadAuthException,
	BlockedException,
	InternalServerError,
	UserNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('getProfilePicture', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock')
	})

	it('returns object URL on 200 with non-empty blob', async () => {
		const blob = new Blob(['x'])
		api.get.mockResolvedValue({ status: 200, data: blob })
		await expect(getProfilePicture('me')).resolves.toBe('blob:mock')
		expect(api.get).toHaveBeenCalledWith('/users/me/propic', { responseType: 'blob' })
	})

	it('returns null for empty blob on 200', async () => {
		api.get.mockResolvedValue({ status: 200, data: new Blob([]) })
		await expect(getProfilePicture('me')).resolves.toBeNull()
	})

	it('maps own uid to "me" path', async () => {
		api.get.mockResolvedValue({ status: 200, data: new Blob(['x']) })
		await getProfilePicture(1)
		expect(api.get).toHaveBeenCalledWith('/users/me/propic', { responseType: 'blob' })
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(getProfilePicture(2)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on 403', async () => {
		api.get.mockResolvedValue({ status: 403 })
		await expect(getProfilePicture(2)).rejects.toBe(BlockedException)
	})

	it('returns UserNotFoundException on 404', async () => {
		api.get.mockResolvedValue({ status: 404 })
		await expect(getProfilePicture(99)).resolves.toBe(UserNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(getProfilePicture(2)).rejects.toBe(InternalServerError)
	})
})
