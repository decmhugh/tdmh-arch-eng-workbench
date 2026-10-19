---
parent: Decisions
nav_order: 12
title: ADR-0012 Changelog Format
status: draft
date: 2026-04-27
---

# ADR-0012: Changelog Format

## Status

**Draft**

## Context and Problem Statement

How should we track notable changes to the project?

## Decision Outcome

**Chosen option**: Keep a Changelog format

## Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

## Entry Types

| Type | When to Use |
|------|-------------|
| Added | New features |
| Changed | Changes to existing functionality |
| Deprecated | Soon-to-be removed features |
| Removed | Removed features |
| Fixed | Bug fixes |
| Security | Security vulnerability fixes |

## Consequences

**Good:** Standardized format, user-friendly changelog
**Bad:** Manual maintenance required

## More Information

See [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
