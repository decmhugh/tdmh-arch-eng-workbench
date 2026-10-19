# Developer Automations — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: [EACPP-1388](https://sunlife.atlassian.net/browse/EACPP-1388)

Scope of this gate: the first automation, **`pr-weekly-summary`**. Later automations add their
own requirements to this spec.

The implementation adopts a script already proven for another team and is delivered in two
phases (see D2): **Phase 1** adopts it with the minimum changes to report on ACP repositories;
**Phase 2** closes the requirements it does not yet meet. Requirements met only in Phase 2 are
marked so.

## User Stories

### US-1: The team sees what merged last week without asking

**As an** ACP Product Team engineer,
**I want** a weekly post in the team channel listing the pull requests merged across our
repositories,
**So that** I know what changed in repositories I do not watch.

**Acceptance Criteria**:
- [ ] **Given** pull requests were merged into `main` in the configured repositories last week,
      **When** the Monday run completes, **Then** a single card appears in *ACP Product Team -
      Chat* listing each one with its number (linked), Jira ticket (linked, when the title has
      one), title, author and merge date.
- [ ] **Given** a pull request was merged outside the reporting window, **When** the report is
      built, **Then** it does not appear.
- [ ] **Given** a repository had no merges, **When** the report is built, **Then** that repository
      is shown with a count of zero rather than omitted.

### US-2: The Product Owner gets a delivery signal without assembling one

**As the** ACP Product Owner,
**I want** the weekly post to state the total and each repository's count,
**So that** I can see the shape of the week's delivery at a glance.

**Acceptance Criteria**:
- [ ] **Given** the card is posted, **When** I read it, **Then** it opens with the reporting
      window and the total merged, and each repository's section is headed with its count.

### US-3: The owner knows when the report did not run

**As the** automation owner,
**I want** to be told when a run fails,
**So that** a quiet channel is never mistaken for a quiet week.

**Acceptance Criteria**:
- [ ] **Given** no pull requests merged in any repository, **When** the run completes, **Then** a
      card is still posted saying so explicitly.
- [ ] **Given** Bitbucket or the workflow endpoint fails, **When** the run ends, **Then** the
      Jenkins build fails. *(Phase 2: the owner is also notified.)*

### US-4: The owner can check the report before it is posted

**As the** automation owner,
**I want** to run the job without posting,
**So that** I can change the report or the repository list safely.

**Acceptance Criteria**:
- [ ] **Given** the job is run with `POST` unchecked, **When** it completes, **Then**
      `weekly_summary.md` is archived as a build artefact and nothing is posted.

## Functional Requirements

### FR-1: Collect merged pull requests

For each configured repository, retrieve every pull request in state `MERGED` into `main` whose
merge time falls inside the reporting window. *Phase 1 reads one page of 30 per repository;
Phase 2 follows pagination until the window is exhausted.*

**API Contract Sketch** (Bitbucket Data Center REST 1.0):
```
GET /rest/api/1.0/projects/EDAEACP/repos/{repo}/pull-requests?state=MERGED&at=refs/heads/main&limit=30
Authorization: Basic <gitget-userid-password>          (Phase 2: Bearer <read-only token>)
Response: { values: [ { id, title, description, author.user.displayName, closedDate } ], isLastPage, nextPageStart }
```

### FR-2: A fixed, calendar-aligned reporting window

The window is the seven days ending at **00:00 Monday, `America/Toronto`**, on the day the job
runs — Monday 00:00 of the previous week up to but excluding Monday 00:00 of this week. It is
computed from the calendar, not from the run's start time, so a delayed or re-run job reports
the same week. *Phase 2 — Phase 1 uses the starter's rolling seven days before the run.*

### FR-3: Configured repositories

The repository list is configuration, not code. The initial list is `acp-product-specs`,
`acp-harness-sdk`, `luminate-sunlife-deploy` and `acp-product-devkit`, all in `EDAEACP`.

### FR-4: Render an Adaptive Card

Build a single Adaptive Card (version 1.5) containing: a title; a line with the window and the
total merged; and one section per repository headed `<repo> (<count>)`, listing each pull
request's number (linked), Jira ticket (linked, when the title contains a key), title, author and
merge date. A repository with no merges shows *No PRs merged.* *Phase 2:* keep the card within
the Teams message size limit by truncating each repository's list with an *"and N more"* link.

### FR-5: Post to Teams through the Power Automate workflow

POST the card through the Sun Life HTTP proxy to the *Send webhook alerts to a channel*
workflow, which delivers it to *ACP Program › ACP Product Team - Chat*.

**API Contract Sketch**:
```
POST $TEAMS_WEBHOOK_URL            (via proxy-prod-http.ca.sunlife:8080)
Content-Type: application/json
{ "type": "message",
  "attachments": [ { "contentType": "application/vnd.microsoft.card.adaptive",
                     "content": { "type": "AdaptiveCard", "version": "1.5", "body": [ ... ] } } ] }
Response: 2xx
```

### FR-6: Run weekly on a schedule

A Jenkins job triggers on cron `H 2 * * 1` in `America/Toronto`.

### FR-7: A Markdown report on every run

Every run writes `weekly_summary.md` — one table per repository with PR number, Jira ticket,
title, author, merge date and description — and Jenkins archives it. A `POST` parameter
(default on) controls whether the card is also posted; unchecked, the run is a dry run.

### FR-8: Fail loudly

Any non-2xx from Bitbucket or the workflow endpoint fails the build. An empty week is a
successful run that posts a card showing every repository with *No PRs merged.* *Phase 2:* a
failed build notifies the owner.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Performance | Run time for four repositories | < 2 minutes |
| NFR-2 | Availability | Scheduled weeks with a posted card | 100%, or a failed build with notification |
| NFR-3 | Security | No credential or workflow URL in the repository, build log, artefact or process arguments | Zero |
| NFR-4 | Security | Bitbucket access is read-only and limited to the configured repositories; Phase 2 replaces shared Basic auth with a Bearer token | Read scope only |
| NFR-5 | Maintainability | Pipeline and script versioned together and reviewed through pull requests | 100% — nothing configured only in the Jenkins UI beyond credentials |
| NFR-6 | Portability | Script runs on the `jenkins-inbound-agent:jdk21-tools` image as provided | No `pip install` at run time |

## Data Model Requirements

Stateless. Nothing is persisted between runs; each run reads Bitbucket and posts once.

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| `MergedPullRequest` (in memory) | `repo`, `id`, `title`, `description`, `author`, `closed`, `ticket`, `url`, `ticket_url` | belongs to one configured repository |
| `ReportWindow` (in memory) | `start`, `end`, `tz` | one per run |

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No merges in any repository | Post the card with every repository showing *No PRs merged.* |
| A configured repository does not exist or is not readable | Build fails; no card is posted |
| More than 30 merges in a repository in one week | Phase 1: only the latest 30 are reported. Phase 2: paginate |
| More merges than fit in one card | Phase 2: truncate per repository with an *"and N more"* link |
| Job re-run later in the week | Phase 1: a different rolling window. Phase 2: the same calendar week (FR-2) |
| Pull request merged into a branch other than `main` | Excluded |
| Title contains Markdown special characters | Escaped in the card; Phase 2 also escapes `\|` and newlines in the Markdown table |
| Title contains no Jira key | Ticket column left empty |
| Daylight-saving transition inside the window | Phase 2: boundaries computed in `America/Toronto` local time |
| `TEAMS_WEBHOOK_URL` is not set and `POST` is checked | Build fails; nothing is posted anywhere |
| Workflow endpoint returns non-2xx | Build fails; no retry that could double-post |

## Constraints

- Bitbucket Data Center at `bitbucket.sunlifecorp.com`, read with the shared
  `gitget-userid-password` service account (Basic auth) in Phase 1. Basic auth can trigger
  CAPTCHA account locks, hence the Phase 2 move to a Bearer token.
- The Teams channel is fed by a Power Automate workflow, not an Office 365 connector webhook.
- Jenkins is the sanctioned scheduler; credentials live in Jenkins. The job runs on the
  Kubernetes `jenkins-inbound-agent:jdk21-tools` image used by the starter job.
- Power Platform (`*.environment.api.powerplatform.com`) is reachable only through
  `proxy-prod-http.ca.sunlife:8080`; Bitbucket is called directly.
- The starter script and `Jenkinsfile` are proven for another team; they change only once they
  have run successfully for ACP, except for the Phase 1 changes listed in D2.

## Capability Gaps

None. This is internal team tooling and selects no ACP capability (see D0).

## Traceability

| Requirement | Capability | D0 Success Criteria | Jira Story |
|-------------|-----------|-------------------|------------|
| FR-1, FR-3 | — | The report is complete | EACPP-1388 |
| FR-2 | — | The report is complete | EACPP-1388 |
| FR-4, FR-5 | — | Manual status assembly is removed | EACPP-1388 |
| FR-6 | — | The report runs unattended; The report is timely | EACPP-1388 |
| FR-7 | — | The report is complete | EACPP-1388 |
| FR-8 | — | Failures are visible | EACPP-1388 |
| US-1, US-2 | — | Manual status assembly is removed | EACPP-1388 |
| US-3 | — | Failures are visible | EACPP-1388 |

No requirement traces to an ACP capability because none is selected; stories are created at D3.
