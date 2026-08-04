import { describe, it, expect, vi, beforeEach } from 'vitest'
import newPost from '@/services/newPost'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { cachePostPayload, normalizePost } from '@/services/getPost'
import { BadAuthException, BadUploadException, InternalServerError } from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({
	cachePostPayload: vi.fn(),
	normalizePost: vi.fn()
}))

describe('newPost', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
	})

	it('returns normalized post on 200', async () => {
		const raw = {
			post_id: 1,
			author_id: 2,
			pub_time: '2024-01-01',
			image: 'img',
			caption: 'c',
			like_cnt: 0,
			comments: []
		}
		const normalized = { postID: 1 }
		api.post.mockResolvedValue({ status: 200, data: raw })
		normalizePost.mockReturnValue(normalized)
		await expect(newPost('img', 'c')).resolves.toEqual(normalized)
		expect(api.post).toHaveBeenCalledWith('/users/me/posts/', { image: 'img', caption: 'c' }, {
			headers: { 'Content-Type': 'application/json' }
		})
		expect(cachePostPayload).toHaveBeenCalledWith(raw)
		expect(normalizePost).toHaveBeenCalledWith(raw)
	})

	it('throws BadUploadException on 400', async () => {
		api.post.mockResolvedValue({ status: 400 })
		await expect(newPost('img', 'c')).rejects.toBe(BadUploadException)
	})

	it('throws BadUploadException on 422', async () => {
		api.post.mockResolvedValue({ status: 422 })
		await expect(newPost('img', 'c')).rejects.toBe(BadUploadException)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.post.mockResolvedValue({ status: 401 })
		await expect(newPost('img', 'c')).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws InternalServerError on any other status', async () => {
		api.post.mockResolvedValue({ status: 500 })
		await expect(newPost('img', 'c')).rejects.toBe(InternalServerError)
	})
})
