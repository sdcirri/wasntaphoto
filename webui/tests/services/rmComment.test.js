import { describe, it, expect, vi, beforeEach } from 'vitest'
import rmComment from '@/services/rmComment'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { resolveCommentContext } from '@/services/getPost'
import {
	AccessDeniedException,
	BadAuthException,
	CommentNotFoundException,
	InternalServerError
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({ resolveCommentContext: vi.fn() }))

describe('rmComment', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolveCommentContext.mockResolvedValue({ postId: 10, authorId: 7 })
	})

	it('resolves on 204', async () => {
		api.delete.mockResolvedValue({ status: 204 })
		await expect(rmComment(5)).resolves.toBeUndefined()
		expect(api.delete).toHaveBeenCalledWith('/users/7/posts/10/comments/5')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.delete.mockResolvedValue({ status: 401 })
		await expect(rmComment(5)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws AccessDeniedException on 403', async () => {
		api.delete.mockResolvedValue({ status: 403 })
		await expect(rmComment(5)).rejects.toBe(AccessDeniedException)
	})

	it('throws CommentNotFoundException on 404', async () => {
		api.delete.mockResolvedValue({ status: 404 })
		await expect(rmComment(5)).rejects.toBe(CommentNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.delete.mockResolvedValue({ status: 500 })
		await expect(rmComment(5)).rejects.toBe(InternalServerError)
	})
})
