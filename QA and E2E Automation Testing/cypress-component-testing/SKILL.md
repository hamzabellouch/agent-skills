---
name: cypress-component-testing
metadata:
  category: QA and E2E Automation Testing
description: Master Cypress component testing, React/Vue/Svelte mounting, component isolation, custom command creation, network stubbing, and visual snapshot assertions. Trigger when building or testing isolated UI components with Cypress Component Testing (CT).
compatibility: Node.js 18+, Cypress 12.0+, React / Vue / Svelte, Vite / Webpack
---

# Cypress Component Testing Skill Guide

This skill provides production standards, configuration structures, and execution practices for testing isolated UI components using Cypress Component Testing.

---

## 1. Directory Structure & Architecture

Organize component tests alongside component source files or in dedicated `cypress/component/` hierarchies:

```text
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   └── Button.cy.tsx          # Component test specification
│   └── UserCard/
│       ├── UserCard.tsx
│       └── UserCard.cy.tsx
cypress/
├── config/
│   └── cypress.config.ts          # Cypress configuration file
└── support/
    ├── component.ts               # Global component test setup & imports
    ├── component-index.html       # HTML template container for mounted components
    └── commands.ts                # Custom Cypress commands
```

---

## 2. Configuration Standard (`cypress.config.ts` & `support/component.ts`)

### A. Cypress Configuration (`cypress.config.ts`)

```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,ts,jsx,tsx}',
    supportFile: 'cypress/support/component.ts',
    indexHtmlFile: 'cypress/support/component-index.html',
    viewportWidth: 1024,
    viewportHeight: 768,
    video: false,
    screenshotOnRunFailure: true,
  },
});
```

### B. Support Setup (`cypress/support/component.ts`)

```typescript
import './commands';
import { mount } from 'cypress/react18';
import '../../src/styles/globals.css'; // Import global CSS styles

// Declare custom mount command type for TypeScript autocomplete
declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount;
    }
  }
}

Cypress.Commands.add('mount', mount);
```

---

## 3. Component Spec Implementation Examples

### A. Testing React Button Component (`Button.cy.tsx`)

```tsx
import React from 'react';
import { Button } from './Button';

describe('<Button /> Component', () => {
  it('renders with correct default label and variant styling', () => {
    cy.mount(<Button variant="primary">Click Me</Button>);
    
    cy.get('button')
      .should('be.visible')
      .and('have.text', 'Click Me')
      .and('have.class', 'bg-blue-600');
  });

  it('triggers onClick handler when clicked', () => {
    const onClickSpy = cy.spy().as('onClickSpy');
    
    cy.mount(<Button onClick={onClickSpy}>Submit</Button>);
    cy.get('button').click();
    
    cy.get('@onClickSpy').should('have.been.calledOnce');
  });

  it('disables interactions when disabled prop is set', () => {
    const onClickSpy = cy.spy().as('onClickSpy');
    
    cy.mount(<Button disabled onClick={onClickSpy}>Disabled</Button>);
    
    cy.get('button')
      .should('be.disabled')
      .and('have.attr', 'aria-disabled', 'true');
      
    cy.get('@onClickSpy').should('not.have.been.called');
  });
});
```

### B. Component Test with Network Interception (`UserCard.cy.tsx`)

```tsx
import React from 'react';
import { UserCard } from './UserCard';

describe('<UserCard /> Component', () => {
  it('displays loading state and fetches user data', () => {
    // Intercept component-level fetch request
    cy.intercept('GET', '/api/users/usr_100', {
      statusCode: 200,
      body: {
        id: 'usr_100',
        name: 'Jane Doe',
        role: 'Administrator',
        avatarUrl: 'https://example.com/avatar.png',
      },
    }).as('getUser');

    cy.mount(<UserCard userId="usr_100" />);

    // Assert initial loading indicator
    cy.get('[data-testid="skeleton-loader"]').should('be.visible');

    // Wait for network request to resolve and verify UI update
    cy.wait('@getUser');
    cy.get('[data-testid="user-name"]').should('have.text', 'Jane Doe');
    cy.get('[data-testid="user-role"]').should('have.text', 'Administrator');
  });
});
```

---

## 4. Execution Commands

```bash
# Run component tests headlessly in CI mode
npx cypress run --component

# Run component tests targeting a specific browser
npx cypress run --component --browser chrome

# Launch interactive Cypress Component Test runner UI
npx cypress open --component
```

---

## 5. Anti-Patterns & Best Practices

| Anti-Pattern | Operational Failure | Production Best Practice |
| :--- | :--- | :--- |
| **Testing full pages with Component Testing** | Bypasses actual page routing and integration layers. | Use Cypress CT for individual components; use Playwright/Cypress E2E for full pages. |
| **Omitting CSS imports in `component.ts`** | Components render without styles, causing layout bugs in snapshots. | Import global CSS, Tailwind, or theme providers in `cypress/support/component.ts`. |
| **Using `cy.wait(1000)` instead of aliases** | Creates non-deterministic race conditions and test flakiness. | Use `cy.intercept().as('alias')` and wait for `cy.wait('@alias')`. |
| **Relying on implementation details (`.parent().children().eq(2)`)** | Spec fails whenever internal markup changes despite identical behavior. | Query using accessibility roles, text content, or explicit `data-testid` attributes. |
