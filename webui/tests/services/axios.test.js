import { describe, it, expect, vi, beforeEach } from 'vitest'

const { responseHandlers } = vi.hoisted(() => ({
	responseHandlers: { onSuccess: null, onError: null }
}))

vi.mock('axios', () => ({
	default: {
		create: vi.fn(() => ({
			interceptors: {
				response: {
					use: vi.fn((onSuccess, onError) => {
						responseHandlers.onSuccess = onSuccess
						responseHandlers.onError = onError
					})
				}
			}
		}))
	}
}))

describe('axios', () => {
	beforeEach(async () => {
		vi.resetModules()
		await import('@/services/axios')
	})

	it('passes through successful responses', () => {
		const response = { status: 200, data: {} }
		expect(responseHandlers.onSuccess(response)).toBe(response)
	})

	it('resolves error responses that include a response object', async () => {
		const errorResponse = { status: 404 }
		await expect(responseHandlers.onError({ response: errorResponse }))
			.resolves.toBe(errorResponse)
	})

	it('rejects errors without a response object', async () => {
		const error = new Error('network')
		await expect(responseHandlers.onError(error)).rejects.toBe(error)
	})
})
