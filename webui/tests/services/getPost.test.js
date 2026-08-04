import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockApi, mockEnsureAuthenticated, mockClearAuth } = vi.hoisted(() => ({
	mockApi: {
		get: vi.fn(),
		post: vi.fn(),
		put: vi.fn(),
		delete: vi.fn()
	},
	mockEnsureAuthenticated: vi.fn(),
	mockClearAuth: vi.fn()
}))

vi.mock('@/services/axios', () => ({ default: mockApi }))
vi.mock('@/services/login', () => ({
	ensureAuthenticated: mockEnsureAuthenticated,
	clearAuth: mockClearAuth
}))

describe('getPost', () => {
	let getPostModule
	let apiErrors

	beforeEach(async () => {
		vi.resetModules()
		mockApi.get.mockReset()
		mockEnsureAuthenticated.mockReset()
		mockClearAuth.mockReset()
		mockEnsureAuthenticated.mockResolvedValue(1)
		getPostModule = await import('@/services/getPost')
		apiErrors = await import('@/services/apiErrors')
	})

	describe('cache helpers', () => {
		it('cacheAuthorPosts ignores invalid author and post ids', async () => {
			const { cacheAuthorPosts, resolvePostAuthorId } = getPostModule
			cacheAuthorPosts('bad', ['also-bad'])
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [] })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('cacheAuthorPosts skips invalid post ids in list', async () => {
			const { cacheAuthorPosts, resolvePostAuthorId } = getPostModule
			cacheAuthorPosts(7, [10, 'bad'])
			await expect(resolvePostAuthorId(10)).resolves.toBe(7)
		})

		it('cacheCommentIds ignores invalid post and comment ids', async () => {
			const { cacheCommentIds, resolveCommentContext } = getPostModule
			cacheCommentIds('bad', ['also-bad'])
			await expect(resolveCommentContext(1)).rejects.toBe(apiErrors.CommentNotFoundException)
		})

		it('cacheCommentIds skips invalid comment ids in list', async () => {
			const { cacheAuthorPosts, cacheCommentIds, resolveCommentContext } = getPostModule
			cacheAuthorPosts(7, [10])
			cacheCommentIds(10, [5, 'bad'])
			await expect(resolveCommentContext(5)).resolves.toEqual({ postId: 10, authorId: 7 })
		})

		it('cachePostPayload ignores posts with missing ids', async () => {
			const { cachePostPayload, resolvePostAuthorId } = getPostModule
			cachePostPayload({ post_id: 1 })
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [] })
			await expect(resolvePostAuthorId(1)).rejects.toBe(apiErrors.PostNotFoundException)
		})
	})

	describe('normalizePost', () => {
		it('maps API shape to UI shape', () => {
			const { normalizePost } = getPostModule
			expect(normalizePost({
				post_id: 1,
				author_id: 2,
				pub_time: '2024-01-01',
				image: 'b64',
				caption: 'hi',
				like_cnt: 5,
				comments: [3]
			})).toEqual({
				postID: 1,
				author: 2,
				pubTime: '2024-01-01',
				imageB64: 'b64',
				caption: 'hi',
				likeCount: 5,
				comments: [3]
			})
		})

		it('defaults missing caption and comments', () => {
			const { normalizePost } = getPostModule
			const result = normalizePost({
				post_id: 1,
				author_id: 2,
				pub_time: 't',
				image: 'img',
				like_cnt: 0
			})
			expect(result.caption).toBe('')
			expect(result.comments).toEqual([])
		})
	})

	describe('resolvePostAuthorId', () => {
		it('throws PostNotFoundException for invalid id', async () => {
			const { resolvePostAuthorId } = getPostModule
			await expect(resolvePostAuthorId('bad')).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('returns cached author id without API call', async () => {
			const { cacheAuthorPosts, resolvePostAuthorId } = getPostModule
			cacheAuthorPosts(7, [10])
			await expect(resolvePostAuthorId(10)).resolves.toBe(7)
			expect(mockApi.get).not.toHaveBeenCalled()
		})

		it('refreshes cache and finds author', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [10] })
			await expect(resolvePostAuthorId(10)).resolves.toBe(1)
		})

		it('throws PostNotFoundException when post not in cache after refresh', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [] })
			await expect(resolvePostAuthorId(99)).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('clears auth and throws BadAuthException when refresh gets 401', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get.mockResolvedValue({ status: 401 })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.BadAuthException)
			expect(mockClearAuth).toHaveBeenCalled()
		})

		it('clears auth when author post lists return 401 during refresh', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 401 })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.BadAuthException)
			expect(mockClearAuth).toHaveBeenCalled()
		})

		it('throws InternalServerError when author post lists fail during refresh', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 500 })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.InternalServerError)
		})

		it('ignores 404 on author post lists during refresh', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 404 })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('ignores 403 on author post lists during refresh', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [2] })
				.mockResolvedValueOnce({ status: 403 })
				.mockResolvedValueOnce({ status: 200, data: [10] })
			await expect(resolvePostAuthorId(10)).resolves.toBe(2)
		})

		it('throws InternalServerError when refresh gets unknown status', async () => {
			const { resolvePostAuthorId } = getPostModule
			mockApi.get.mockResolvedValue({ status: 500 })
			await expect(resolvePostAuthorId(10)).rejects.toBe(apiErrors.InternalServerError)
		})

		it('refresh=true bypasses stale cache entry', async () => {
			const { cacheAuthorPosts, resolvePostAuthorId } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [10] })
			await expect(resolvePostAuthorId(10, true)).resolves.toBe(1)
		})
	})

	describe('resolveCommentContext', () => {
		it('throws CommentNotFoundException for invalid comment id', async () => {
			const { resolveCommentContext } = getPostModule
			await expect(resolveCommentContext('bad')).rejects.toBe(apiErrors.CommentNotFoundException)
		})

		it('throws CommentNotFoundException when comment not cached', async () => {
			const { resolveCommentContext } = getPostModule
			await expect(resolveCommentContext(99)).rejects.toBe(apiErrors.CommentNotFoundException)
		})

		it('returns post and author ids from cache', async () => {
			const { cacheAuthorPosts, cacheCommentIds, resolveCommentContext } = getPostModule
			cacheAuthorPosts(7, [10])
			cacheCommentIds(10, [5])
			await expect(resolveCommentContext(5)).resolves.toEqual({ postId: 10, authorId: 7 })
		})
	})

	describe('default export', () => {
		it('returns normalized post on 200', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			const raw = {
				post_id: 10,
				author_id: 7,
				pub_time: '2024-01-01',
				image: 'img',
				caption: 'c',
				like_cnt: 1,
				comments: []
			}
			mockApi.get.mockResolvedValue({ status: 200, data: raw })
			await expect(getPost(10)).resolves.toEqual({
				postID: 10,
				author: 7,
				pubTime: '2024-01-01',
				imageB64: 'img',
				caption: 'c',
				likeCount: 1,
				comments: []
			})
		})

		it('retries with refresh on 404', async () => {
			const getPost = getPostModule.default
			mockApi.get
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [10] })
				.mockResolvedValueOnce({ status: 404 })
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [10] })
				.mockResolvedValueOnce({
					status: 200,
					data: {
						post_id: 10,
						author_id: 1,
						pub_time: 't',
						image: 'img',
						like_cnt: 0
					}
				})
			await expect(getPost(10)).resolves.toMatchObject({ postID: 10 })
		})

		it('clears auth and throws BadAuthException on 401', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get.mockResolvedValue({ status: 401 })
			await expect(getPost(10)).rejects.toBe(apiErrors.BadAuthException)
			expect(mockClearAuth).toHaveBeenCalled()
		})

		it('throws BlockedException on 403', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get.mockResolvedValue({ status: 403 })
			await expect(getPost(10)).rejects.toBe(apiErrors.BlockedException)
		})

		it('throws PostNotFoundException on 404 after retry', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get
				.mockResolvedValueOnce({ status: 404 })
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 404 })
			await expect(getPost(10)).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('throws PostNotFoundException when retry fetch still returns 404', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get
				.mockResolvedValueOnce({ status: 404 })
				.mockResolvedValueOnce({ status: 200, data: [] })
				.mockResolvedValueOnce({ status: 200, data: [10] })
				.mockResolvedValueOnce({ status: 404 })
			await expect(getPost(10)).rejects.toBe(apiErrors.PostNotFoundException)
		})

		it('throws InternalServerError on unknown status', async () => {
			const getPost = getPostModule.default
			const { cacheAuthorPosts } = getPostModule
			cacheAuthorPosts(7, [10])
			mockApi.get.mockResolvedValue({ status: 500 })
			await expect(getPost(10)).rejects.toBe(apiErrors.InternalServerError)
		})
	})
})
