import { describe, it, expect, vi, beforeEach } from 'vitest'
import setPP from '@/services/setPP'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import {
	BadAuthException,
	ImageTooBigException,
	InternalServerError
} from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('setPP', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('sends decoded bytes on 204', async () => {
		api.put.mockResolvedValue({ status: 204 })
		await expect(setPP('aGVsbG8=')).resolves.toBeUndefined()
		expect(api.put).toHaveBeenCalledWith(
			'/users/me/pp',
			expect.any(Uint8Array),
			{ headers: { 'Content-Type': 'application/octet-stream' } }
		)
		const bytes = api.put.mock.calls[0][1]
		expect(Array.from(bytes)).toEqual([104, 101, 108, 108, 111])
	})

	it('throws ImageTooBigException on 400', async () => {
		api.put.mockResolvedValue({ status: 400 })
		await expect(setPP('aGVsbG8=')).rejects.toBe(ImageTooBigException)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.put.mockResolvedValue({ status: 401 })
		await expect(setPP('aGVsbG8=')).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws InternalServerError on any other status', async () => {
		api.put.mockResolvedValue({ status: 500 })
		await expect(setPP('aGVsbG8=')).rejects.toBe(InternalServerError)
	})
})
