---
name: rtl-bidi-ui-support
metadata:
  category: Localization and Internationalization (i18n)
description: Master right-to-left (RTL) and bidirectional (BiDi) UI design, CSS logical properties (`margin-inline`, `padding-block`), layout direction switching (Arabic, Hebrew, Persian), typography scaling, icon mirroring rules, and automated RTL testing. Trigger when designing or implementing RTL UI support, multi-directional web/mobile layouts, or fixing BiDi rendering bugs.
compatibility: Modern Browsers (Chrome 89+, Safari 14.1+, Firefox 88+), CSS3 Logical Properties, React, Vue, HTML5
---

# RTL & BiDi UI Support Skill Guide

This skill provides standards, CSS logical property mappings, component patterns, icon mirroring rules, and testing strategies for Right-to-Left (RTL) and Bidirectional (BiDi) user interfaces.

---

## 1. Physical vs CSS Logical Properties Mapping

Never use directional physical properties (`left`, `right`). Always use **CSS Logical Properties**:

| Physical Property (Avoid) | CSS Logical Property (Use) | Description |
| :--- | :--- | :--- |
| `margin-left: 16px;` | `margin-inline-start: 16px;` | Spacing before element along reading direction |
| `margin-right: 16px;` | `margin-inline-end: 16px;` | Spacing after element along reading direction |
| `padding-left: 8px;` | `padding-inline-start: 8px;` | Inner padding at start of inline axis |
| `padding-right: 8px;` | `padding-inline-end: 8px;` | Inner padding at end of inline axis |
| `left: 0;` | `inset-inline-start: 0;` | Absolute positioning relative to start edge |
| `right: 0;` | `inset-inline-end: 0;` | Absolute positioning relative to end edge |
| `text-align: left;` | `text-align: start;` | Text alignment matching document direction |
| `text-align: right;` | `text-align: end;` | Text alignment matching opposite direction |
| `border-left: 1px solid;` | `border-inline-start: 1px solid;` | Border on reading start side |

---

## 2. Document Directionality & Tailwind CSS Setup

### A. Dynamic Root Direction Handling

```typescript
// Utility to update document root direction dynamically
export function setDocumentDirection(locale: string): void {
  const RTL_LOCALES = ['ar', 'he', 'fa', 'ur', 'dv'];
  const isRtl = RTL_LOCALES.includes(locale.toLowerCase());
  
  const root = document.documentElement;
  root.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
  root.setAttribute('lang', locale);
}
```

### B. Tailwind CSS RTL Variants

Tailwind CSS v3.0+ supports native `rtl:` and `ltr:` modifier variants and logical utilities:

```html
<!-- Example card utilizing Tailwind logical spacing and RTL variants -->
<div className="ms-4 me-2 p-4 text-start bg-white rounded-lg shadow rtl:bg-slate-900">
  <div className="flex items-center gap-3">
    <!-- Icon automatically flipped in RTL -->
    <svg className="w-5 h-5 rtl:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
    <span>Read More</span>
  </div>
</div>
```

---

## 3. Icon Mirroring Guidelines

Not all icons should be flipped when changing document direction.

```text
+-----------------------------------------------------------------------------------+
| SHOULD BE MIRRORED (rtl:rotate-180 or transform: scaleX(-1))                     |
+-----------------------------------------------------------------------------------+
| - Directional arrows (Back, Forward, Next, Previous)                             |
| - Progress indicators and navigation steps                                       |
| - Media player controls (Play, Rewind, Fast-Forward)                             |
| - Sliders and volume bars                                                        |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
| MUST NOT BE MIRRORED                                                             |
+-----------------------------------------------------------------------------------+
| - Universal objects (Search glass, Lock, Key, Camera, Trash can, Shopping cart)   |
| - Clock faces and time direction                                                 |
| - Brand logos and trademarks                                                     |
| - Slash symbols in file paths (`/`)                                              |
+-----------------------------------------------------------------------------------+
```

---

## 4. BiDi Text Isolation (`<bdi>` & `unicode-bidi`)

When displaying user-generated content (e.g. phone numbers, email addresses, usernames, mixed language strings), wrap them in HTML `<bdi>` elements to prevent directional bleed.

```tsx
import React from 'react';

export const UserCommentItem: React.FC<{ username: string; commentText: string }> = ({
  username,
  commentText,
}) => {
  return (
    <div className="p-3 border-b border-slate-200 text-start">
      {/* <bdi> isolates directionality of the username so mixed Hebrew/English does not spill */}
      <span className="font-semibold me-2">
        <bdi>{username}</bdi>:
      </span>
      <span>
        <bdi>{commentText}</bdi>
      </span>
    </div>
  );
};
```

---

## 5. Automated RTL Visual Regression Testing with Playwright

```typescript
import { test, expect } from '@playwright/test';

test.describe('RTL Layout Verification', () => {
  test('should render dashboard layout correctly in Arabic RTL', async ({ page }) => {
    // Set locale to Arabic and navigate
    await page.goto('/ar/dashboard');

    // Assert root element has dir="rtl"
    const dirAttribute = await page.getAttribute('html', 'dir');
    expect(dirAttribute).toBe('rtl');

    // Take visual snapshot of RTL layout
    await expect(page).toHaveScreenshot('dashboard-rtl-arabic.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });
});
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Visual / Layout Bug | Production Best Practice |
| :--- | :--- | :--- |
| **Using `margin-left` / `margin-right` in CSS** | Layout fails to mirror in RTL mode, causing overlapping text and broken margins. | Always use CSS Logical Properties (`margin-inline-start`, `margin-inline-end`). |
| **Flipping all icons indiscriminately in RTL** | Flips search magnifying glasses or clocks backward, breaking UI conventions. | Only mirror directional navigation icons; leave universal object icons untouched. |
| **Un-isolated inline numbers or mixed text** | Phone numbers (`+1-555-0199`) or codes render mangled (`0199-555-1+`). | Wrap dynamic mixed-language strings in `<bdi>` or apply `dir="ltr"` on numeric codes. |
| **Hardcoding `text-align: left` on form inputs** | Inputs remain left-aligned in Arabic/Hebrew, creating unnatural entry fields. | Use `text-align: start` so alignment adapts automatically to page direction. |
