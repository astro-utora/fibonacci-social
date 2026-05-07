import { test, expect } from '@playwright/test'
import { loginAsAdmin, loginAsUser } from './helpers'

test.describe('Role Tree Feature', () => {
  test.describe('Admin Panel', () => {
    test('should allow admin to view and edit role tree', async ({ page }) => {
      await loginAsAdmin(page)
      await page.goto('/admin/role-tree')

      // Check if JSON editor is present
      const editor = await page.locator('textarea[label="Role Tree JSON"]')
      expect(await editor.isVisible()).toBeTruthy()

      // Test JSON validation
      await editor.fill('invalid json')
      const errorMessage = await page.locator('.v-messages__message')
      expect(await errorMessage.textContent()).toContain('Invalid JSON format')

      // Test valid JSON
      const validJson = JSON.stringify({
        role: 'Test Org',
        subroles: [
          {
            role: 'Test Role',
            filloutId: 'test-form',
            subroles: []
          }
        ]
      }, null, 2)

      await editor.fill(validJson)
      await page.locator('button:has-text("Save Role Tree")').click()
      
      // Check if preview updates
      const previewRole = await page.locator('.role-tree-preview .v-card-title')
      expect(await previewRole.textContent()).toContain('Test Org')
    })

    test('should show role tree statistics', async ({ page }) => {
      await loginAsAdmin(page)
      await page.goto('/admin/role-tree/stats')

      const statsTable = await page.locator('.v-data-table')
      expect(await statsTable.isVisible()).toBeTruthy()

      // Check table headers
      const headers = await page.locator('.v-data-table-header th')
      expect(await headers.count()).toBe(3) // Role, Submissions, Unique Users
    })
  })

  test.describe('User Dashboard', () => {
    test('should show role tree with collapsible sections', async ({ page }) => {
      await loginAsUser(page)
      await page.goto('/dashboard')

      // Check initial state
      const roleTree = await page.locator('.role-tree')
      expect(await roleTree.isVisible()).toBeTruthy()

      // Click a role
      await page.locator('.role-tree .v-card').first().click()
      
      // Check if it's selected
      const selectedRole = await page.locator('.selected-role')
      expect(await selectedRole.isVisible()).toBeTruthy()

      // Check subroles list
      const subrolesList = await page.locator('.subrole-names')
      expect(await subrolesList.isVisible()).toBeTruthy()

      // Click expand button
      await page.locator('button:has-text("Show Full Tree")').click()
      
      // Check expanded state
      const expandedSubroles = await page.locator('.subroles-expanded')
      expect(await expandedSubroles.isVisible()).toBeTruthy()
    })

    test('should show fillout form when selecting role with filloutId', async ({ page }) => {
      await loginAsUser(page)
      await page.goto('/dashboard')

      // Find and click a role with filloutId
      const roles = await page.locator('.role-tree .v-card')
      const roleWithForm = await roles.filter({
        has: page.locator('.mdi-form-select')
      })
      await roleWithForm.first().click()

      // Check if fillout form appears
      const filloutForm = await page.locator('[data-fillout-embed-type="standard"]')
      expect(await filloutForm.isVisible()).toBeTruthy()
    })
  })
}) 