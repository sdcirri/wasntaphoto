import { describe, it, expect, vi, beforeEach } from 'vitest'
import logout from '@/services/logout'
import * as loginService from '@/services/login'

describe('logout', () => {
	it('calls clearAuth', () => {
		const clearAuthSpy = vi.spyOn(loginService, 'clearAuth').mockImplementation(() => {})
		logout()
		expect(clearAuthSpy).toHaveBeenCalled()
	})
})
