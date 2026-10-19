# D1 — Requirements

> **Gate**: D1 | **Status**: Draft | **Epic**: [EACPP-1320](https://sunlife.atlassian.net/browse/EACPP-1320)

## How to read this

Three requirement sets, with different owners.

| Set | Applies to | Owner |
|---|---|---|
| **MIR-1 … MIR-42** | A workload consuming inference through ACP, and the platform team offering it | Assessed once per onboarding, reusable for its ISRA |
| **FR-1 … FR-14** | The ACP platform | ACP Product Team |
| **NFR-1 … NFR-9** | The inference lane as a service | ACP Product Team + Platform |

Every MIR carries a **class** (M mandatory, C conditional, R recommended), the **topology** it
applies to (**C** centralized, **D** distributed, **B** both), an **enforcement point**, and a
**verification method**. A requirement that cannot be evidenced is a wish, so each one names how it
is checked.

---

## Section A — Topology and routing

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-1** | M | B | **Every model call traverses a Luminate gateway.** A workload holding its own provider credential can bypass it; doing so is outside this pattern and outside governance entirely — no policy decision, no budget, no trace, no token accounting, no kill switch. | Network and IAM policy | Absence of a direct provider grant on the workload role; presence of gateway traces for the workload |
| **MIR-2** | M | B | **The workload holds no model credential.** The gateway makes the provider call; the workload authenticates to the gateway, never to Bedrock. | Gateway | Workload secret inventory; role policy review |
| **MIR-3** | M | B | **The topology is a recorded decision, not a default.** Each onboarding records centralized or distributed, and why. | Onboarding record | The onboarding spec names the topology with its reason |
| **MIR-4** | C | C | **Centralized is used where the workload has no AWS account**, or where the account sprawl of the distributed shape is itself the problem. | Architecture review | Recorded in the onboarding decision |
| **MIR-5** | C | D | **Distributed is used where the workload already has an AWS account.** Costs land where they are incurred and no attribution machinery is required. | Architecture review | Service Catalog product launched in the consumer account |
| **MIR-6** | M | C | **Centralized inference is not offered to a workload until the attribution preconditions in Section B are met** for the environment serving it. | Platform | The Section B checks, run against that environment |
| **MIR-7** | R | B | **Region is chosen explicitly.** A model is reached through an offering keyed `(model, provider, region)`; the region a call routes to is a decision with data-residency consequences. | Catalogue | The offering record names the region |

---

## Section B — Attribution

Centralized inference aggregates the bill, so these requirements are what keep it decomposable.
**MIR-8 to MIR-11 are jointly the gate on offering centralized inference to a workload** — each is
independently verifiable, and satisfying only some of them produces a confident wrong number, which
is worse than no number.

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-8** | M | C | **Token quantity is captured completely, including cache reads and cache writes.** The metering path must record every token dimension the provider bills, not only prompt and completion. | Gateway tracing | A cache-heavy call's recorded tokens reconcile to the provider's own usage block within the MIR-13 tolerance |
| **MIR-9** | M | C | **Every model reachable through the gateway carries a per-token price**, including cache-read and cache-write rates where the provider charges them. | Pricing catalogue | `PricingCatalogEntry` count equals the reachable-model count; no reachable model priced null |
| **MIR-10** | M | C | **Usage is materialized into the ledger** at `(project, entity, user, model, provider)` per day. | Rollup worker | `ProjectUsageDaily` is non-empty and its daily totals reconcile to the trace store |
| **MIR-11** | M | C | **Every project that can incur inference spend carries a cost centre** in the finance system's own coding. | Catalogue | No project with usage has an empty `cost_centre` |
| **MIR-12** | M | C | **Unattributed spend is visible and bounded.** The share of spend landing in the null-project bucket is reported, and an agreed ceiling is set. | Chargeback report | The `unattributed` filter returns a share below the agreed ceiling |
| **MIR-13** | M | C | **The ACP figure reconciles to the provider bill** within an agreed tolerance, checked each period before any charge is raised. | Finance control | Period reconciliation record: ACP total vs AWS/Bedrock invoice |
| **MIR-14** | M | C | **No charge is raised from an unreconciled period.** A figure that has not passed MIR-13 may be shown as showback, never cross-charged. | Finance control | Charge run references a passed reconciliation |
| **MIR-15** | R | B | **Run-level correlation is supplied by the caller** via `x-luminate-session-id` where per-run cost attribution is wanted. The ledger aggregates by day, so per-run cost is a trace-store query, not a ledger field. | Caller | Sessions present in the trace store for the workload |

---

## Section C — Measurement integrity

Attribution is only as good as its metering. These requirements exist because a chargeback model is
withdrawn the first time a team audits its bill and finds it wrong.

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-16** | M | C | **Metering error is measured, not assumed.** Before a model is offered centrally, a sample of its traffic is reconciled against the provider's own usage figures and the error recorded. | Platform | Recorded per-model reconciliation sample |
| **MIR-17** | M | C | **Systematic bias between workloads is treated as a defect, not a tolerance.** An error that falls unevenly across teams — for example under-counting cache-heavy callers — is not acceptable at any magnitude that changes who pays. | Platform | Error distribution across workloads, not just the aggregate |
| **MIR-18** | M | B | **Pricing-catalogue drift is detected.** Provider rate cards change; a stale price produces a wrong bill silently. | Platform | Catalogue entries carry a source and a refresh date; drift check on a schedule |
| **MIR-19** | R | C | **Currency is explicit on every figure.** The ledger denominates in `currency` beside `cost`; reports must not drop it. | Report | Report columns include currency |

---

## Section D — Budgets and enforcement

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-20** | M | C | **Spend is bounded by an enforced budget** bound to the accountable owner — project, team, entity or user. A call is **refused** when any matching budget is exhausted, not reported afterwards. | Gateway | A call exceeding a budget returns a throttle response; counter state readable |
| **MIR-21** | M | B | **Budgets warn before they cap**, with enough margin for the owner to act. | Gateway + notification | Soft-warn fires ahead of the cap in a controlled test |
| **MIR-22** | C | B | **Provider or account-side limits bound catastrophic runaway below the platform**, as defence in depth behind the budget. | Provider / cloud account | Limit configuration |
| **MIR-23** | M | B | **A budget has a named owner, and changing one is approved and audited.** Raising one caller's limit must not silently raise another's. | Catalogue | Budget records carry an owner; change history |
| **MIR-24** | M | B | **The kill path is credential and policy revocation, not a budget.** A budget bounds spend; it does not bound damage. | Platform | Revocation drill recorded |
| **MIR-25** | R | B | **A budget whose access path is removed retires itself**, so a limit protecting an unreachable target does not persist as stale configuration. | Catalogue | Orphaned-budget check |
| **MIR-26** | M | C | **What a business owner is told matches what is enforced** for their workload in their environment. A configured-but-inactive budget is worse than none, because it converts an explicit risk into an assumed protection. | Onboarding record | Stated limit reconciles to the enforced limit |

---

## Section E — Model access governance

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-27** | M | B | **Access to a model is an explicit grant.** Default-deny; a caller reaches only the models named by policy. | Policy engine | Policy records; a negative test against an ungranted model |
| **MIR-28** | M | B | **The source of a grant is the smallest thing that is true** — an agent, an application, a user or a user group — never `all_users` as a convenience. | Policy engine | Policy source types in use; absence of `all_users` on model targets |
| **MIR-29** | C | B | **Human access is granted through a user group**, mapped from the enterprise directory, so joining and leaving a team changes access without a policy edit. | Policy engine + directory | `source_type=user_group` policies exist and resolve |
| **MIR-30** | M | B | **Model availability is scoped by region** through the offering, and the region is a data-residency decision recorded at onboarding. | Catalogue | Offering region; onboarding record |
| **MIR-31** | C | B | **Model availability is scoped by project** where a model is restricted to particular work. | Policy scope | Scope tokens on the policy |
| **MIR-32** | M | B | **Model approval status governs availability.** A model not approved for a classification of data is not reachable by a workload handling it. | Catalogue + policy | Model record and the workload's data classification |
| **MIR-33** | M | B | **A model withdrawal is a governed action** with a stated migration path for callers, not a silent catalogue edit. | Lifecycle | Withdrawal record; caller notification |
| **MIR-34** | R | B | **Grants are reviewed on a cycle**, and a grant with no traffic in the period is challenged. | Operations | Review record against the usage ledger |

---

## Section F — Provider portability

The catalogue indirection in Section A is what makes a provider replaceable. These requirements are
what keep that replaceability real rather than asserted.

| # | Class | Topo | Requirement | Enforcement point | Verification |
|---|---|---|---|---|---|
| **MIR-35** | M | C | **A workload names a model, never a provider, endpoint, region or account.** A workload carrying a provider SDK or a provider-native response dependency has opted out of portability whatever the catalogue says. | Gateway contract | Code/config review; the workload's request names only a model |
| **MIR-36** | M | C | **The gateway presents one request and response format** regardless of the provider underneath, absorbing differences in message shape, tool-call encoding, streaming framing and error taxonomy. | Gateway | The same workload call succeeds unchanged against two different providers' offerings |
| **MIR-37** | M | B | **Each offering declares its capabilities** — context window, tool calling, structured output, streaming, multimodal input, prompt caching — and **a swap to an offering that does not meet its callers' declared needs is refused, not attempted.** | Catalogue | Capability declarations present; a deliberately deficient swap is refused |
| **MIR-38** | M | B | **A swap that changes the model is evaluated before cutover.** The same prompt against a different model returns different output; behavioural equivalence is demonstrated, not assumed. | Evaluation | Evaluation record comparing candidate to incumbent |
| **MIR-39** | M | B | **Cost is re-measured after a swap.** Price is a property of the offering, and providers price dimensions — cached reads especially — differently. | Pricing + ledger | Post-swap cost compared to pre-swap for the same workload |
| **MIR-40** | M | B | **Rollback is as cheap as the swap.** If reverting needs a workload redeploy, a prompt rewrite or a data migration, it was not a repoint and is handled as a change programme. | Operations | Rollback rehearsed or demonstrated |
| **MIR-41** | R | B | **At least one model carries a credible alternate offering**, and the swap path is exercised — in shadow if not in anger — so portability is a tested control rather than a belief. | Platform | Shadow or progressive swap record |
| **MIR-42** | M | B | **Onboarding a provider is a governed platform change** — credentials, capability declarations, pricing and a data-handling position recorded before any workload is pointed at it. | Platform | Provider onboarding record |

---

## Functional requirements — the platform

| # | Requirement | Rationale |
|---|---|---|
| **FR-1** | Offer both topologies and publish the decision criteria. | Both are legitimate; the choice is contextual |
| **FR-2** | Record the centralized-inference decision and the population it is offered to. | Discharges integration-patterns T16 |
| **FR-3** | Capture every token dimension the provider bills, including cache reads and writes. | Break 1; AIC-679 |
| **FR-4** | Load and maintain a per-token price for every reachable model. | Break 2 |
| **FR-5** | Materialize usage into the daily ledger and monitor the rollup. | Break 3 |
| **FR-6** | Require and validate a cost centre on every project that can incur spend. | Break 4 |
| **FR-7** | Deliver attribution to the enterprise chargeback pipeline in the finance system's own coding. | Replaces the AWS account boundary centralization removes |
| **FR-8** | Report unattributed spend as a first-class figure with a ceiling. | Centralization widens this bucket |
| **FR-9** | Reconcile the ACP figure to the provider bill each period before any charge. | A number reaching finance acquires authority |
| **FR-10** | Publish model availability by region and by project. | Governance question asked directly |
| **FR-11** | Support user-group-sourced grants against model targets, mapped from the directory. | The AD-group requirement |
| **FR-15** | **Maintain provider portability as an operating property** — capability declarations kept true, an alternate offering available, and the swap path rehearsed. | Portability that has never been exercised is a belief, not a control |
| **FR-16** | **Support shadow, progressive, per-region, full-repoint and failover swap modes**, with rollback no more expensive than the swap. | A swap that cannot be reversed cheaply will not be attempted |
| **FR-12** | State the enforced budget position for each workload, and keep the stated limit equal to the enforced one. | Prevents an assumed protection |
| **FR-13** | Raise the enforcement and spend-dimension dependencies with the consortium. | D-1, D-2 |
| **FR-14** | Keep `integration-patterns` consistent with this pattern's topology decision. | Two specs must not contradict |

---

## Non-functional requirements

| # | Requirement | Target |
|---|---|---|
| **NFR-1** | Inference-path latency added by governance | Within the gateway's existing budget; attribution is asynchronous and adds none |
| **NFR-2** | Ledger freshness | Rollup completes within one day of the usage date |
| **NFR-3** | Reconciliation variance | Within an agreed tolerance, measured per period per model |
| **NFR-4** | Attribution completeness | Unattributed share below the agreed ceiling |
| **NFR-5** | Availability of the inference lane | Inherits the gateway's posture; fail-closed on a policy decision |
| **NFR-6** | Report access control | Scoped; org-wide per-user spend restricted to an explicitly authorized role |
| **NFR-7** | Personal data in reports | Minimum necessary; purpose and retention stated |
| **NFR-8** | Catalogue accuracy | No reachable model without a price; no priced model without a source and refresh date |
| **NFR-9** | Auditability | Every model call produces an audit event and a trace attributable to a principal |

---

## Traceability

| Requirements | Addresses | From D0 |
|---|---|---|
| MIR-1 … MIR-7 | Topology decision, routing, region | SC-1, SC-8 |
| MIR-8 … MIR-15 | Attribution and reconciliation | SC-3, SC-4 |
| MIR-16 … MIR-19 | Metering integrity | SC-5 |
| MIR-20 … MIR-26 | Budgets, enforcement and ownership | SC-6 |
| MIR-27 … MIR-34 | Model access governance | SC-7 |
| MIR-35 … MIR-42 | Provider portability and swap safety | SC-1 |
| FR-1 … FR-2 | The recorded decision | SC-1, SC-2 |
| FR-3 … FR-9 | Attribution as a programme | SC-3, SC-4, SC-5 |
| FR-10 … FR-11 | Access governance | SC-7 |
| FR-12 … FR-14 | Budget commitment, consortium asks, spec consistency | SC-2, SC-6 |
