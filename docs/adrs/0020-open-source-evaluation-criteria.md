---
parent: Decisions
nav_order: 20
title: ADR-0020 Open Source Evaluation Criteria
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0020: Open Source Evaluation Criteria

## Status

**Draft**

## Context and Problem Statement

ACP will integrate various open source projects (databases, message queues, ML frameworks, etc.). We need clear criteria for evaluating whether an open source project is suitable for enterprise use.

## Decision Drivers

* Security and vulnerability management
* Long-term maintainability
* Scalability characteristics
* License compliance
* Enterprise support availability
* Community health and longevity

## Decision Outcome

### Evaluation Scorecard

All open source dependencies must score **≥70%** to be approved.

| Category | Weight | Criteria |
|----------|--------|----------|
| **Security** | 25% | CVE history, response time, security audit status |
| **Maintenance** | 20% | Release frequency, issue response, contributor diversity |
| **Scalability** | 20% | Horizontal scaling, resource efficiency, benchmarks |
| **License** | 15% | Compatibility (Apache 2.0, MIT preferred), no GPL |
| **Enterprise Support** | 10% | Paid support available, SLA options |
| **Community** | 10% | GitHub stars, corporate backing, ecosystem size |

### Security Evaluation

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| **CVE count (last 2 years)** | <5 | 5-15 | >15 critical |
| **Avg fix time (critical)** | <7 days | 7-30 days | >30 days |
| **Security audit** | Recent (< 1yr) | Older | None |
| **Dependency security** | Snyk clean | Minor issues | Critical issues |

### Maintenance Evaluation

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| **Release frequency** | Monthly | Quarterly | >6 months |
| **Issue response (p50)** | <7 days | 7-30 days | >30 days |
| **Bus factor** | >5 contributors | 2-5 | 1 (single maintainer) |
| **Corporate backing** | Major company | Small company | Individual only |

### Scalability Evaluation

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| **Horizontal scaling** | Native support | With workarounds | Not supported |
| **Benchmark data** | Published, verified | Self-reported | None |
| **Production usage** | >1000 companies | <100 | Few/unknown |
| **Resource efficiency** | Documented | Basic | Unknown |

### License Compatibility

**Approved Licenses:**
- Apache 2.0 ✅
- MIT ✅
- BSD 2/3-Clause ✅
- ISC ✅

**Requires Legal Review:**
- LGPL (linking concerns)
- MPL 2.0 (file-level copyleft)

**Not Approved:**
- GPL/AGPL ❌ (copyleft concerns)
- SSPL ❌ (service restrictions)
- Proprietary ❌

### Required Documentation

For each open source dependency integration, document:

1. **Evaluation Summary** (scorecard results)
2. **Risk Assessment** (what if project is abandoned?)
3. **Exit Strategy** (alternatives identified)
4. **Monitoring Plan** (CVE tracking, update schedule)

### Snyk Integration

All dependencies must pass Snyk scanning:
- Critical vulnerabilities: Block
- High vulnerabilities: Block (or approved exception)
- Medium/Low: Track, remediate per schedule

## Consequences

**Good:**
* Consistent evaluation across projects
* Reduces risk of unmaintained dependencies
* Ensures license compliance

**Bad:**
* May exclude otherwise good projects with low scores
* Evaluation takes time upfront

## More Information

* Related: ADR-0017 (Testing Strategy) — security testing
* Related: ADR-0019 (Backend Standards) — specific technology choices
* See: [OSSF Scorecard](https://github.com/ossf/scorecard) for automated evaluation
