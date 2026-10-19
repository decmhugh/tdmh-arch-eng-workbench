---
parent: Decisions
nav_order: 18
title: ADR-0018 Frontend Technology Standards
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0018: Frontend Technology Standards

## Status

**Draft**

## Context and Problem Statement

ACP will have user-facing components (ui-management-console, ui-advanced-features). We need to standardize on frontend technologies to ensure consistency, maintainability, and ability to share components across projects.

## Decision Drivers

* Team familiarity and skills availability
* Enterprise support and long-term viability
* Performance and bundle size concerns
* Component reusability across UI projects
* Accessibility compliance requirements
* Server-side rendering for SEO/performance

## Decision Outcome

### Primary Stack

| Category | Technology | Rationale |
|----------|------------|-----------|
| **Framework** | Next.js 14+ | App Router, RSC, Vercel support |
| **UI Library** | React 18+ | Industry standard, team familiarity |
| **Language** | TypeScript 5+ | Type safety, tooling support |
| **Styling** | Tailwind CSS | Utility-first, consistent design |
| **Component Library** | shadcn/ui | Accessible, customizable, not a dependency |
| **State Management** | React Query + Zustand | Server state (TanStack Query) + client state |
| **Testing** | Playwright + Vitest | E2E + unit testing |

### Required Standards

#### TypeScript Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "moduleResolution": "bundler",
    "target": "ES2022"
  }
}
```

#### Accessibility

- WCAG 2.1 AA compliance required
- Automated axe-core testing in CI
- Manual keyboard navigation testing
- Screen reader testing (NVDA, VoiceOver)

#### Performance Budgets

| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| FID | < 100ms |
| CLS | < 0.1 |
| Bundle size (initial) | < 200KB gzipped |

#### Folder Structure

```
src/
├── app/                  # Next.js App Router pages
├── components/
│   ├── ui/              # shadcn/ui components
│   └── features/        # Feature-specific components
├── lib/                 # Utilities, API clients
├── hooks/               # Custom hooks
├── stores/              # Zustand stores
└── types/               # TypeScript types
```

### Prohibited Patterns

- No `any` types without explicit justification
- No inline styles (use Tailwind utilities)
- No direct DOM manipulation (use React patterns)
- No class components (use functional + hooks)

## Consequences

**Good:**
* Consistent developer experience across UI projects
* Leverages team existing React/TypeScript skills
* Modern patterns (RSC, streaming) for performance

**Bad:**
* Learning curve for Next.js App Router
* Vercel lock-in for optimal deployment (can use other platforms)

## More Information

* Related: ADR-0017 (Testing Strategy)
* Related: ADR-0021 (Scalability Requirements)
* See: [Next.js Documentation](https://nextjs.org/docs)
