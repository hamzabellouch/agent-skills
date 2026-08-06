---
name: playwright-e2e-automation
metadata:
  category: QA and E2E Automation Testing
description: Master enterprise Playwright end-to-end (E2E) automation, Page Object Model (POM) architecture, cross-browser testing, network mocking, visual regression testing, and CI pipeline integrations. Trigger when writing Playwright tests, automating web UI E2E flows, or configuring Playwright CI/CD test runners.
compatibility: Node.js 18+, @playwright/test 1.35+, Chromium, Firefox, WebKit
---

# Playwright E2E Automation Skill Guide

This skill provides production standards, design patterns, and test harness setups for building resilient end-to-end (E2E) test suites with Playwright.

---

## 1. Test Architecture & Directory Layout

Structure Playwright test suites using the **Page Object Model (POM)** and custom test fixtures:

```text
e2e-tests/
├── playwright.config.ts    # Global configuration, browser matrix, CI settings
├── fixtures/
│   └── test-fixtures.ts   # Custom Playwright fixtures (auth, page objects)
├── pages/
│   ├── base.page.ts       # Shared base page class with common assertions
│   ├── login.page.ts      # Login page object
│   └── dashboard.page.ts  # Dashboard page object
├── tests/
│   ├── auth/
│   │   └── login.spec.ts  # Authentication E2E test specs
│   └── dashboard/
│       └── analytics.spec.ts
└── .auth/
    └── user.json          # Cached storageState for authenticated sessions
```

---

## 2. Configuration Standard (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['github'],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },
  projects: [
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

---

## 3. Page Object Model (POM) Implementation

### A. Base Page Class (`pages/base.page.ts`)

```typescript
import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async waitForPageLoaded(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle');
  }

  async verifyHeading(text: string | RegExp): Promise<void> {
    const heading = this.page.getByRole('heading', { level: 1 });
    await expect(heading).toHaveText(text);
  }
}
```

### B. Login Page Object (`pages/login.page.ts`)

```typescript
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email address');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto(): Promise<void> {
    await this.page.goto('/login');
    await this.waitForPageLoaded();
  }

  async login(email: string, pass: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(pass);
    await this.submitButton.click();
  }

  async assertErrorMessage(message: string): Promise<void> {
    await expect(this.errorMessage).toBeVisible();
    await expect(this.errorMessage).toContainText(message);
  }
}
```

---

## 4. Test Specifications & Network Interception

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

test.describe('Authentication E2E Flow', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('should display error on invalid credentials', async () => {
    await loginPage.login('invalid@example.com', 'wrongpassword');
    await loginPage.assertErrorMessage('Invalid email or password');
  });

  test('should mock backend API response for success flow', async ({ page }) => {
    // Intercept network call and return mock payload
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ token: 'mock-jwt-token', user: { id: 'usr_123' } }),
      });
    });

    await loginPage.login('user@example.com', 'ValidPass123!');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should pass visual regression snapshot check', async ({ page }) => {
    await expect(page).toHaveScreenshot('login-page.png', {
      maxDiffPixelRatio: 0.01,
    });
  });
});
```

---

## 5. Execution Commands & Reporting

```bash
# Execute all tests across configured browsers
npx playwright test

# Run tests in interactive UI Mode for debugging
npx playwright test --ui

# Run specific spec file on a single browser engine
npx playwright test tests/auth/login.spec.ts --project=chromium

# Debug failing test step-by-step with Playwright Inspector
npx playwright test --debug

# View generated HTML test execution report
npx playwright show-report
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Test Flakiness / Failure | Production Best Practice |
| :--- | :--- | :--- |
| **Using hardcoded delays (`page.waitForTimeout(3000)`)** | Leads to slow, fragile tests that fail under loaded CI runtimes. | Rely on Playwright auto-waiting and locator assertions (`expect(locator).toBeVisible()`). |
| **Locating elements via CSS classes or XPath (`div > span.btn-2`)** | Fragile selectors break whenever CSS layout or refactoring occurs. | Use user-visible aria locators (`getByRole`, `getByLabel`, `getByText`). |
| **Re-authenticating via UI in every test spec** | Dramatically slows execution time across large suites. | Authenticate once in `global.setup.ts` and save state to `storageState: '.auth/user.json'`. |
| **Not running tests in parallel in CI** | CI execution bottlenecking release pipelines. | Set `fullyParallel: true` and scale workers dynamically via CI runner CPU counts. |
