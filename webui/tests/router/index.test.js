import { vi, describe, it, expect } from 'vitest'
import router from '@/router'
import * as loginService from '@/services/login'

describe('router guard', () => {
  it('redirects to /login with a redirect param when not authenticated', async () => {
    vi.spyOn(loginService, 'ensureAuthenticated').mockRejectedValue(new Error('nope'))
    await router.push('/newpost')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
    expect(router.currentRoute.value.query.redirect).toBe('/newpost')
  })

  it('proceeds when authenticated', async () => {
    vi.spyOn(loginService, 'ensureAuthenticated').mockResolvedValue(42)
    await router.push('/newpost')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/newpost')
  })

  it('does not gate public routes', async () => {
    await router.push('/search')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/search')
  })
})