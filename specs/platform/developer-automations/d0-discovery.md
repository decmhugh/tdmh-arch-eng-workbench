# Developer Automations — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: [EACPP-1388](https://sunlife.atlassian.net/browse/EACPP-1388)

## Problem Statement

The ACP Product Team works across many repositories in the `EDAEACP` Bitbucket project, and
there is no single view of what changed in a given week. Knowing what merged means opening each
repository's pull-request list in turn, or asking the people who did the work.

That gap costs time in three places:

- **Status reporting** — weekly updates are assembled by hand from memory, chat and Bitbucket.
- **Team awareness** — engineers do not see changes merged in repositories they do not watch,
  including changes that affect them.
- **Stakeholder visibility** — the Product Owner and Scrum Master have no regular, low-effort
  signal of delivery across the product.

Reporting like this is routine, recurring and mechanical, which makes it a good candidate for
automation. It is the first of what is expected to be a small family of developer automations,
so this spec is scoped as the home for them rather than for one script.

## Opportunity

- **A weekly delivery signal at no reporting cost.** A report of merged pull requests, posted
  where the team already works, replaces hand-assembled status updates.
- **Shared awareness across repositories.** Everyone sees what merged, not only what they
  reviewed.
- **A reusable pattern.** A scheduled Jenkins job that runs a script and posts to Teams is the
  shape the next automations can reuse, with the same credential handling and ownership.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| Sam Mamelli | Owner / author | A reliable weekly report that runs without intervention |
| Lalit Summan | ACP Product Owner | A regular view of delivery across the product |
| David Nguyen | ACP Scrum Master | Input to sprint reporting and team cadence |
| ACP Product Team engineers | Readers | Awareness of changes across repositories they do not watch |
| Jenkins / Global DevOps | Platform owner | Job follows JTE conventions and credential standards |

## Scope

### In Scope

- **`pr-weekly-summary`** — the first automation. A weekly report of pull requests merged in
  the previous seven days across four `EDAEACP` repositories — `acp-product-specs`,
  `acp-harness-sdk`, `luminate-sunlife-deploy` and `acp-product-devkit` — posted to
  **ACP Program › ACP Product Team - Chat** in Microsoft Teams.
- **Scheduled execution** — run weekly by a Jenkins job, with no manual trigger needed.
- **A new `EDAEACP` repository** holding the script and its `Jenkinsfile` together.
- **Configuration** — the repository list, branch and report title are kept together in one
  place, separate from the logic; the channel is chosen by credential, not code.
- **Credential handling** — the Bitbucket read credential and the Teams posting credential are
  held in Jenkins credentials, never in the repository.

### Out of Scope

- **Repositories outside `EDAEACP`** — `T1KACP` and the consortium GitHub Enterprise
  (`AI-Consortium`) are not covered by the first automation.
- **Open, declined or in-review pull requests** — the report covers merged pull requests only.
- **Metrics and scoring** — no cycle-time, review-latency or per-person productivity measures.
  The report says what merged, not how well anyone performed.
- **Jira reconciliation** — linking merged pull requests to tickets or moving ticket status.
- **Further automations** — added to this spec as they are identified, each with its own scope.

## Capability Requirements

Not applicable. This is internal ACP Product Team tooling: it does not onboard a use case to ACP
and does not route traffic through the platform, so the
[ACP Capability Map](../../../capability-map.md) baseline does not apply.

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| The report runs unattended | Weekly Jenkins runs completed without manual intervention | 100% over four consecutive weeks |
| The report is complete | Merged pull requests in the report vs merged pull requests in Bitbucket for the configured repositories and window | 100% match on a sampled week |
| The report is timely | Posted to the Teams channel on the scheduled day | Every scheduled week |
| Manual status assembly is removed | Weekly status updates built by hand from Bitbucket | None, once the report is live |
| Failures are visible | A failed run notifies the owner rather than posting nothing | 100% of failed runs |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
| Bitbucket read access to the selected `EDAEACP` repositories | Bitbucket administrators / ACP Product Team | Hard | No data to report |
| A Power Automate workflow (*Send webhook alerts to a channel*) posting to the ACP Product Team - Chat channel | ACP Product Team | Hard | Report has nowhere to go — workflow already created |
| A new `EDAEACP` repository for the script and `Jenkinsfile` | Bitbucket administrators / ACP Product Team | Hard | Nowhere to version the automation |
| A Jenkins folder, job and credentials | Global DevOps / ACP Jenkins folder owners | Hard | No scheduled execution |
| The existing starter script and `Jenkinsfile` | Another Sun Life team (*Enterprise Pipeline Weekly Summary*, `CSDP`) via Sam Mamelli | Hard | Proven in Sun Life's Jenkins and network — adopted, then adapted |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| A credential is committed or logged | Medium | High | The starter script hard-codes another team's signed workflow URL; it is removed before the script enters an ACP repository. Credentials bound from Jenkins at runtime; never printed |
| A failed run goes unnoticed and the channel is simply quiet | Medium | Medium | Notify the owner on failure; distinguish "no merges this week" from "did not run" |
| The report is used as a per-person performance measure | Low | Medium | Report merged work by repository; no individual metrics (out of scope) |
| The workflow URL leaks — it carries its own signature, so anyone holding it can post to the channel | Low | Medium | Held only as a Jenkins secret-text credential; never committed, logged or placed in a spec; regenerated if exposed |
| The repository list drifts from what the team actually works in | Medium | Low | Keep the list in one place and review it with the team |
| Shared `gitget` service account is locked by CAPTCHA after Basic-auth failures | Low | Medium | Proven for the starter job; move to a read-only Bearer token once the job is stable |

## Open Questions

- [x] **Repositories** — `acp-product-specs`, `acp-harness-sdk`, `luminate-sunlife-deploy`,
      `acp-product-devkit`.
- [x] **Channel and mechanism** — ACP Program › ACP Product Team - Chat, through a Power
      Automate *Send webhook alerts to a channel* workflow receiving an Adaptive Card.
- [x] **Home for the code** — a new `EDAEACP` repository holding both the script and the
      `Jenkinsfile`. A starter script exists.
- [x] **Schedule** — Jenkins cron `H 2 * * 1`, `America/Toronto`.
- [x] **Bitbucket identity** — the shared `gitget-userid-password` service account, as used by
      the starter job.
- [ ] What is the new repository called? (`acp-developer-automations` is proposed in D2.)
- [ ] What other automations are candidates for this spec after `pr-weekly-summary`?
