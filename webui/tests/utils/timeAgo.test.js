import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import timeAgo from '@/utils/timeAgo'

describe('timeAgo', () => {
	beforeEach(() => {
		vi.useFakeTimers()
		vi.setSystemTime(new Date('2024-06-01T12:00:00Z'))
	})

	afterEach(() => {
		vi.useRealTimers()
	})

	it('formats seconds ago', () => {
		const date = new Date('2024-06-01T11:59:30Z')
		expect(timeAgo(date)).toMatch(/30 seconds ago/i)
	})

	it('formats minutes ago', () => {
		const date = new Date('2024-06-01T11:55:00Z')
		expect(timeAgo(date)).toMatch(/5 minutes ago/i)
	})

	it('formats hours ago', () => {
		const date = new Date('2024-06-01T10:00:00Z')
		expect(timeAgo(date)).toMatch(/2 hours ago/i)
	})

	it('formats days ago', () => {
		const date = new Date('2024-05-30T12:00:00Z')
		expect(timeAgo(date)).toMatch(/2 days ago/i)
	})

	it('formats weeks ago', () => {
		const date = new Date('2024-05-18T12:00:00Z')
		expect(timeAgo(date)).toMatch(/2 weeks ago/i)
	})

	it('formats months ago', () => {
		const date = new Date('2024-04-01T12:00:00Z')
		expect(timeAgo(date)).toMatch(/2 months ago/i)
	})

	it('formats years ago', () => {
		const date = new Date('2022-06-01T12:00:00Z')
		expect(timeAgo(date)).toMatch(/2 years ago/i)
	})
})
