import { PlaywrightTestConfig } from '@playwright/test'
import baseConfig from './playwright.config'

const config: PlaywrightTestConfig = {
  ...baseConfig,
  timeout: 60000,
  workers: 1,
  use: {
    ...baseConfig.use,
    trace: 'on',
    video: 'on',
    screenshot: 'on',
  },
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/test-results.json' }]
  ],
}

export default config 