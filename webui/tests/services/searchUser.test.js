import { describe, it, expect, vi, beforeEach } from 'vitest'
import searchUser from '@/services/searchUser'
import api from '@/services/axios'
import { InternalServerError } from '@/services/apiErrors'

vi.mock('@/services/axios')

describe('searchUser', () => {
	beforeEach(() => vi.clearAllMocks())

	it('returns [] for queries shorter than 3 chars', async () => {
		await expect(searchUser('ab')).resolves.toEqual([])
		await expect(searchUser('  ')).resolves.toEqual([])
		await expect(searchUser(null)).resolves.toEqual([])
		expect(api.get).not.toHaveBeenCalled()
	})

	it('returns data on 200', async () => {
		const data = [{ user_id: 1, username: 'alice' }]
		api.get.mockResolvedValue({ status: 200, data })
		await expect(searchUser('  ali  ')).resolves.toEqual(data)
		expect(api.get).toHaveBeenCalledWith('/users/', { params: { q: 'ali', limit: 10 } })
	})

	it('throws InternalServerError on non-200', async () => {
		api.get.mockResolvedValue({ status: 500 })
		await expect(searchUser('alice')).rejects.toBe(InternalServerError)
	})
})
