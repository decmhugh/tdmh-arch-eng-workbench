---
parent: Decisions
nav_order: 17
title: ADR-0017 Testing Strategy Standards
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0017: Testing Strategy Standards

## Status

**Draft**

## Context and Problem Statement

As ACP components move from D0 (Discovery) to D2 (Design), each component needs a consistent testing strategy. Without standards, teams may have inconsistent coverage, different tooling, and varying quality gates.

This ADR defines testing standards that apply to:
1. **This repository** (`acp-specs`) — validation of documentation artifacts
2. **Future component repositories** — testing strategy requirements for D2 designs

## Decision Drivers

* Need consistent quality across all ACP components
* D2 designs must include testing strategy per process documentation
* Automation of validation in CI/CD pipelines
* Alignment with CCoE quality standards

## Decision Outcome

### For acp-specs Repository

Since this is a documentation/spec repository (not code), testing focuses on validation:

| Test Type | Purpose | Tool |
|-----------|---------|------|
| Spec validation | Required sections present | `acp validate specs` |
| ADR validation | MADR template compliance | `acp validate adrs` |
| Frontmatter validation | Schema compliance | `acp validate frontmatter` |
| TechDocs build | Rendering without errors | `mkdocs build --strict` |
| Link checking | No broken links | markdownlint / lychee |

### For Component Repositories

All D2 design documents must include a Testing Strategy section covering:

| Layer | Test Type | Coverage Target | Required |
|-------|-----------|-----------------|----------|
| Unit | Function/method level | ≥80% line coverage | Yes |
| Integration | Service/API level | Critical paths | Yes |
| Contract | API schema validation | All endpoints | Yes |
| E2E | User journey | Happy paths | Recommended |
| Performance | Load/stress testing | Per SLAs in D1 | If SLAs defined |
| Security | SAST/DAST scanning | OWASP Top 10 | Yes |

### Testing Tools Guidance

| Language | Unit Testing | Coverage | Mocking |
|----------|-------------|----------|---------|
| Python | pytest | pytest-cov | pytest-mock |
| Go | testing | go test -cover | gomock |
| TypeScript | jest / vitest | c8 / istanbul | jest mocks |

| Category | Tool |
|----------|------|
| Contract testing | Pact, OpenAPI validation |
| E2E | Playwright, Cypress |
| Load testing | k6, locust |
| Security (SAST) | Snyk, SonarQube |

### Pre-commit Hooks (ADR-0010)

All repositories must use pre-commit hooks. Testing-related hooks:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: poetry run pytest --cov=src --cov-fail-under=80
        language: system
        types: [python]
        pass_filenames: false
```

### CI/CD Requirements

All component repositories must have CI that runs:
1. Unit tests with coverage report
2. Linting (language-appropriate)
3. Security scanning (Snyk)
4. Contract tests (if APIs exposed)

### Definition of Done (Testing)

For D4 (Verification) gate approval:
- [ ] All unit tests pass
- [ ] Coverage ≥80% (or justified exception)
- [ ] No critical/high Snyk vulnerabilities
- [ ] API contract tests pass
- [ ] Performance tests meet D1 SLAs

## Consequences

**Good:**
* Consistent quality across components
* Clear expectations for D2 design reviews
* Automation reduces manual review burden

**Bad:**
* Initial setup overhead per repository
* May slow initial development

**Neutral:**
* Teams can choose specific tools within categories

## More Information

* Related: ADR-0010 (Pre-commit Hook Enforcement)
* See: [D2 Template](../templates/d2-design.md) for required Testing Strategy section
* See: [D4 Template](../templates/d4-verification.md) for verification checklist
