import { describe, it, expect, vi, beforeEach } from 'vitest'
import getPostMedia from '@/services/getPostMedia'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolvePostAuthorId } from '@/services/getPost'
import {
	BadAuthException,
	BlockedException,
	InternalServerError,
	PostNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolvePostAuthorId: vi.fn() }))

describe('getPostMedia', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock')
		resolvePostAuthorId.mockResolvedValue(7)
	})

	it('returns object URL on 200', async () => {
		const blob = new Blob(['x'])
		api.get.mockResolvedValue({ status: 200, data: blob })
		await expect(getPostMedia(10)).resolves.toBe('blob:mock')
		expect(api.get).toHaveBeenCalledWith('/users/7/posts/10/media', { responseType: 'blob' })
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(getPostMedia(10)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws BlockedException on 403', async () => {
		api.get.mockResolvedValue({ status: 403 })
		await expect(getPostMedia(10)).rejects.toBe(BlockedException)
	})

	it('throws PostNotFoundException on 404', async () => {
		api.get.mockResolvedValue({ status: 404 })
		await expect(getPostMedia(10)).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(getPostMedia(10)).rejects.toBe(InternalServerError)
	})
})
