import { describe, it, expect, vi, beforeEach } from 'vitest'

const { mockApi } = vi.hoisted(() => ({
	mockApi: {
		get: vi.fn(),
		post: vi.fn(),
		delete: vi.fn()
	}
}))

vi.mock('@/services/axios', () => ({ default: mockApi }))

describe('login', () => {
	let loginModule
	let apiErrors

	beforeEach(async () => {
		vi.resetModules()
		mockApi.get.mockReset()
		mockApi.post.mockReset()
		mockApi.delete.mockReset()
		mockApi.get.mockResolvedValue({ status: 401 })
		loginModule = await import('@/services/login')
		apiErrors = await import('@/services/apiErrors')
	})

	it('login succeeds and fetches user id', async () => {
		mockApi.post.mockResolvedValue({ status: 200 })
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 42 } })
		await expect(loginModule.default('user', 'pass')).resolves.toBe(42)
		expect(mockApi.post).toHaveBeenCalledWith(
			'/session/',
			{ username: 'user', password: 'pass' },
			{ headers: { 'Content-Type': 'application/json' } }
		)
	})

	it('throws FailedLoginException on 403', async () => {
		mockApi.post.mockResolvedValue({ status: 403 })
		await expect(loginModule.default('user', 'pass')).rejects.toBe(apiErrors.FailedLoginException)
	})

	it('throws FailedLoginException on 422', async () => {
		mockApi.post.mockResolvedValue({ status: 422 })
		await expect(loginModule.default('user', 'pass')).rejects.toBe(apiErrors.FailedLoginException)
	})

	it('throws InternalServerError on unknown login status', async () => {
		mockApi.post.mockResolvedValue({ status: 500 })
		await expect(loginModule.default('user', 'pass')).rejects.toBe(apiErrors.InternalServerError)
	})

	it('currentUserId returns cached value without API call', async () => {
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 7 } })
		await loginModule.currentUserId()
		mockApi.get.mockClear()
		await expect(loginModule.currentUserId()).resolves.toBe(7)
		expect(mockApi.get).not.toHaveBeenCalled()
	})

	it('currentUserId force refetches', async () => {
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 7 } })
		await loginModule.currentUserId()
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 8 } })
		await expect(loginModule.currentUserId(true)).resolves.toBe(8)
	})

	it('currentUserId clears auth and returns null on 401', async () => {
		mockApi.get.mockResolvedValue({ status: 401 })
		await expect(loginModule.currentUserId()).resolves.toBeNull()
		expect(loginModule.getCachedUserId()).toBeNull()
	})

	it('currentUserId throws InternalServerError on unknown status', async () => {
		mockApi.get.mockResolvedValue({ status: 500 })
		await expect(loginModule.currentUserId()).rejects.toBe(apiErrors.InternalServerError)
	})

	it('deduplicates concurrent currentUserId calls', async () => {
		mockApi.get.mockClear()
		let resolveGet
		mockApi.get.mockReturnValue(new Promise(resolve => {
			resolveGet = resolve
		}))
		const p1 = loginModule.currentUserId()
		const p2 = loginModule.currentUserId()
		resolveGet({ status: 200, data: { user_id: 7 } })
		await expect(Promise.all([p1, p2])).resolves.toEqual([7, 7])
		expect(mockApi.get).toHaveBeenCalledTimes(1)
	})

	it('ensureAuthenticated returns user id when logged in', async () => {
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 7 } })
		await expect(loginModule.ensureAuthenticated()).resolves.toBe(7)
	})

	it('ensureAuthenticated throws BadAuthException when not logged in', async () => {
		mockApi.get.mockResolvedValue({ status: 401 })
		await expect(loginModule.ensureAuthenticated()).rejects.toBe(apiErrors.BadAuthException)
	})

	it('clearAuth deletes session when user was cached', async () => {
		mockApi.get.mockResolvedValue({ status: 200, data: { user_id: 7 } })
		await loginModule.currentUserId()
		loginModule.clearAuth()
		expect(mockApi.delete).toHaveBeenCalledWith('/session/current')
		expect(loginModule.getCachedUserId()).toBeNull()
	})

	it('clearAuth skips session delete when no user was cached', () => {
		loginModule.clearAuth()
		expect(mockApi.delete).not.toHaveBeenCalled()
		expect(loginModule.getCachedUserId()).toBeNull()
	})
})
