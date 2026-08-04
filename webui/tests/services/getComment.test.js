import { describe, it, expect, vi, beforeEach } from 'vitest'
import getComment from '@/services/getComment'
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

describe('getComment', () => {
	beforeEach(() => {
		vi.clearAllMocks()
		vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(1)
		resolveCommentContext.mockResolvedValue({ postId: 10, authorId: 7 })
	})

	it('returns normalized comment on 200', async () => {
		const raw = {
			comment_id: 5,
			author_id: 2,
			pub_time: '2024-01-01',
			content: 'hello',
			like_cnt: 3
		}
		api.get.mockResolvedValue({ status: 200, data: raw })
		await expect(getComment(5)).resolves.toEqual({
			commentID: 5,
			postID: 10,
			author: 2,
			time: '2024-01-01',
			content: 'hello',
			likes: 3
		})
		expect(api.get).toHaveBeenCalledWith('/users/7/posts/10/comments/5')
	})

	it('clears auth and throws BadAuthException on 401', async () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		api.get.mockResolvedValue({ status: 401 })
		await expect(getComment(5)).rejects.toBe(BadAuthException)
		expect(clearAuthSpy).toHaveBeenCalled()
	})

	it('throws CommentNotFoundException on 404', async () => {
		api.get.mockResolvedValue({ status: 404 })
		await expect(getComment(5)).rejects.toBe(CommentNotFoundException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(getComment(5)).rejects.toBe(InternalServerError)
	})
})
