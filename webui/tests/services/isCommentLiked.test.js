import { describe, it, expect, vi, beforeEach } from 'vitest'
import isCommentLiked from '@/services/isCommentLiked'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolveCommentContext } from '@/services/getPost'
import {
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolveCommentContext: vi.fn() }))

describe('isCommentLiked', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolveCommentContext.mockResolvedValue({ postId: 10, authorId: 7 })
	})

	it('returns data on 200', async () => {
		api.get.mockResolvedValue({ status: 200, data: false })
		await expect(isCommentLiked(5)).resolves.toBe(false)
		expect(api.get).toHaveBeenCalledWith('/users/7/posts/10/comments/5/like')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(isCommentLiked(5)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws CommentNotFoundException on 404', async () => {
		api.get.mockResolvedValue({ status: 404 })
		await expect(isCommentLiked(5)).rejects.toBe(CommentNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(isCommentLiked(5)).rejects.toBe(InternalServerError)
	})
})
