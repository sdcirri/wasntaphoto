import { describe, it, expect, vi, beforeEach } from 'vitest'
import likeComment from '@/services/likeComment'
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

describe('likeComment', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolveCommentContext.mockResolvedValue({ postId: 10, authorId: 7 })
	})

	it('resolves on 204', async () => {
		api.put.mockResolvedValue({ status: 204 })
		await expect(likeComment(5)).resolves.toBeUndefined()
		expect(api.put).toHaveBeenCalledWith('/users/7/posts/10/comments/5/like', null)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.put.mockResolvedValue({ status: 401 })
		await expect(likeComment(5)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws CommentNotFoundException on 404', async () => {
		api.put.mockResolvedValue({ status: 404 })
		await expect(likeComment(5)).rejects.toBe(CommentNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.put.mockResolvedValue({ status: 500 })
		await expect(likeComment(5)).rejects.toBe(InternalServerError)
	})
})
