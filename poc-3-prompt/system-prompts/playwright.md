# Playwright TypeScript — Framework-Specific Instructions

## Project Patterns (ai-web-automation)

You follow the Page Object Model structure from the `ai-web-automation` project:

```
tests/
├── pages/           ← Page classes (one per page/component)
├── locators/        ← Object repository (separate locator files)
├── helpers/         ← Shared utilities (auth, data, wait helpers)
├── fixtures/        ← Playwright fixtures (custom test context)
└── specs/           ← Test specs (thin — delegate to pages)
```

## Canonical Patterns

### Page Class Structure
```typescript
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  // Locators defined as properties (self-healing via getByRole/Label)
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput   = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton  = page.getByRole('button', { name: 'Sign in' });
  }

  async navigate() { await this.page.goto('/login'); }
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

### Test Spec Structure
```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Authentication', () => {
  test('should redirect to dashboard after valid login', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login(process.env.TEST_EMAIL!, process.env.TEST_PASSWORD!);
    await expect(page).toHaveURL('/dashboard');
  });
});
```

## Locator Priority Order
1. `getByRole()` — ARIA roles (most resilient)
2. `getByLabel()` — form inputs
3. `getByTestId()` — data-testid attributes
4. `getByText()` — visible text
5. `locator()` with CSS — only as last resort

## NEVER use:
- `page.waitForTimeout(3000)` — use `waitForSelector` or `expect().toBeVisible()`
- `page.$('#id')` — use `page.locator()` or semantic locators
- Hardcoded credentials — use environment variables or test fixtures
