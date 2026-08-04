import { describe, it, expect, vi, beforeEach } from 'vitest'
import registerAndLogin from '@/services/register'
import api from '@/services/axios'
import login from '@/services/login'
import {
	InternalServerError,
	UsernameAlreadyTakenException,
	WeakPasswordException
} from '@/services/apiErrors'

vi.mock('@/services/axios')
vi.mock('@/services/login', () => ({ default: vi.fn() }))

describe('registerAndLogin', () => {
	beforeEach(() => {
		vi.clearAllMocks()
	})

	it('calls login on 200', async () => {
		api.post.mockResolvedValue({ status: 200 })
		await registerAndLogin('user', 'pass')
		expect(api.post).toHaveBeenCalledWith(
			'/users/',
			{ username: 'user', password: 'pass' },
			{ headers: { 'Content-Type': 'application/json' } }
		)
		expect(login).toHaveBeenCalledWith('user', 'pass')
	})

	it('throws WeakPasswordException on 400', async () => {
		api.post.mockResolvedValue({ status: 400 })
		await expect(registerAndLogin('user', 'pass')).rejects.toBe(WeakPasswordException)
	})

	it('throws UsernameAlreadyTakenException on 409', async () => {
		api.post.mockResolvedValue({ status: 409 })
		await expect(registerAndLogin('user', 'pass')).rejects.toBe(UsernameAlreadyTakenException)
	})

	it('throws InternalServerError on any other status', async () => {
		api.post.mockResolvedValue({ status: 500 })
		await expect(registerAndLogin('user', 'pass')).rejects.toBe(InternalServerError)
	})
})
