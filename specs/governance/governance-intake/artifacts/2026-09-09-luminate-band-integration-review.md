# Luminate Band Integration Review — 9 September 2026

> **Artifact type**: Verification · **Status**: Draft — for discussion
> **Verified against**: `AI-Consortium/luminate` `origin/main` = `a0d31c10e`, 9 September 2026
> **Method**: Read the code, not the design branches. Every finding below cites a file.

## Why this was done

ACP is building a risk-classification service and needed to know what Luminate
would actually accept. The governance design documents describe a future state;
this review checks what is merged.

**The headline finding is that Governance Mode is built**, in four merged PRs
(#758, #790, #791, #792), and several ACP specs still describe it as unbuilt.
That is stale, and it changes the posture of this spec from *"could integrate"* to
*"is the missing producer"*.

## Findings

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| **LB-1** | Obligation resolution **cannot proceed without a risk band**. A governed resource carrying none raises `BandNotResolvable`. Nothing in Luminate produces one. | `backend/app/governance/obligations.py` — `raise BandNotResolvable(f"{entity_type}:{entity_id} is governed but carries no '{RISK_BAND_ATTRIBUTE}'.")` | Governance Mode is blocked closed on a band producer. The module docstring says the band *"will come from Risk Triage"*. FR-17. |
| **LB-2** | The `risk-band` attribute **is not seeded**. The string appears only in a constant, two tests and an example README. | `grep -l "risk-band"` → `approvals/facts.py`, `governance/checks.py`, `governance/obligations.py`, `governance/examples/README.md`, 2 test files | Nothing can be written until a deployment seeds the definition, applicability and values. FR-18. |
| **LB-3** | An `EntityAttribute` carries **one curated string**. The version token, pack digests, contributing packs and rationale cannot travel with the band. | `backend/app/attributes/models.py` — `AttributeValue.value = CharField(max_length=120)`, values must pre-exist | FR-16 holds in ACP but not on the Luminate side; an audit there cannot answer *"judged against what?"*. FR-19. |
| **LB-4** | Luminate models **almost none of the agentic inputs**. `autonomy` is zero hits in the backend. `MCPServer` has no data classification, sensitivity or residency field. | `backend/app/agents/models.py`, `backend/app/mcp_servers/models.py` | Agentic bands cannot be derived from the registry; the attributes must be collected at intake. FR-20. |
| **LB-5** | There are **no outbound events**. Zero `webhook` hits. The only async path is `workflow_outbox` → `pg_notify` → in-cluster worker, which is lossy. | `grep -ril webhook backend/**/*.py` → no matches | Nothing signals registration or material change, so classification cannot be event-driven. FR-21. |
| **LB-6** | Writing a governance-authoritative attribute needs **superuser or `governance.metadata.update`**, deliberately withheld from Administrator. | `backend/app/attributes/views.py` — `IsActiveSuperuserOrReadOnly`; `attributes/integration.py` — *"held separately from this resource's own permissions so that whoever can edit a resource cannot tag it out of governance scope"* | The band writer needs a real privilege decision and a dedicated principal. FR-22. |
| **LB-7** | The band vocabulary is **exactly** `low`, `medium`, `high`, `critical`, and it is ranked. A value outside it resolves but is unrankable, and unrankable fails closed **silently**. | `backend/app/governance/obligations.py` — `RISK_BAND_ORDER = ["low", "medium", "high", "critical"]`; `band_rank()` returns `None` outside it | Sun Life's `AA`–`D` must never be written as the band. Confirms the band↔level split is right. NFR-9. |
| **LB-8** | `application` is **deliberately not swept** and has no governance state. `deployment` is band-covered but not swept. | `backend/app/governance/sweep.py` — *"`application` is deliberately absent … it has no `governance_state` column, so there is nothing for a published status to describe"* | A band published against an application is inert in Luminate. LB-Q4. |
| **LB-9** | A `ServicePrincipal` **cannot be an `EvidenceProducer`** — the relation points at the Django user model, and a machine principal is deliberately not a user. An unregistered submission is attributed to `unregistered:`, counts toward nothing, and **still returns 201**. | `backend/app/governance/models.py` — `EvidenceProducer.principal = OneToOneField(settings.AUTH_USER_MODEL, …)`; `shared/service_principal_authentication.py` — `attribution_user()` returns `None` for machine principals | Silent failure on exactly the integration the evidence contract exists for. Upstream defect. LB-Q1. |
| **LB-10** | Luminate has **no discovery**. Its inventory is registration-only; there is no unregistered-resource concept. | No scanning code; every `discover*` hit is OIDC discovery | Discovered-agent auto-triage (FR-10) needs a producer ACP would have to own. LB-Q3. |

## What already fits

Worth recording, because these were the things most likely to be wrong.

| Design choice | Luminate | Status |
|---|---|---|
| Canonical band `low`/`medium`/`high`/`critical` | `RISK_BAND_ORDER` is that list, in that order | Exact match |
| Native level held separately from the platform band | Band is one ranked string | Split is correct |
| Exactly one band per resource | `_band_for` returns `None` unless exactly one value is held | Matches; set `max_per_entity = 1` |
| Band drives approval depth | `ApprovalRequest.resolved_band` and `ObligationProfile.approval_depth` exist | Downstream ready |
| Version token binding inputs and thresholds | `GovernanceStatus.version_token`, `input_digest`, `obligation_revision` | Same pattern, independently arrived at |
| Publish a band, do not decide rigor | Applicability, obligation resolution and enforcement are all core | Boundary correct |

## The path that works today

With no Luminate code change: seed the attribute (T15), classify in ACP, write
only the band string against `(entity_type, entity_id)` (T16), and let Luminate's
`post_save` signal republish `GovernanceStatus`. Explanation and provenance stay
in ACP and are retrievable by the same reference.

The two things that path does **not** solve are LB-3 (provenance cannot cross) and
LB-9 (evidence is closed to machines). Both are on the agenda.

## For the review

| # | Question | Feeds |
|---|---|---|
| **LB-Q1** | Defer the evidence path until Machine Identity lands producer onboarding, or raise the silent-degradation defect with the consortium first? | DD-16, T20 |
| **LB-Q2** | Where does the content pack revision live on the Luminate side — a second governance-authoritative attribute now, or a platform change later? | DD-15, T17 |
| **LB-Q3** | Does discovered-agent auto-triage require ACP to own discovery outright, and is that in this spec or its own? | FR-10 |
| **LB-Q4** | Is the unit of assessment the application or the agent, given Luminate cannot govern an application? | LB-8 |
| **LB-Q5** | Who owns seeding `risk-band` per deployment — ACP, or the Luminate deployment owner? | T15 |

## Ticket traceability

Task→ticket mapping for the tasks this review added. T15–T20 are deliberately
**not** ticketed yet: they are draft and under review, and creating stories for
tasks that may change would clutter the board. `create_jira_from_spec.py` is
idempotent and will fill them in once D3 is agreed.

| Task | Ticket | Why it was raised ahead of the review |
|---|---|---|
| T21 | [EACPP-1293](https://sunlife.atlassian.net/browse/EACPP-1293) | API Platform onboarding has external lead time — an Okta authorization server, audience, scopes and an ingress path are provisioned by another team. Starting it does not depend on how the rest of the review lands. |
| T15–T20 | — | Pending D3 sign-off |

## To raise upstream

| Gap | Ask | Owner |
|---|---|---|
| LB-9 | Let a `ServicePrincipal` register as an `EvidenceProducer`; reject rather than silently degrade an unregistered producer | Machine Identity / Governance Mode |
| LB-3 | Carry a producer-supplied revision or digest alongside a governance-authoritative attribute | Governance Mode |
| LB-5 | An outbound event or durable change feed for registration and material change | Platform |

## Caveat

`origin/designs/org-plugins`, `designs/governance-mode` and `designs/risk-triage`
are **unmerged** and all carry *Status: Draft, Decision: Pending*. Where this
review cites behaviour it cites `origin/main`; where it cites intent it says so.
