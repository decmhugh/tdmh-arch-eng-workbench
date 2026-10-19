# ACP Capability Map — Future Roadmap

> What ACP will be able to do that it cannot do today, ranked so it can be argued with.
> **Nothing here is delivered** until it appears as ✅ on the [capability map](capability-map.md).
>
> **Last verified**: 2026-09-14 against `luminate` @ `654c3199`, `luminate-designs` @ `d477c13`,
> the open code and design PRs, and `AIC` / `ACPDIS` on `ai-consortium.atlassian.net`.
> **Owner**: Seth Chalmers (ACP Product)

---

## 1. Proposed ranking

**The next 20, in the order Sun Life would argue for them.** A *starting order for the
discussion*, not an agreed one — the Product Board sets the real rank. Bring it to the meeting
and move things.

Ordered on the Sun Life position: **governance gaps first, then anything touching cost**, then
the capability asks behind them. **Group** is where each lands on the
[At a Glance view](capability-map-summary.md). Nothing already shipped or being built appears
here — that is [§2](#2-work-underway), and under the [voting procedure][voting] it does not
consume a place.

| Rank | Priority | Group | Capability | Where it stands | Consortium |
|---|---|---|---|---|---|
| | **Governance gaps** | | | | |
| **1** | Access attestation and 3LoD | E | [CAP-19](capability-map.md#cap-19) | Ballot | [ACPDIS-125](https://ai-consortium.atlassian.net/browse/ACPDIS-125) |
| **2** | External audit-event ingest | E | [CAP-18](capability-map.md#cap-18) | **Nothing** | *nothing anywhere* |
| **3** | MCP tool change review | C | [CAP-03](capability-map.md#cap-03) | Ballot | [ACPDIS-112](https://ai-consortium.atlassian.net/browse/ACPDIS-112) |
| **4** | Mandatory access restrictions | B | [CAP-07](capability-map.md#cap-07) | Ballot | [ACPDIS-73](https://ai-consortium.atlassian.net/browse/ACPDIS-73) |
| **5** | AI incident containment workflows | C | [CAP-11](capability-map.md#cap-11) | Ballot | [ACPDIS-30](https://ai-consortium.atlassian.net/browse/ACPDIS-30) |
| **6** | Agent behaviour circuit breakers | C | [CAP-11](capability-map.md#cap-11) | Ballot | [ACPDIS-52](https://ai-consortium.atlassian.net/browse/ACPDIS-52) |
| **7** | AI quality drift alerts | D | [CAP-17](capability-map.md#cap-17) | Ballot | [ACPDIS-35](https://ai-consortium.atlassian.net/browse/ACPDIS-35) |
| | **Cost, budgets and attribution** | | | | |
| **8** | Quota enforcement at the gateway | C | [CAP-12](capability-map.md#cap-12) | Accepted | [AIC-20](https://ai-consortium.atlassian.net/browse/AIC-20) |
| **9** | Budget management | C | [CAP-12](capability-map.md#cap-12) | Accepted | [AIC-831](https://ai-consortium.atlassian.net/browse/AIC-831) |
| **10** | Monetary spend enforcement | C | [CAP-12](capability-map.md#cap-12) | Ballot | [ACPDIS-104](https://ai-consortium.atlassian.net/browse/ACPDIS-104) |
| **11** | Total spend by end user | E | [CAP-20](capability-map.md#cap-20) | Accepted | [AIC-79](https://ai-consortium.atlassian.net/browse/AIC-79) |
| **12** | Spend by team or group | E | [CAP-20](capability-map.md#cap-20) | **Nothing** | *nothing anywhere* |
| **13** | Internal chargeback | E | [CAP-20](capability-map.md#cap-20) | Ballot | [ACPDIS-103](https://ai-consortium.atlassian.net/browse/ACPDIS-103) |
| | **The capability asks behind them** | | | | |
| **14** | Multi-tenancy | F | [CAP-22](capability-map.md#cap-22) | Ballot | [ACPDIS-83](https://ai-consortium.atlassian.net/browse/ACPDIS-83) |
| **15** | Federated / per-BU gateways | F | [CAP-22](capability-map.md#cap-22) | Ballot | [ACPDIS-124](https://ai-consortium.atlassian.net/browse/ACPDIS-124) |
| **16** | Agent skills registry | A | [CAP-27](capability-map.md#cap-27) | Accepted | [AIC-153](https://ai-consortium.atlassian.net/browse/AIC-153) |
| **17** | Governed API resources | A | [CAP-03](capability-map.md#cap-03) | Ballot | [ACPDIS-108](https://ai-consortium.atlassian.net/browse/ACPDIS-108) |
| **18** | Evaluation-driven model routing | C | [CAP-08](capability-map.md#cap-08) | **Nothing** | *nothing anywhere* |
| **19** | Evaluation test suites | D | [CAP-17](capability-map.md#cap-17) | Ballot | [ACPDIS-110](https://ai-consortium.atlassian.net/browse/ACPDIS-110) |
| **20** | Session data-flow restrictions | C | [CAP-26](capability-map.md#cap-26) | Ballot | [ACPDIS-77](https://ai-consortium.atlassian.net/browse/ACPDIS-77) |

**Read *Where it stands* before arguing rank.** It is the difference between a priority that can
be ranked next month and one that cannot be ranked at all.

| | Meaning | What ranking it achieves |
|---|---|---|
| **Accepted** | An `AIC` epic exists — the consortium has taken the work. Detail in [§4](#4-accepted-awaiting-capacity) | Moves it up the queue for capacity |
| **Ballot** | An `ACPDIS` idea exists, nothing scheduled. Detail in [§5](#5-the-full-ballot) | Gets it into the top 20 and therefore into design |
| **Nothing** | **No idea, no design, no code — nothing anywhere in Luminate.** Detail in [§6](#6-not-in-luminate-at-all) | **Nothing.** Raise the idea first, or the rank is decorative |

**Three of the twenty do not exist in Luminate in any form.** That is
the actionable finding on this page. Ranking them changes nothing until the ideas are raised;
see [§6](#6-not-in-luminate-at-all).

**Why governance sits above cost even though governance is now largely enforced.** The
September build closed the big one: governance status is read by the access layer, so a
non-compliant or suspended resource is now **denied at runtime** rather than merely flagged.
What is left in Group E is the part a regulator and internal audit ask for and the platform
still cannot produce — attestation, and a way for a Sun Life system that is not the gateway to
contribute to the AI audit trail. Neither has an idea behind it.

**Cost has shipped more than it looks.** Per-token pricing, the usage rollup fed from Langfuse's
ClickHouse, and usage-and-cost charts for agents, models and MCP servers are all on `main`
under [AIC-59](https://ai-consortium.atlassian.net/browse/AIC-59). The gaps are the ones that
turn reporting into control: **nothing debits a quota**, there is no monetary dimension, and
spend can be sliced by application but not yet by end user — and not at all by team.

**OSFI is deliberately not on this list.** Governance Mode ships the *schema* for compliance
regimes, not the regimes themselves — shipping one jurisdiction's prudential rules as the platform
default would make one member's regulator everyone's baseline. E-23 and B-13 are expressed by
supplying a regime configuration, and a worked `ca-osfi.json` example covering `ca-osfi-e23` and
`ca-osfi-b13` ships in the repo as an illustration. What Sun Life owes is its own control catalogue,
band vocabulary and obligation profiles, signed off by the people accountable for them. That is
deployment configuration on our side, not a consortium ask — see
[INT-10](capability-map.md#int-10).

**Risk triage is not on this list either, for the same reason.** The band already decides how
much rigour applies — obligation resolution keys on *(framework, band)*, and a governed resource
carrying no band raises rather than passing. What *sets* the band is a seam Luminate left open on
purpose: `obligations.py` reads it from a governance-authoritative attribute and says outright
that it *"will come from Risk Triage"*, isolating the swap to one function. Sun Life fills that
seam with `acp-risk-classification` — a standalone service that scores against versioned content
packs and publishes a band with its own revision. It supplies a **band, never a verdict**, because
Governance Mode keeps obligation resolution in core. Product-team work against an interface that
already exists, tracked as `governance-risk-triage`
([EACPP-648](https://sunlife.atlassian.net/browse/EACPP-648)) and `governance-intake`
([EACPP-877](https://sunlife.atlassian.net/browse/EACPP-877)) — see
[INT-11](capability-map.md#int-11).

---

## 2. Work underway

Being built now. **Not ranked** — under the [voting procedure][voting] work underway continues by
default and does not consume one of the 20 places, though a representative can propose pausing or
stopping any of it.

**Sun Life is writing most of this.** Every row marked *SLF* is a Sun Life-authored PR open
against `AI-Consortium/luminate`, which is the strongest lever we have on the roadmap: work we
build ourselves does not wait for a ranking round.

| Priority | Group | Capability | Where it is | Consortium |
|---|---|---|---|---|
| **Structured model and agent cards** — the named sections a reviewer asks for: intended use, limitations, training data, evaluation, contact. Follows the published Hugging Face model-card section set and the A2A agent card, with import and a sha256 of exactly what was read | D | [CAP-16](capability-map.md#cap-16) | *SLF* — [#845](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/845) open, design [#164](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/164) | [AIC-805](https://ai-consortium.atlassian.net/browse/AIC-805) |
| **Model and agent evaluation** — evaluation evidence with a looked-up tier, the obligation deciding what is measured and the band deciding the bar, demotion published as a signal governance adjudicates | D | [CAP-17](capability-map.md#cap-17) | *SLF* — five stacked PRs [#815–#819](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/815) open, design [#150](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/150) | [AIC-38](https://ai-consortium.atlassian.net/browse/AIC-38) |
| **Governance evidence chain** — an action plan and target date on an open finding, the validation a verdict rests on, an inventory of what a resource consumes and a flag when a material input never arrives, and a documentation/repository pointer on every governed kind | D, E | [CAP-14](capability-map.md#cap-14), [CAP-19](capability-map.md#cap-19) | *SLF* — [#841](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/841), [#842](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/842), [#843](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/843), [#844](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/844) open | [AIC-801](https://ai-consortium.atlassian.net/browse/AIC-801)–[AIC-804](https://ai-consortium.atlassian.net/browse/AIC-804) |
| **Per-project provider accounts** — a project's inference served from that project's own provider account, and shared-account spend attributed per project | C, E | [CAP-08](capability-map.md#cap-08), [CAP-20](capability-map.md#cap-20) | *SLF* — [#824](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/824) open, design [#161](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/161) | [AIC-783](https://ai-consortium.atlassian.net/browse/AIC-783) |
| **Application usage and cost charts** — the Applications tab onto the usage rollup | E | [CAP-20](capability-map.md#cap-20) | [#840](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/840) open | [AIC-526](https://ai-consortium.atlassian.net/browse/AIC-526) |
| **Configurable audit export** — formatters, saved configurations and a portal export | E | [CAP-18](capability-map.md#cap-18), [CAP-20](capability-map.md#cap-20) | [#852](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/852) open | [AIC-553](https://ai-consortium.atlassian.net/browse/AIC-553) |
| **Compliance reporting and evidence** | E | [CAP-19](capability-map.md#cap-19) | epic in progress | [AIC-154](https://ai-consortium.atlassian.net/browse/AIC-154) |
| **Governance exceptions** — time-bound, approved departures from an obligation | D | [CAP-14](capability-map.md#cap-14) | epic in progress | [AIC-441](https://ai-consortium.atlassian.net/browse/AIC-441) |
| **Usage and cost attribution** — pricing, rollup and charts. Mostly landed; see [§1](#1-proposed-ranking) | E | [CAP-20](capability-map.md#cap-20) | epic in progress | [AIC-59](https://ai-consortium.atlassian.net/browse/AIC-59) |
| **Chain authorization (on-behalf-of)** | B | [CAP-24](capability-map.md#cap-24) | epic in progress | [AIC-483](https://ai-consortium.atlassian.net/browse/AIC-483) |
| **Access policy enforcement and RBAC** — incl. traces and metrics endpoints | B | [CAP-07](capability-map.md#cap-07) | epic in progress, [#847](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/847), [#853](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/853) | [AIC-49](https://ai-consortium.atlassian.net/browse/AIC-49) |
| **Safety control enforcement** | C | [CAP-10](capability-map.md#cap-10) | epic in progress | [AIC-23](https://ai-consortium.atlassian.net/browse/AIC-23) |
| **End-user attribution and directory sync** | B | [CAP-05](capability-map.md#cap-05) | epic in progress | [AIC-56](https://ai-consortium.atlassian.net/browse/AIC-56) |

> **Left this list by shipping.** *Governance enforcement at the access layer*
> ([AIC-442](https://ai-consortium.atlassian.net/browse/AIC-442)) is on `main`. `facts.py`
> publishes the governance statuses of resources under a rule promoted to **enforce**, and
> `authz.rego` gates `allow` on `not governance_denied` for models, MCP servers and agents —
> denying on `governance_non_compliant`, `governance_status_stale` and
> `governance_status_untrusted`. A resource under a rule still in *observe* is absent from the
> policy input entirely rather than present and ignored. This is the change that turns the kill
> switch, the governed lifecycle and risk-proportionate rigour from records into controls.
>
> Also shipped since the last pass: **govern MCP tool access**
> ([AIC-47](https://ai-consortium.atlassian.net/browse/AIC-47)), **custom roles**
> ([AIC-384](https://ai-consortium.atlassian.net/browse/AIC-384)), the **governance approval
> carve-out** ([AIC-796](https://ai-consortium.atlassian.net/browse/AIC-796)) that makes
> Administrator's hold on the approval verbs a deploy-time choice, and
> **machine-token attribution** ([AIC-797](https://ai-consortium.atlassian.net/browse/AIC-797)),
> so a Keycloak machine token resolves to the machine rather than to nobody.

---

## 3. How ranking works

```text
ACPDIS idea  →  Product Board ranking  →  design  →  AIC epic  →  built
    §5              §5 → §4                §4          §2          capability-map.md ✅
```

From the consortium's [Product Board Roadmap Voting procedure][voting]:

- Each representative submits **one ranked list of 20** from [`ACPDIS`][acpdis], privately,
  before seeing anyone else's.
- **Your top 3 are protected.** Every representative's first choice lands in Tier 1, second in
  Tier 2, third in Tier 3, regardless of how little other support it has. That is the mechanism
  by which a Sun Life-specific need — OSFI — survives a room where nobody else is federally
  regulated in Canada. Spend them deliberately.
- Points are `21 − rank`, summed across all lists, and order **within** a tier only. A high score
  never jumps a tier.
- Protection applies to the **agreed deliverable**, not the whole feature. Splitting a large ask
  into increments does not extend it past the first one.
- Equal weight per seat; monthly or quarterly, looking roughly 3 months ahead.

### What a date means

Windows are quoted verbatim from the `AIC` epic. Read them as **the release window the epic
currently sits in, not an estimate for that feature**: they cluster on `2026-09-30` and
`2026-10-28` because that is how the squads bucketed MVP release planning, not because thirty
features independently landed on two days. No dates means the epic has never been through release
planning, which is not a signal of low priority.

### How much comfort a design should give you

Of the 41 designs in `luminate-designs`, **two are APPROVED — the Organizational Model and Portal
RBAC. Every other one is `Status: Draft`, `Decision: Pending`**, several since Q1. A merged design
means *"someone wrote down how this could work"*, not *"this is agreed and scheduled"*. An open PR
is less than that; a **draft** PR less again. Where a design exists, the ask is *"move this design
to a decision"* rather than *"write a design"* — a materially shorter path, and one that benefits
from a named business group behind it.

---

## 4. Accepted, awaiting capacity

An `AIC` epic exists — the board has accepted the work — but nothing has started. These compete
for the ranked places in §1.

| Group | Capability | What it would deliver | Consortium epic | Window | Design |
|---|---|---|---|---|---|
| C | [CAP-12](capability-map.md#cap-12) | **Quota enforcement at the gateway** — the counter store that turns the quota model from documentation into a control. Still the single largest P0 on the map: `quotas.rego` computes `matched_quota_ids`, `authz.rego` allows on policy match and **not** on quota remaining, and nothing debits. | [AIC-20](https://ai-consortium.atlassian.net/browse/AIC-20) | 2026-08-10 → 2026-09-30 | [rate-limiting](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/rate-limiting) |
| C | [CAP-12](capability-map.md#cap-12) | **Budget management** — the epic behind a budget as a first-class object rather than a quota dimension. **Accepted with no child stories and no dates**, so there is nothing to read about scope yet; ranking it is what gives it shape. | [AIC-831](https://ai-consortium.atlassian.net/browse/AIC-831) | *no dates* | — |
| E | [CAP-20](capability-map.md#cap-20) | **Total spend by end user over a chosen period** — the per-user half of attribution. Its sibling [AIC-75](https://ai-consortium.atlassian.net/browse/AIC-75) does the same by application. Both are `To Do` under an epic that is otherwise largely delivered. | [AIC-79](https://ai-consortium.atlassian.net/browse/AIC-79) | *no dates* | [usage-and-cost-tracking](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/usage-and-cost-tracking) |
| C | [CAP-12](capability-map.md#cap-12) | **Quota modelling and governance** — pools, attribute filters, approval routing on the authoring side. | [AIC-43](https://ai-consortium.atlassian.net/browse/AIC-43) | 2026-08-10 → 2026-10-28 | [quotas](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/quotas) |
| A | [CAP-27](capability-map.md#cap-27) | **Agent skills registry** — a governed catalogue of reusable agent skills: reviewed-before-adoptable versions, integrity pinning, provenance on import, platform-wide recall. Raised with Nova; TELUS is building the same thing. Design still a **draft** PR after two months. | [AIC-153](https://ai-consortium.atlassian.net/browse/AIC-153) | *no dates* | [#106](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/106) *(draft)* |
| B | [CAP-06](capability-map.md#cap-06) | **First-class machine identity** — workload identity lifecycle beyond today's service principals and API keys. | [AIC-37](https://ai-consortium.atlassian.net/browse/AIC-37) | 2026-09-01 → 2026-10-28 | [machine-identity](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/machine-identity) |
| A | [CAP-04](capability-map.md#cap-04) | **Promote a deployment and its access policy between tiers** — dev → SIT → stage → prod as a governed transition rather than a re-registration. | [AIC-61](https://ai-consortium.atlassian.net/browse/AIC-61) | 2026-09-11 → 2026-10-30 | [organizational-model](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/organizational-model) — **APPROVED** |
| E | [CAP-17](capability-map.md#cap-17), [CAP-20](capability-map.md#cap-20) | **Alerting on model quality, latency and error degradation** — the monitoring half of E-23 ongoing monitoring. | [AIC-28](https://ai-consortium.atlassian.net/browse/AIC-28) | 2026-09-11 → 2026-10-30 | [agent-traceability](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/agent-traceability) |
| B | [CAP-07](capability-map.md#cap-07) | **Fine-grained access rules** and lifecycle authority for policy state. | [AIC-152](https://ai-consortium.atlassian.net/browse/AIC-152) | *no dates* | portal-rbac — **APPROVED** |
| B | [CAP-24](capability-map.md#cap-24) | **Delegated access and token attenuation** — narrowing a delegated token as it crosses a hop. | [AIC-364](https://ai-consortium.atlassian.net/browse/AIC-364) | *no dates* | [agent-platform-delegation](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/agent-platform-delegation) |
| C | [CAP-08](capability-map.md#cap-08) | **Control agent network access** — environment and location connectivity matrices. | [AIC-30](https://ai-consortium.atlassian.net/browse/AIC-30) | *no dates* | [connectivity-rules](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/connectivity-rules) |
| B | [CAP-07](capability-map.md#cap-07) | **Access policy learning** — propose policies from observed traffic; reachability, drift and redundancy queries. | [AIC-31](https://ai-consortium.atlassian.net/browse/AIC-31) | *no dates* | [access-insights](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/access-insights) |
| D | [CAP-14](capability-map.md#cap-14) | **Human approval for agent actions** — an approval in the request path, not only on the configuration change. | [AIC-32](https://ai-consortium.atlassian.net/browse/AIC-32) | *no dates* | [approval-flows](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/approval-flows) D2 [#141](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/141) *(draft)* |
| E | [CAP-18](capability-map.md#cap-18) | **Audit and decision-event coverage** — closing the gap where a governed action produces no event. | [AIC-295](https://ai-consortium.atlassian.net/browse/AIC-295) | *no dates* | [audit-events](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/audit-events) |
| E | [CAP-20](capability-map.md#cap-20) | **Export vendor telemetry** — getting platform telemetry out to a member's own stack. | [AIC-42](https://ai-consortium.atlassian.net/browse/AIC-42) | *no dates* | — |
| E | [CAP-01](capability-map.md#cap-01), [CAP-04](capability-map.md#cap-04) | **Sync AI assets to CMDB.** The consortium-side half of what Sun Life needs for Archer / ServiceNow. See [INT-06](capability-map.md#5-the-sun-life-integration-surface) for the Sun Life-side half. | [AIC-22](https://ai-consortium.atlassian.net/browse/AIC-22) | *no dates* | — |
| C | [CAP-11](capability-map.md#cap-11) | **Automated incident response** — turning a detected signal into a containment action. | [AIC-25](https://ai-consortium.atlassian.net/browse/AIC-25) | *no dates* | — |
| F | [CAP-21](capability-map.md#cap-21) | **Platform plugins** — per-organisation extension points, so a member can add behaviour without forking. | [AIC-151](https://ai-consortium.atlassian.net/browse/AIC-151) | *no dates* | [#99](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/99) |
| E | [CAP-20](capability-map.md#cap-20) | **Member chargeback** — internal pricing, margin visibility, multi-hop cost attribution, showback-mode ramps. | [AIC-157](https://ai-consortium.atlassian.net/browse/AIC-157) | *no dates* | [chargeback](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/chargeback) |
| A | [CAP-02](capability-map.md#cap-02) | **Curated model provider catalogue** and **prompt-template management**. | [AIC-159](https://ai-consortium.atlassian.net/browse/AIC-159), [AIC-155](https://ai-consortium.atlassian.net/browse/AIC-155) | *no dates* | [model-pricing-catalog](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/model-pricing-catalog) |
| D | [CAP-17](capability-map.md#cap-17) | **Validate model responses** — structured-output conformance checking on the response path. | [AIC-29](https://ai-consortium.atlassian.net/browse/AIC-29) | *no dates* | — |
| F | [CAP-21](capability-map.md#cap-21) | **Catalog playground** and **project resource views** — the self-service surface a builder lands on. | [AIC-17](https://ai-consortium.atlassian.net/browse/AIC-17), [AIC-18](https://ai-consortium.atlassian.net/browse/AIC-18) | *no dates* | [self-service-portal](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/self-service-portal) |

---

## 5. The full ballot

Every idea in [`ACPDIS`][acpdis] in *Parking Lot* or *Discovery* — proposed, not scheduled, and
eligible to be ranked. The top 20 in §1 is drawn from here. A Sun Life ask that belongs to one of
these should be added as a comment on the existing idea rather than raised as a duplicate.

**Sun Life interest** is the argument a representative would make in the room. It is not a score.

| Group | Idea | What it would deliver | Design | Capability | Sun Life interest |
|---|---|---|---|---|---|
| F | [ACPDIS-83](https://ai-consortium.atlassian.net/browse/ACPDIS-83) **Multi-Tenancy** | One enterprise Luminate deployment where each tenant's resources, users, activity and evidence are isolated from the others. Renamed from *Business Unit Data Isolation* and now the **only** live multi-tenancy idea — the sharing and delegated-administration ideas beside it were closed. | [#144](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/144) *(draft)*, [#155](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/155) *(draft)* | [CAP-22](capability-map.md#cap-22) | **High.** Raised with the US team. Projects alone do not isolate deployment-wide resources; without this, one Sun Life BU can see another's evidence. |
| F | [ACPDIS-126](https://ai-consortium.atlassian.net/browse/ACPDIS-126) **Data Residency and Isolation** | One central control plane and portal, while regulated data rests inside a boundary the member names — and a party outside that boundary, the platform operator included, cannot read what is inside it. **Depends on ACPDIS-83**: residency is a property *of* a tenant boundary, so there is nothing to pin data to until that lands. | — | [CAP-22](capability-map.md#cap-22), [CAP-26](capability-map.md#cap-26) | **High if confirmed.** Raised off the multi-tenancy meeting against a possible US HIPAA requirement. A covered entity must know where PHI rests and who can reach it, and an operator able to read it becomes a business associate. Confirm the requirement is real before ranking it high. |
| F | [ACPDIS-124](https://ai-consortium.atlassian.net/browse/ACPDIS-124) **Federated Gateways** | An organisational unit's inference served by gateways it operates, in its own network and jurisdiction, without a second control plane — and compliance still answerable centrally across every gateway. Distinct from multi-tenancy, which draws the boundary *within* one deployment but does not settle who **operates** the gateway traffic egresses through. | — | [CAP-22](capability-map.md#cap-22) | **High.** The topology conversation with the US team, and the shape Sun Life BUs with residency or network-boundary obligations keep arriving at. Raised 2026-09-15 off this page's own finding that nothing covered it. |
| C | [ACPDIS-104](https://ai-consortium.atlassian.net/browse/ACPDIS-104) **Monetary Spend Enforcement** | Monetary caps that actually stop work when the allowance is exhausted, accounting for in-flight consumption. | [quotas](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/quotas) D1/D2 | [CAP-12](capability-map.md#cap-12) | **High.** `dimension=spend` is Phase 2 and gated on the pricing catalogue. Any use case asking for a **dollar** budget cannot be served until this lands. |
| C | [ACPDIS-30](https://ai-consortium.atlassian.net/browse/ACPDIS-30) **AI Incident Containment Workflows** | Turning incident signals into controlled containment actions with accountable response authority and a safe recovery path. | — | [CAP-11](capability-map.md#cap-11) | **High.** B-13 Principle 17. Suspension gives the stop; this gives the workflow around it. |
| C | [ACPDIS-52](https://ai-consortium.atlassian.net/browse/ACPDIS-52) **Agent Behaviour Circuit Breakers** | Detecting abnormal agent behaviour and interrupting the workload under an explicit containment policy. | — | [CAP-11](capability-map.md#cap-11) | **High.** The automatic half of the kill switch — today every stop is a human noticing. |
| D | [ACPDIS-35](https://ai-consortium.atlassian.net/browse/ACPDIS-35) **AI Quality Drift Alerts** | Drift detection against a baseline, and an alert when quality degrades. | [#150](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/150) | [CAP-17](capability-map.md#cap-17) | **High.** E-23 ongoing monitoring. No drift detection exists today. |
| D | [ACPDIS-110](https://ai-consortium.atlassian.net/browse/ACPDIS-110) **Evaluation Test Suites** | Reusable evaluation suites a use case can be measured against before promotion. | [#150](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/150) | [CAP-17](capability-map.md#cap-17) | **High.** E-23 independent validation before production. |
| D | [ACPDIS-112](https://ai-consortium.atlassian.net/browse/ACPDIS-112) **MCP Tool Change Review** | Re-review when a registered MCP tool's definition changes underneath its approval. | — | [CAP-03](capability-map.md#cap-03) | **High.** An approved tool whose schema silently changes is an approval that no longer means anything. |
| B | [ACPDIS-73](https://ai-consortium.atlassian.net/browse/ACPDIS-73) **Mandatory Access Restrictions** | Org-level deny rules a project-level policy cannot override — a compliance floor. | [access-constraints](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/access-constraints) | [CAP-07](capability-map.md#cap-07) | **High.** Without it, every guarantee is only as strong as the most permissive project policy. |
| C | [ACPDIS-77](https://ai-consortium.atlassian.net/browse/ACPDIS-77) **Session Data-Flow Restrictions** | Session-scoped flow attributes — sensitivity, provenance, tenant, jurisdiction — constraining where data may go. | [data-flow-control](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/data-flow-control) | [CAP-26](capability-map.md#cap-26) | **High.** The only designed answer to a data-residency obligation. |
| E | [ACPDIS-96](https://ai-consortium.atlassian.net/browse/ACPDIS-96) **Stored Trace Privacy Controls** | Controls over what of a governed call is retained in the trace store. | [langfuse](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/langfuse) | [CAP-20](capability-map.md#cap-20) | **High.** Traces holding customer content is a privacy exposure, not a feature. |
| B | [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) **Per-User Third-Party Connections** | A person connects their own vendor SaaS account once, and agents acting for them reach that service as that person — three-legged OAuth tokens held, refreshed and presented by the platform, never by the agent. Distinct from [ACPDIS-26](https://ai-consortium.atlassian.net/browse/ACPDIS-26), which is one shared credential per deployment. | — | [CAP-24](capability-map.md#cap-24) | **High.** Waldo ([EACPP-987](https://sunlife.atlassian.net/browse/EACPP-987)) runs a self-built per-user OAuth vault for Atlassian, ServiceNow and Splunk, and its pilot exit needs a 3LO tool call through Luminate as the right user. A shared service account cannot do it — the vendor loses the person. Sun Life record: [EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444). |
| E | [ACPDIS-106](https://ai-consortium.atlassian.net/browse/ACPDIS-106) **SIEM Audit Export** | Luminate audit events delivered into a member's SIEM with preserved attribution and observable delivery failures. | — | [CAP-20](capability-map.md#cap-20) | **Medium.** Sun Life ships infrastructure logs to Splunk separately ([INT-05](capability-map.md#int-05)); this is about the control-plane audit store. |
| E | [ACPDIS-23](https://ai-consortium.atlassian.net/browse/ACPDIS-23) **Enterprise CMDB Resource Sync** | Synchronising AI resource records with a supported CMDB, surfacing conflicts, missing ownership and stale records. | — | [CAP-01](capability-map.md#cap-01) | **Medium.** The Archer / ServiceNow route. The Archer API is not available to us until 2027, which is why the ACP record is becoming the primary one. |
| E | [ACPDIS-107](https://ai-consortium.atlassian.net/browse/ACPDIS-107) **Platform Security Evidence Pack** | A packaged security-control evidence set for a member's own assurance process. | [compliance-reporting](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/compliance-reporting) | [CAP-19](capability-map.md#cap-19) | **Medium.** Feeds the ISRA / ATG process rather than the regulator. |
| A | [ACPDIS-108](https://ai-consortium.atlassian.net/browse/ACPDIS-108) **Governed API Resources** | Governed API targets that a skill or an agent can declare a dependency on. | [#105](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/105) *(draft)* | [CAP-03](capability-map.md#cap-03) | **Medium.** The natural companion to the skills registry — a skill that calls an API needs the API governed too. |
| D | [ACPDIS-111](https://ai-consortium.atlassian.net/browse/ACPDIS-111) **Model-Assisted Evaluation** | LLM-as-judge scoring inside the governed evaluation path. | [#150](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/150) | [CAP-17](capability-map.md#cap-17) | **Medium.** |
| B | [ACPDIS-57](https://ai-consortium.atlassian.net/browse/ACPDIS-57) **Temporary Privileged AI Access** | Time-bound, workflow-bound and break-glass access instead of standing access. | [jit-access](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/jit-access) | [CAP-25](capability-map.md#cap-25) | **Medium.** B-13 least privilege. Access is standing today. |
| B | [ACPDIS-75](https://ai-consortium.atlassian.net/browse/ACPDIS-75) **Conditional AI Access Posture** | Per-call context — geo, device, MFA, network zone, attestation — refining the authorization decision. | [caller-posture](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/caller-posture) | [CAP-26](capability-map.md#cap-26) | **Medium.** |
| B | [ACPDIS-74](https://ai-consortium.atlassian.net/browse/ACPDIS-74) **AI Access Reachability Insights** | "Who can reach what" queries over the effective policy set. | [access-insights](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/access-insights) | [CAP-07](capability-map.md#cap-07) | **Medium.** Needed for access attestation. |
| E | [ACPDIS-125](https://ai-consortium.atlassian.net/browse/ACPDIS-125) **Access Recertification** | Access grants reviewed on a cadence by a named accountable person, with the outcome held as durable evidence — and reviews by different assurance functions distinguishable from each other. [ACPDIS-74](https://ai-consortium.atlassian.net/browse/ACPDIS-74) answers *who can reach what*; this is the decision taken on that answer, and the record that it was taken. | — | [CAP-19](capability-map.md#cap-19) | **High.** Periodic access review is a control every regulated member is examined on, and the platform cannot evidence it. Access is standing today. Raised 2026-09-15 off this page's own finding. |
| D | [ACPDIS-78](https://ai-consortium.atlassian.net/browse/ACPDIS-78) **User-Approved Agent Missions** | User-signed, session-scoped task consent bounding what an agent may do on someone's behalf. | [mission-contracts](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/mission-contracts) | [CAP-24](capability-map.md#cap-24) | **Medium.** |
| A | [ACPDIS-42](https://ai-consortium.atlassian.net/browse/ACPDIS-42) **Governed Prompt Library** | A governed prompt catalogue with ownership and visibility rules. | — | [CAP-27](capability-map.md#cap-27) | **Medium.** Sun Life has already tried an ungoverned prompt library and it failed on ownership, not on technology. Rank this only with an owner named. |
| C | [ACPDIS-97](https://ai-consortium.atlassian.net/browse/ACPDIS-97) **Enterprise DLP Integration** | Routing prompt and response content through an enterprise DLP engine. | [guardrails](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/guardrails) | [CAP-10](capability-map.md#cap-10) | **Medium.** |
| C | [ACPDIS-95](https://ai-consortium.atlassian.net/browse/ACPDIS-95) **Reversible PII Tokenization** | Tokenising rather than redacting PII, so a downstream response can be re-identified. | guardrails | [CAP-10](capability-map.md#cap-10) | **Medium.** Redaction breaks any use case that must return the customer's own data. |
| E | [ACPDIS-55](https://ai-consortium.atlassian.net/browse/ACPDIS-55) **Audit Investigation** | Investigation tooling over the audit store rather than raw queries. | audit-events | [CAP-18](capability-map.md#cap-18) | **Medium.** |
| E | [ACPDIS-103](https://ai-consortium.atlassian.net/browse/ACPDIS-103) **Internal AI Chargeback** | Cross-charging AI consumption back to the consuming business unit. | [chargeback](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/chargeback) | [CAP-20](capability-map.md#cap-20) | **Medium.** |
| B | [ACPDIS-89](https://ai-consortium.atlassian.net/browse/ACPDIS-89) **Platform-Managed Service Identities** | The platform issuing and rotating workload credentials rather than a human doing it. | [machine-identity](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/machine-identity) | [CAP-06](capability-map.md#cap-06) | **Medium.** |
| F | [ACPDIS-45](https://ai-consortium.atlassian.net/browse/ACPDIS-45) **Organization Extension Plugins** | Member-specific extension points on the platform. | [#99](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/99) | [CAP-21](capability-map.md#cap-21) | **Medium.** The alternative to a Sun Life fork. |
| C | [ACPDIS-38](https://ai-consortium.atlassian.net/browse/ACPDIS-38) **Private AI Network Boundaries** | Private-endpoint and egress-restricted network topologies for the gateway. | [connectivity-rules](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/connectivity-rules) | [CAP-08](capability-map.md#cap-08) | **Medium.** Largely absorbed by the Sun Life deployment today ([INT-03](capability-map.md#5-the-sun-life-integration-surface)). |
| C | [ACPDIS-31](https://ai-consortium.atlassian.net/browse/ACPDIS-31) **Model Failover Routing** | Automatic failover to a second provider when the primary degrades. | — | [CAP-08](capability-map.md#cap-08) | **Medium.** E-21 operational resilience. |
| C | [ACPDIS-26](https://ai-consortium.atlassian.net/browse/ACPDIS-26) **MCP Credential Isolation** | Per-tenant credential isolation for MCP servers — one shared service credential per deployment, injected so the agent never holds it. The per-user case is [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165). | [mcp-hosting](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/mcp-hosting) | [CAP-03](capability-map.md#cap-03) | **Medium.** |
| E | [ACPDIS-22](https://ai-consortium.atlassian.net/browse/ACPDIS-22) **Project AI Budget Alerts** | Warning before a budget is exhausted, as distinct from stopping at the cap. | quotas | [CAP-12](capability-map.md#cap-12) | **Medium.** Weaker than [ACPDIS-104](https://ai-consortium.atlassian.net/browse/ACPDIS-104); rank that one first. |
| D | [ACPDIS-29](https://ai-consortium.atlassian.net/browse/ACPDIS-29) **Human Approval for Agent Actions** | An approval gate on a specific agent action at runtime. | [approval-flows](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/approval-flows) | [CAP-14](capability-map.md#cap-14) | **Medium.** |
| D | [ACPDIS-99](https://ai-consortium.atlassian.net/browse/ACPDIS-99) **Safety Control Effectiveness** | Measuring whether a guardrail is actually catching anything. | guardrails | [CAP-10](capability-map.md#cap-10) | **Medium.** A guardrail nobody measures is a guardrail nobody can defend. |
| E | [ACPDIS-100](https://ai-consortium.atlassian.net/browse/ACPDIS-100) **Observability Recovery & Retention** | Retention policy and recovery for the observability store. | langfuse | [CAP-20](capability-map.md#cap-20) | **Medium.** |
| C | [ACPDIS-102](https://ai-consortium.atlassian.net/browse/ACPDIS-102) **Controlled Gateway Fleet Maintenance** | Rolling gateway upgrades without dropping governed traffic. | [gateway-management](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/gateway-management) | [CAP-08](capability-map.md#cap-08) | **Medium.** |
| B | [ACPDIS-79](https://ai-consortium.atlassian.net/browse/ACPDIS-79) **Directory Attribute Sync** | Syncing directory attributes so policies can target them. | [portal-sso](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/tree/main/docs/projects/luminate/02-architecture-and-design/designs/portal-sso) | [CAP-13](capability-map.md#cap-13) | **Medium.** |
| C | [ACPDIS-82](https://ai-consortium.atlassian.net/browse/ACPDIS-82) **Reusable Guardrail Control Profiles** | Named guardrail profiles applied by attribute rather than configured per resource. | guardrails | [CAP-10](capability-map.md#cap-10) | **Medium.** |
| F | [ACPDIS-54](https://ai-consortium.atlassian.net/browse/ACPDIS-54) **Governed AI Resource Playground** | A sanctioned place to try a model or agent without standing up a deployment. | self-service-portal | [CAP-21](capability-map.md#cap-21) | **Medium.** The alternative is people testing outside the gateway. |
| A | [ACPDIS-59](https://ai-consortium.atlassian.net/browse/ACPDIS-59) **Unified AI Resource Inventory** | One inventory across registries and platforms. | — | [CAP-01](capability-map.md#cap-01) | **Medium.** Largely met by the existing registries; rank only if a gap is named. |
| D | [ACPDIS-51](https://ai-consortium.atlassian.net/browse/ACPDIS-51) **Controlled Model Experiments** | Governed A/B testing between models. | — | [CAP-17](capability-map.md#cap-17) | **Low.** |
| E | [ACPDIS-50](https://ai-consortium.atlassian.net/browse/ACPDIS-50) **AI Spend Scenario Planning** | Modelling spend under a proposed change before making it. | chargeback | [CAP-20](capability-map.md#cap-20) | **Low.** |
| F | [ACPDIS-61](https://ai-consortium.atlassian.net/browse/ACPDIS-61) **Project Resource Workspace** | A project-scoped view of everything a team owns. | self-service-portal | [CAP-21](capability-map.md#cap-21) | **Low.** |
| F | [ACPDIS-49](https://ai-consortium.atlassian.net/browse/ACPDIS-49) **In-Portal Guidance Assistant** | An assistant inside the portal that answers "how do I onboard". | — | [CAP-21](capability-map.md#cap-21) | **Low.** |
| B | [ACPDIS-37](https://ai-consortium.atlassian.net/browse/ACPDIS-37) **Resource Name Impersonation Checks** | Preventing a resource registering under a name that impersonates another. | — | [CAP-01](capability-map.md#cap-01) | **Low.** |
| C | [ACPDIS-43](https://ai-consortium.atlassian.net/browse/ACPDIS-43) **Private Semantic Response Cache** | A cache keyed on semantic similarity, inside the governance boundary. | — | [CAP-08](capability-map.md#cap-08) | **Low.** Cost optimisation, not governance. |
| C | [ACPDIS-62](https://ai-consortium.atlassian.net/browse/ACPDIS-62) **Third-Party Gateway Adapter** | Governing traffic that goes through someone else's gateway. | — | [CAP-08](capability-map.md#cap-08) | **Low.** Weakens [CAP-08](capability-map.md#cap-08); prefer the single governed egress path. |

> **Closed ideas.** [ACPDIS-114](https://ai-consortium.atlassian.net/browse/ACPDIS-114)
> Shared AI Services Across Tenants and [ACPDIS-113](https://ai-consortium.atlassian.net/browse/ACPDIS-113)
> Delegated Tenant Administration were **closed to Won't Do** since the last pass — both were
> ranked in the previous version of this page, and ranking a closed idea achieves nothing.
> Multi-tenancy now rests entirely on [ACPDIS-83](https://ai-consortium.atlassian.net/browse/ACPDIS-83).
> Also Won't Do: [ACPDIS-80](https://ai-consortium.atlassian.net/browse/ACPDIS-80)
> Work Management Hierarchy, [ACPDIS-68](https://ai-consortium.atlassian.net/browse/ACPDIS-68)
> Gateway Audit Trail, [ACPDIS-56](https://ai-consortium.atlassian.net/browse/ACPDIS-56)
> Metadata engine / approval flow, [ACPDIS-53](https://ai-consortium.atlassian.net/browse/ACPDIS-53)
> Luminate Security Framework and [ACPDIS-20](https://ai-consortium.atlassian.net/browse/ACPDIS-20)
> Advanced Authorization. Re-raising one needs a new argument, not a re-submission.

---

## 6. Not in Luminate at all

The most important list on this page. Each of these has **no `ACPDIS` idea, no design, and no
code** — verified against `luminate` `origin/main`, `luminate-designs` `origin/main` and the open
PRs on both, plus `AIC` / `ACPDIS` / `ACP`. They therefore **cannot be ranked at a Product Board
round in their current state**: the procedure ranks ideas, and there is no idea to rank.

Raise the idea first — see [Capability Gap Escalation](process/capability-gap-escalation.md) and
the `submit-consortium-idea` skill in `acp-consortium-devkit`.

> **Two have left this list.** Access attestation was rank 1 and federated gateways rank 15, both
> with nothing behind them; they are now
> [ACPDIS-125](https://ai-consortium.atlassian.net/browse/ACPDIS-125) and
> [ACPDIS-124](https://ai-consortium.atlassian.net/browse/ACPDIS-124), and both rankable. That is
> the whole purpose of this section — it is a to-do list, not a description of the weather.

| Rank | Group | Gap | What was searched, and found | Sun Life impact |
|---|---|---|---|---|
| **2** | E | **External audit-event ingest** ([CAP-18](capability-map.md#cap-18)) | The audit contract states there is *deliberately* no public producer endpoint — producers call in-process. [ACPDIS-105](https://ai-consortium.atlassian.net/browse/ACPDIS-105) covers event coverage *within* the platform, not ingest from outside it. The [#852](https://ai-consortium.ghe.com/AI-Consortium/luminate/pull/852) export work moves events *out*, not in. | **Material.** Any Sun Life system that is not the gateway and must contribute to the AI audit trail is unserved, and has no route to becoming served. |
| **12** | E | **Spend by team or group** ([CAP-20](capability-map.md#cap-20)) | Spend can be sliced by application ([AIC-75](https://ai-consortium.atlassian.net/browse/AIC-75)) and, once built, by end user ([AIC-79](https://ai-consortium.atlassian.net/browse/AIC-79)). **Team, group and cost-centre are absent** — no story, no idea, no dimension on the rollup. | **Material.** A budget holder at Sun Life owns a team, not an application. Cost that cannot be rolled up to the group that spent it cannot be governed by the person accountable for it. |
| **18** | C | **Evaluation-driven model routing** ([CAP-08](capability-map.md#cap-08)) | Routing today is registry configuration: a policy names permitted offerings and the gateway routes to them. **Nothing selects a model by evaluation score, semantic fit, or a quality-versus-cost tradeoff.** The adjacent ideas are not this: [ACPDIS-31](https://ai-consortium.atlassian.net/browse/ACPDIS-31) *Model Failover Routing* is availability, [ACPDIS-43](https://ai-consortium.atlassian.net/browse/ACPDIS-43) and `ACP-201` are semantic **caching**, and [AIC-26](https://ai-consortium.atlassian.net/browse/AIC-26) *Provide Inference Failover* is **Cancelled**. | **Medium-high, and rising.** The evaluation work in flight ([AIC-38](https://ai-consortium.atlassian.net/browse/AIC-38)) produces exactly the scores such a router would consume. Raising the idea while that build is fresh is materially cheaper than retrofitting it later. |

> **Also absent, and not ranked here.** **AI red-teaming / adversarial testing** has no design
> and no code; [AIC-727](https://ai-consortium.atlassian.net/browse/AIC-727) exists only to record
> that a sibling design was *named* and never written. Sun Life carries it as
> `ai-red-teaming` ([EACPP-842](https://sunlife.atlassian.net/browse/EACPP-842)). If it is wanted
> upstream it needs an idea of its own.

> **Also absent, and not ranked here.** **Per-user attribution for a developer-local coding
> agent** ([CAP-29](capability-map.md#cap-29)). The governed path itself exists — Claude Code
> reaches a model through the gateway and the access policy denies correctly — but a human
> token authenticates without attributing, so the call bills to nobody and the audit row cannot
> be joined to a person. The adjacent consortium items are **not** this: [AIC-79](https://ai-consortium.atlassian.net/browse/AIC-79)
> is spend by end user on the rollup, not identity on the call. Sun Life carries the capability
> as [EACPP-1324](https://sunlife.atlassian.net/browse/EACPP-1324) and the Claude Code slice as
> [EACPP-1319](https://sunlife.atlassian.net/browse/EACPP-1319). It needs an `ACPDIS` idea before
> it can be ranked.

---

## 7. Keeping this page current

This page goes stale faster than the capability map, because Jira moves daily. Refresh it before
every Product Board round and at every consortium release. The full procedure — which source
feeds which column — is in
[`.github/skills/capability-map-refresh/SKILL.md`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/.github/skills/capability-map-refresh/SKILL.md).

1. **Re-read the funnel, do not re-derive it.** `ACPDIS` status decides §5 membership; the
   presence of an `AIC` epic decides §4; that epic's `statusCategory` decides §2. A design merging
   promotes nothing — a design is not a schedule.
2. **Refresh the Jira columns mechanically**, so a date cannot be wrong by hand:

   ```bash
   python3 scripts/refresh_roadmap_jira.py            # report drift
   python3 scripts/refresh_roadmap_jira.py --write    # rewrite the window cells
   ```

3. **Re-read the design statuses** on `luminate-designs` `origin/main` and the open PRs. A design
   moving from `Pending` to a `Decision` is the most useful thing to report back to a waiting use
   case.
4. **Move anything that shipped** off this page and onto [capability-map.md](capability-map.md) as
   ✅. A row in both places is how the two documents start disagreeing.
5. **Re-rank §1** after a Product Board round, recording what the board agreed rather than what
   was proposed.
6. **Regenerate the At a Glance diagram** — it renders §1 and §2 as clickable cards, so a rank
   change that skips this step leaves the picture lying:
   `python3 scripts/render_capability_map.py --export`.
7. Update the `Last verified` header, then re-sync:
   `CONFLUENCE_SPACE_KEY=T1KACP python3 scripts/sync_to_confluence.py --capability-map`.
   The space key must be inline — the shared credential file exports `DPEP`.

---

## Related

- **[ACP Capability Map — At a Glance](capability-map-summary.md)** — the one-page view this page hangs off
- **[ACP Capability Map (detailed)](capability-map.md)** — what is built today, and the [gap register](capability-map.md#6-gap-register) this page is the forward half of
- **[Capability Gap Escalation](process/capability-gap-escalation.md)** — how a use-case need becomes an `ACPDIS` idea
- **[Product Board Roadmap Voting][voting]** — the consortium procedure this page is shaped to

[acpdis]: https://ai-consortium.atlassian.net/jira/polaris/projects/ACPDIS/ideas
[voting]: https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/160
