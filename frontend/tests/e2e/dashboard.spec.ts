import { test, expect } from '@playwright/test'
import { loginAsUser } from './helpers'

// Move test.use() to top level
test.use({
  trace: 'retain-on-failure',
})

test.describe('Dashboard', () => {
  test('should display user profile data', async ({ page }) => {
    await loginAsUser(page)
    await page.goto('/dashboard')

    // Wait for profile data to load
    await page.waitForSelector('.v-card-title:has-text("Your Profile")')

    // Take screenshot of the profile section for debugging
    await page.locator('.v-card:has-text("Your Profile")').screenshot({
      path: 'test-results/profile-section.png'
    })

    // Check profile fields visibility
    const profileFields = [
      'name',
      'location',
      'workplace',
      'birth_date',
      'goals',
      'education',
      'referral_code'
    ]

    for (const field of profileFields) {
      const fieldElement = await page.locator(`[data-test="profile-${field}"]`)
      await expect(fieldElement).toBeVisible()
      
      // Log the field value
      const value = await fieldElement.textContent()
      console.log(`${field}: ${value}`)
    }
  })

  test('should display user roles', async ({ page }) => {
    await loginAsUser(page)
    await page.goto('/dashboard')

    // Wait for roles section to load
    await page.waitForSelector('.v-card-title:has-text("Your Roles")')

    // Take screenshot of the roles section
    await page.locator('.v-card:has-text("Your Roles")').screenshot({
      path: 'test-results/roles-section.png'
    })

    // Check if role chips are visible
    const roleChips = await page.locator('.v-chip')
    const count = await roleChips.count()
    expect(count).toBeGreaterThan(0)

    // Log all roles
    for (let i = 0; i < count; i++) {
      const roleText = await roleChips.nth(i).textContent()
      console.log(`Role ${i + 1}: ${roleText}`)
    }
  })

  test('should display role tree', async ({ page }) => {
    await loginAsUser(page)
    await page.goto('/dashboard')

    // Wait for role tree to load
    await page.waitForSelector('.v-card-title:has-text("Your Role Tree")')

    // Take screenshot of the role tree section
    await page.locator('.v-card:has-text("Your Role Tree")').screenshot({
      path: 'test-results/role-tree-section.png'
    })

    // Check if role tree is visible
    const roleTree = await page.locator('.role-tree')
    await expect(roleTree).toBeVisible()

    // Log the structure
    const roles = await page.locator('.role-tree .v-card-title').allTextContents()
    console.log('Role Tree Structure:', roles)
  })
}) 