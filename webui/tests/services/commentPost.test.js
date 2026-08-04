import { describe, it, expect, vi, beforeEach } from 'vitest'
import commentPost from '@/services/commentPost'
import api from '@/services/axios'
import * as loginService from '@/services/login'
import { cacheCommentIds, resolvePostAuthorId } from '@/services/getPost'
import {
	BadAuthException,
	BadCommentException,
	InternalServerError,
	PostNotFoundException
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/getPost', () => ({
	resolvePostAuthorId: vi.fn(),
	cacheCommentIds: vi.fn()
}))

describe('commentPost', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolvePostAuthorId.mockResolvedValue(7)
	})

	it('returns comment id on 200', async () => {
		api.post.mockResolvedValue({ status: 200, data: { comment_id: 5 } })
		await expect(commentPost(10, 'hello')).resolves.toBe(5)
		expect(api.post).toHaveBeenCalledWith(
			'/users/7/posts/10/comments/',
			JSON.stringify('hello'),
			{ headers: { 'Content-Type': 'application/json' } }
		)
		expect(cacheCommentIds).toHaveBeenCalledWith(10, [5])
	})

	it('throws BadCommentException on 400', async () => {
		api.post.mockResolvedValue({ status: 400 })
		await expect(commentPost(10, 'hello')).rejects.toBe(BadCommentException)
	})

	it('throws BadCommentException on 422', async () => {
		api.post.mockResolvedValue({ status: 422 })
		await expect(commentPost(10, 'hello')).rejects.toBe(BadCommentException)
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.post.mockResolvedValue({ status: 401 })
		await expect(commentPost(10, 'hello')).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws PostNotFoundException on 404', async () => {
		api.post.mockResolvedValue({ status: 404 })
		await expect(commentPost(10, 'hello')).rejects.toBe(PostNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.post.mockResolvedValue({ status: 500 })
		await expect(commentPost(10, 'hello')).rejects.toBe(InternalServerError)
	})
})
