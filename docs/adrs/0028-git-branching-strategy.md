---
parent: Decisions
nav_order: 28
title: ADR-0028 Git Branching Strategy
status: accepted
date: 2026-06-10
decision-makers: [Seth Chalmers, Matthew Clark]
---

# ADR-0028: Git Branching Strategy

## Status

**Accepted**

## Context and Problem Statement

ACP uses a polyrepo architecture (ADR-0025) with 20+ repositories. We need a consistent branching strategy that defines when CI/CD pipelines trigger, how code flows to environments, and how releases are cut. The strategy must work with Jenkins JTE pipelines and CDD release promotion (ADR-0027).

Key questions:
- What triggers a build/deploy to dev?
- How do we cut a release candidate for sit/stg/prod?
- Do we use long-lived branches (develop/release/main) or trunk-based?
- How does the branching model interact with CDD phases?

## Decision Drivers

* CI/CD integration -- Jenkins JTE needs clear trigger events (branch push, tag, PR merge)
* CDD compatibility -- release promotion phases need a defined artifact (image tag, Git ref) to promote
* Team size and velocity -- small team (< 10 devs) favors simpler models
* Polyrepo complexity -- 20+ repos means the branching model is replicated everywhere
* Environment mapping -- need clear mapping from branch/tag to environment
* Rollback clarity -- need to know which commit is in which environment

## Considered Options

* **Option A: Release Branch Model** -- Feature branches merge to main, release branches for promotion
* **Option B: Tag-Based (GitHub Flow)** -- Feature branches merge to main, tags trigger CDD promotion
* **Option C: Git Flow** -- develop/release/main branches with hotfix support
* **Option D: Environment Branches** -- Branch per environment (dev, staging, prod)

## Decision Outcome

**Chosen option: Option B — Tag-Based (GitHub Flow)**

Tags are the single source of truth for releases. No release branches to manage. Main must always be in a releasable state, which enforces quality discipline at the PR level.

### Model

```
feature/EACPP-{id}  -->  main  -->  tag v{version}
     |                    |              |
     PR + CI build        dev-ca         CDD promotes through sit/stg/prod
```

### Flow

1. Developers work on `feature/EACPP-{id}` branches (per existing convention)
2. PR to `main` triggers CI: build, test, scan (no deploy)
3. Merge to `main` triggers CD: build image, deploy to dev-ca automatically
4. When ready for release, tag `v{version}-rc.1` on main — CDD promotes to sit-ca
5. If sit-ca validation passes, tag `v{version}` — CDD promotes through stg-ca → prod-ca → prod-us
6. Hotfixes: PR directly to main, then tag a new patch version (`v{version}.{patch}`)

### Trigger Mapping

| Event | Pipeline Action | Environment |
| - | - | - |
| PR opened/updated | Build + test + scan (no deploy) | None (CI only) |
| PR merged to main | Build + test + scan + deploy | dev-ca |
| Tag `v*-rc.*` pushed | Deploy existing image | sit-ca (via CDD) |
| CDD promotion (rc tag) | Deploy existing image | stg-ca |
| Tag `v*` (no rc) pushed | Deploy existing image | prod-ca, prod-us (via CDD) |

### Image Tagging Convention

| Trigger | Image Tag | Example |
| - | - | - |
| PR merge to main | `main-{SHA7}` | `main-a1b2c3d` |
| RC tag | Same image, promoted by CDD | `main-a1b2c3d` (unchanged) |
| Release tag | Same image, promoted by CDD | `main-a1b2c3d` (unchanged) |

> **Key insight:** The image is built once on merge to main. Tags don't rebuild — they tell CDD which already-built image to promote. This ensures the exact binary tested in dev-ca reaches production.

### Constraints

- **Main must always be releasable.** Broken main blocks all releases across the team.
- **Feature flags** for incomplete features that land on main before they're prod-ready.
- **Squash merges** to keep main history linear and bisectable.
- **No long-lived branches** — only short-lived feature branches off main.

### Consequences

* Good, because no release branch management overhead across 20+ repos
* Good, because one branch (main) + immutable tags = simple mental model
* Good, because CDD only needs to know "which tag?" — no branch-to-env mapping
* Good, because image is built once and promoted (binary parity guarantee)
* Bad, because main must always be releasable — requires discipline and good CI
* Bad, because hotfixes must go through main (no cherry-pick to release branch)
* Neutral, because small team size makes "always-releasable main" achievable

## More Information

* Referenced by D1 US-2 and FR-4 in the Deployment & Infrastructure spec (EACPP-212)
* Must align with CDD release promotion (ADR-0027)
* Polyrepo architecture (ADR-0025) means the strategy is applied per-repo
* Existing convention uses `feature/EACPP-{id}` branches (from copilot-instructions.md)
* Can be revised if team grows significantly or if "always-releasable main" proves problematic
