---
name: i18next-localization-workflow
metadata:
  category: Localization and Internationalization (i18n)
description: Implement production-grade i18next localization workflows, dynamic locale switching, ICU message syntax formatting, fallback strategies, namespaces, and automated translation extraction. Trigger when configuring internationalization (i18n) in React/Next.js/Vue applications or setting up localization workflows.
compatibility: Node.js 18+, i18next 23+, react-i18next, next-i18next, TypeScript
---

# i18next Localization Workflow Skill Guide

This skill provides architecture standards, directory layouts, configuration patterns, and extraction workflows for building multi-locale applications using i18next.

---

## 1. Locales Directory & Namespace Architecture

Organize locale dictionaries logically by language tag and domain namespaces:

```text
public/
└── locales/
    ├── en/
    │   ├── common.json        # Shared UI elements (buttons, navigation, footers)
    │   ├── auth.json          # Authentication forms and error messages
    │   └── dashboard.json     # Dashboard metrics and reports
    ├── ar/                    # Arabic translations
    │   ├── common.json
    │   ├── auth.json
    │   └── dashboard.json
    └── fr/                    # French translations
        ├── common.json
        ├── auth.json
        └── dashboard.json
src/
├── lib/
│   └── i18n.ts                # i18next core client initialization
└── i18next-parser.config.js   # Automated translation extractor config
```

---

## 2. i18next Initialization Configuration (`src/lib/i18n.ts`)

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpApi from 'i18next-http-backend';

export const SUPPORTED_LOCALES = ['en', 'ar', 'fr', 'es'] as const;
export type SupportedLocale = typeof SUPPORTED_LOCALES[number];

i18n
  .use(HttpApi)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: SUPPORTED_LOCALES,
    defaultNS: 'common',
    ns: ['common', 'auth', 'dashboard'],
    
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // React handles XSS escaping natively
    },
    
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    detection: {
      order: ['cookie', 'htmlTag', 'navigator', 'path'],
      caches: ['cookie'],
      cookieMinutes: 60 * 24 * 365, // 1 year
    },
  });

export default i18n;
```

---

## 3. Translation Dictionary Files (`public/locales/en/auth.json`)

Enforce ICU message syntax for plurals, interpolation, and gender/context:

```json
{
  "welcome_user": "Welcome back, {{name}}!",
  "items_count_one": "You have {{count}} item in your cart.",
  "items_count_other": "You have {{count}} items in your cart.",
  "last_login_date": "Last login was on {{val, datetime}}",
  "status_message": "User status is {{context}}"
}
```

---

## 4. React Component Usage & Dynamic Switching

```tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

export const UserWelcomeBanner: React.FC<{ userName: string; cartCount: number }> = ({
  userName,
  cartCount,
}) => {
  const { t, i18n } = useTranslation('auth');

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    // Update HTML dir attribute for RTL support if needed
    document.documentElement.dir = lng === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lng;
  };

  return (
    <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-800">
      <h2 className="text-xl font-bold">{t('welcome_user', { name: userName })}</h2>
      <p>{t('items_count', { count: cartCount })}</p>

      <div className="mt-4 flex gap-2">
        <button onClick={() => changeLanguage('en')} className="px-3 py-1 bg-blue-500 text-white rounded">
          English
        </button>
        <button onClick={() => changeLanguage('ar')} className="px-3 py-1 bg-green-500 text-white rounded">
          العربية
        </button>
      </div>
    </div>
  );
};
```

---

## 5. Automated Translation Extraction (`i18next-parser.config.js`)

Automate extraction of `t('key')` tokens from TypeScript source code into JSON files:

```javascript
module.exports = {
  contextSeparator: '_',
  createOldCatalogs: false,
  defaultNamespace: 'common',
  defaultValue: '',
  indentation: 2,
  lexers: {
    ts: ['JsxLexer'],
    tsx: ['JsxLexer'],
    default: ['JsxLexer'],
  },
  locales: ['en', 'ar', 'fr'],
  output: 'public/locales/$LOCALE/$NAMESPACE.json',
  input: ['src/**/*.{ts,tsx}'],
  sort: true,
};
```

Run extraction via CLI:

```bash
npx i18next
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Localization Bug | Production Best Practice |
| :--- | :--- | :--- |
| **String concatenation (`t('welcome') + ' ' + userName`)** | Fails in languages with different word orders (e.g. Arabic, Japanese). | Use variable interpolation (`t('welcome_user', { name: userName })`). |
| **Using hardcoded plural logic (`count === 1 ? 'item' : 'items'`)** | Fails in languages with complex plural rules (Arabic has 6 plural forms). | Use i18next plural keys (`_one`, `_zero`, `_two`, `_few`, `_many`, `_other`). |
| **Storing all translations in a single monolithic JSON file** | Slows initial page load due to large bundle sizes. | Split translations into logical namespaces (`common`, `auth`, `dashboard`). |
| **Hardcoding date, currency, or number formats manually** | Violates locale conventions across different countries. | Format dates and numbers using native `Intl` APIs or i18next formatters. |
