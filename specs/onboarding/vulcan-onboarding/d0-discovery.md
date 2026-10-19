# Vulcan Onboarding — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: **Approved 2026-09-03** | **Epic**: [EACPP-1133](https://sunlife.atlassian.net/browse/EACPP-1133)
>
> Approved with the use case on 2026-09-03, together with D1 and D2; implementation proceeds
> under [D3](d3-tasks.md). **One exit condition remains open** — the capability table below is
> still marked *proposed* because the confirmation session against named capability IDs is not
> recorded as having happened. It is carried as D3 **T19** rather than back-filled with a date.
>
> **Sources**: the onboarding discovery session; the follow-up thread on centralised inference
> and chargeback; and the target-run-journey architecture and repository links supplied by
> Patrick Dufour afterwards — `AGI/ai-agent-orchestration-api` and `AGI/vulcan-agent-langchain`,
> both read at `main` on 2026-08-28.

## Problem Statement

Vulcan started as an agent a developer drove interactively through GitHub Copilot on their own
machine. A human had to start every remediation, and the model access came from a developer's
personal Copilot entitlement.

The team is now turning it into **remediation as a service**: a containerised OpenShift workload
that ingests a vulnerability list, processes repositories at scale, and raises pull requests for
an engineer to review. Two Vulcan agents exist today — a Modernizer that upgrades the Java
platform and dependencies against Snyk findings, and a SAST Fixer that remediates Checkmarx
findings. Both are dispatched as Kubernetes Jobs by a separate Spring Boot service, the
AI Agent Orchestration API.

That shift breaks three things interactive operation was quietly covering:

1. **Inference has no legitimate source.** GitHub Copilot is licensed for interactive developer
   use, not for an unattended batch workload. Vulcan has already built an AWS Bedrock provider
   with Okta OAuth2 → STS `AssumeRoleWithWebIdentity` federation to replace it
   (`src/vulcan/providers/bedrock/auth.py`, decision recorded 2026-08-26). Taking that route to
   production means Vulcan needs its own AWS workload account with Bedrock access, and it binds
   Vulcan to one model vendor.
2. **Tool access runs on standing functional-ID credentials.** The job container calls
   Bitbucket, Snyk, Checkmarx, Jenkins and Artifactory directly, authenticated by long-lived
   personal access tokens injected as environment variables from a Kubernetes Secret
   (`BITBUCKET_TOKEN`, `SNYK_TOKEN`, `CX_APIKEY`, `JENKINS_API_TOKEN`). Nothing outside the pod
   can see or constrain which tool the agent reached for, on whose behalf, or why.
3. **Nothing authoritative says the agent is still allowed to run.** The Orchestration API
   resolves the agent from `agent-registry/agents.json` on its own classpath — a file inside its
   own repository. It is a real registry with a real lifecycle enum
   (`DRAFT`/`ACTIVE`/`DEPRECATED`/`REVOKED`), but it is self-asserted. Revoking an agent means
   editing a file and redeploying the orchestrator.

Vulcan's own measurement is also thinner than it looks. Token counts published to the existing
AI Agent Usage Metrics API are a **client-side `tiktoken` estimate**, not the provider-reported
figure, and the `aiModel` field falls back to a hardcoded literal when the pull-request model is
unset. There is no cost figure anywhere in the pipeline.

## Opportunity

Patrick's target-run-journey diagram places ACP in two columns of Vulcan's run, and that framing
is the shape of this onboarding:

| Column | What ACP becomes | Where it attaches in Vulcan's code |
|---|---|---|
| **Identity, policy, registry** | The authority the Orchestration API asks before it spins up a job pod — *is this agent still approved to run?* | `AgentRegistry.resolve(agentId)`, a single-method Java interface |
| **Inference and tool access** | The single governed egress the job container uses instead of calling Bedrock, Bitbucket and the scanners directly | `vulcan.tools.llm.get_llm()`, the provider-neutral seam every agent node already goes through |

Both seams already exist because both codebases were built with the boundary in the right place.
Vulcan's agents never import a provider class; the orchestrator's registry is one method. This is
an unusually cheap integration for the governance it buys.

Beyond the mechanics, the team asked for three things in the follow-up thread:

- **Centralised inference.** ACP calls Bedrock from ACP's own accounts and charges Vulcan back, so
  Vulcan does not have to obtain an AWS workload account with Bedrock access. ACP supports this
  pattern but has never run it — every use case so far has been AgentCore or Bedrock over
  hub-and-spoke, so Vulcan would be the first.
- **Provider insulation.** If a better commercial position appears — Anthropic direct, or via
  Microsoft — the switch happens in ACP configuration, not in Vulcan.
- **Usage data good enough to charge back on.** Vulcan expects ACP to expose per-run token and
  cost data; the recovery model to individual consuming teams stays with Vulcan and Finance.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| Patrick Dufour | Vulcan product and engineering owner | Getting inference and governed tool access without a second onboarding programme; not missing the September window |
| Lalit Summan | ACP delivery | Requirements captured, backlogged and sequenced against the rest of the ACP roadmap |
| Seth Rider | ACP architecture | That the governance claim ACP makes on Vulcan's behalf is one the platform can actually honour |
| Gregory Cheng | ACP gateway and MCP | That brokering registered MCP connections does not quietly become ACP hosting other teams' tools |
| Anirban Mukherjee, Robert Cordeiro | Value measurement | A defensible baseline for remediation cost, engineer time avoided, speed and scale |
| Manan Kshatriya | Cloud FinOps | Any new Bedrock chargeback model has to reconcile with the existing automated CloudWatch-to-cost-centre distribution |
| Vulcan consuming squads | Engineers reviewing the pull requests | Remediation quality; the review burden not going up |

## Scope

### In scope

- **Column 1 — approval check at dispatch.** The Orchestration API asks ACP whether the requested
  agent is approved before it creates the Job, replacing the classpath `agents.json` as the
  authority. Includes agreeing the failure posture when ACP is unreachable.
- **Column 2a — inference through the ACP gateway.** A third Vulcan LLM provider behind
  `get_llm()` pointing at ACP's OpenAI-compatible `/llm/v1/chat/completions` endpoint, with the
  Bedrock credential held by ACP rather than by Vulcan.
- **Registration of both Vulcan agents** (`vulcan-modernizer`, `vulcan-sast-fixer`) and the models
  they use, plus the mandatory governance baseline that registration carries.
- **Per-run attribution** — tokens, model and cost attributable to a Vulcan run, and the
  reconciliation between ACP's usage record and the existing AI Agent Usage Metrics API so the two
  do not become competing sources of truth.
- **A chargeback position**: what ACP is accountable for (metering, attribution, the provider
  billing relationship) versus what stays with Vulcan and Finance (recovery to consuming teams).
- **Column 2b — governed tool access, scoped as a design question in D1 and D2.** Establishing
  what ACP can and cannot broker for Bitbucket, Snyk, Checkmarx and Jenkins, and what would have
  to be true for it to become enforcement rather than inventory.

### Out of scope

- **ACP deploying or operating Vulcan's tools or MCP servers.** ACP brokers registered MCP
  connections through its gateway. It does not host Bitbucket, Snyk, Checkmarx or Jenkins, and it
  does not build or run MCP servers in front of them. Whoever owns each tool owns its MCP surface.
- **Rewriting Vulcan's agents.** The integration is at the provider seam and the registry seam.
  The LangGraph graphs, prompts, Java remediation patterns and pull-request logic are untouched.
- **Hardening the Orchestration API beyond the ACP call.** Its own roadmap — caller
  authentication, typed input schemas, digest-pinned images, durable run state, per-run
  authorization — is Vulcan's Phase 1 and 2 work and is documented in its `docs/ARCHITECTURE.md`.
  ACP does not absorb it, though the approval check assumes the caller authentication lands.
- **Continued GitHub Copilot inference for the unattended workload.** Treated as closed, subject
  to the team confirming the licence terms.
- **Changing the AI Agent Usage Metrics API contract.** In scope to reconcile against; out of
  scope to redesign.
- **Non-Java platforms and non-Bitbucket source control.** Vulcan supports Java with Maven or
  Gradle, and Bitbucket Server or TFS. Expanding that is Vulcan's roadmap, not ACP's.

## Capability Requirements

> **Status: proposed, not yet confirmed — carried to [D3 T19](d3-tasks.md).** The
> [D0 process](../../../process/d0-d4-overview.md) requires this table to be filled in *with the
> use case, in session, against named capability IDs* — precisely so that a capability is never
> inferred from a transcript. Everything below is ACP's reading of the three source
> conversations, mapped onto the [ACP Capability Map](../../../capability-map.md).
>
> **D0 was approved on 2026-09-03 on its problem statement, scope and success criteria. The
> capability confirmation was not recorded as part of that approval**, so the table is left
> proposed rather than marked confirmed with a date that cannot be evidenced. Dating it would
> convert an open item into a false governance record, which is the one failure mode this gate
> exists to prevent. It is tracked as T19 and does not block Phase 1.

### Mandatory baseline — acknowledgement pending

Every use case inherits the mandatory capabilities in the capability map whether or not it asks
for them. Three of the sixteen are not enforceable today, and Vulcan needs to hear that directly
rather than discover it at D2.

| Confirmed with | Date | Notes |
|---|---|---|
| *Pending — Patrick Dufour* | *TBC* | Three mandatory capabilities cannot be honoured today. They are platform debt, not Vulcan's: **CAP-11 kill switch** is a status edit, not an incident-response control, and has no design; **CAP-12 quotas** are modelled but nothing debits a counter, so a configured budget holds nothing; **CAP-15 risk tiering** is an attribute nobody derives and nothing acts on. Vulcan should also hear that **CAP-12 has no spend dimension at all** — the enum stops at requests and tokens — so the "set budgets per run" expectation from the inference thread is not available in the current slice. |

### Selected capabilities — proposed

| Capability | Why this use case needs it | Priority | Status today | Confirmed by |
|---|---|---|---|---|
| [CAP-08](../../../capability-map.md#cap-08) — Governed AI gateway | The single egress that replaces Vulcan's direct Bedrock call. Carries every other runtime control, and is what makes provider insulation a config change rather than a code change. | P0 launch | ✅ Available | *Pending* |
| [CAP-02](../../../capability-map.md#cap-02) — Model registry | ACP holds the approved model, the regional offering and the pricing that turns tokens into dollars. The mechanism behind "switch the source of inference transparently". | P0 launch | ✅ Available | *Pending* |
| [CAP-01](../../../capability-map.md#cap-01) — Agent registry | Becomes the authority behind `AgentRegistry.resolve()`. Column 1 of the target journey is exactly this. | P0 launch | ✅ Available | *Pending* |
| [CAP-06](../../../capability-map.md#cap-06) — Machine identity | Both callers are non-interactive: a Spring Boot service asking the registry, and a batch Job calling the gateway. There is no human in either path. | P0 launch | ✅ Available — **but default-off in the Sun Life deployment**; see the D1 gap register | *Pending* |
| [CAP-20](../../../capability-map.md#cap-20) — Observability and cost accounting | The whole measurement ask: provider-reported tokens instead of a `tiktoken` estimate, real cost per run, and the data chargeback is computed from. | P0 launch | ✅ Available — cost-centre chargeback is built; **per-run** cost is not, see the D1 register | *Pending* |
| [CAP-09](../../../capability-map.md#cap-09) — Policy enforcement | Fail-closed authorization on each inference call, so "approved to run" is enforced continuously rather than only at dispatch. | P0 launch | ✅ Available | *Pending* |
| [CAP-18](../../../capability-map.md#cap-18) — Audit trail | The record that a remediation run happened, against which repository, with which model. Underpins the regulatory story the team was asked about in session. | P0 launch | 🟡 Partial — no external-producer path | *Pending* |
| [CAP-13](../../../capability-map.md#cap-13) — Attribute tagging | Cost centre, business area and environment are the tags cost attribution and chargeback grouping run on. | P0 launch | ✅ Available | *Pending* |
| [CAP-03](../../../capability-map.md#cap-03) — MCP tool registry | Column 2's tool half. Conditional-mandatory the moment Vulcan calls any tool through ACP. | P1 fast follow | ✅ Available for registration — **but see the injected-credential gap in D1** | *Pending* |
| [CAP-11](../../../capability-map.md#cap-11) — Kill switch | An agent that edits source and opens pull requests across the estate is exactly the case where stopping it must be an action, not a status edit. Vulcan gets this whether or not it asks. | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-12](../../../capability-map.md#cap-12) — Quotas and budgets | The team asked for per-run budgets in the inference thread. Requires a candid conversation: the authoring model is real, the enforcement is not, and spend is not expressible at all. | P1 fast follow | ⚠️ Modelled, not enforced | *Pending* |
| [CAP-14](../../../capability-map.md#cap-14) — Lifecycle governance | Vulcan's own registry already models `DRAFT`/`ACTIVE`/`DEPRECATED`/`REVOKED`. If ACP becomes the authority, ACP has to carry at least that much lifecycle. | P1 fast follow | 🟡 Partial — no enforced state machine, and the enums do not align | *Pending* |
| [CAP-10](../../../capability-map.md#cap-10) — Guardrails | Prompts carry proprietary source code and vulnerability detail. Mandatory baseline; Vulcan should confirm it understands that request- and response-side scanning applies to its payloads. | P1 fast follow | ✅ Available | *Pending* |
| [CAP-21](../../../capability-map.md#cap-21) — Single pane of glass | How the Vulcan team and its reviewers see runs, spend and policy without building a console. | P2 later | ✅ Available | *Pending* |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation and quality gating | Remediation success rate is one of the team's headline metrics, and an auto-remediating agent is a candidate for pre-production evaluation and drift detection. | P2 later | 🟡 Partial | *Pending* |

### Capabilities offered and expected to be declined

Recorded so the record shows they were put on the table, not overlooked.

| Capability | Why not |
|---|---|
| [CAP-24](../../../capability-map.md#cap-24) — Delegated access and chain authorization | Vulcan is a single agent per run. It does not call another agent and it does not act on a named user's behalf — a run is triggered by a vulnerability list, not by a person's session. Revisit if Vulcan is ever invoked *as* a tool by another agent. |
| [CAP-22](../../../capability-map.md#cap-22) — Federated per-BU gateways | One workload, one gateway. |
| [CAP-25](../../../capability-map.md#cap-25) — JIT and break-glass access | Vulcan's access is scheduled and batch. There is no interactive operator to grant time-bound access to. |
| [CAP-26](../../../capability-map.md#cap-26) — Conditional access and data-flow control | No data-residency driver identified: source code and findings stay inside the Sun Life estate. Re-test if Vulcan ever processes repositories outside Canada. |
| [CAP-23](../../../capability-map.md#cap-23) — Feedback capture | The pull-request review *is* the feedback loop, and it lives in Bitbucket. |

> Any selected capability that is not ✅ becomes a row in the D1 Capability Gaps register and
> follows [Capability Gap Escalation](../../../process/capability-gap-escalation.md). Each one
> then carries an entry in the D1 **Luminate register**, which records what to check in the
> platform, the answer as verified, and what to raise if that answer is insufficient — so a
> shortfall recorded here has a destination rather than stopping at being described.

## Success Criteria

| ID | Criterion | Measurement | Target |
|---|---|---|---|
| SC-1 | Inference is served by ACP | A `vulcan-modernizer` run completes end to end with `llm.provider: acp` and no AWS credential present in the Job pod | One green run in dev, then one against a non-production Sun Life repository |
| SC-2 | Vulcan needs no Bedrock account | The `aws-okta-credentials` Secret is removed from the agent definition and the run still succeeds | Secret absent from `agents.json` for both agents |
| SC-3 | Dispatch consults ACP | The Orchestration API refuses to create a Job for an agent ACP does not report as approved | Deactivate the agent in ACP; the next submit is refused, and the refusal is visible in the run record |
| SC-4 | Tokens are measured, not estimated | Provider-reported input and output tokens for a run, compared against the current `tiktoken` estimate | Both figures recorded for the same run; the variance is quantified rather than assumed |
| SC-5 | Cost is attributable to a cost centre | Period cost for the Vulcan agents, broken out by model and entity, retrieved from ACP without a manual join | One period reconciles to a single figure per cost centre |
| SC-5b | Cost is attributable **to one run** | Cost for a single remediation, joinable to the vulnerabilities that run fixed | One run reconciles to one figure. **Not achievable from the chargeback surface today** — tracked as a platform item in D1, not as a Vulcan build task |
| SC-6 | Provider insulation is demonstrated | The model behind a Vulcan run is changed in ACP configuration with no change to the Vulcan container image | Two consecutive runs on different models from the same image |
| SC-7 | Chargeback has an owner per line item | A written split of ACP responsibilities versus Vulcan and Finance responsibilities, reviewed with Cloud FinOps | Agreed and recorded in D2; no unowned line items |
| SC-8 | The regulatory story holds | Registration, audit and policy records exist for both agents and the models they use | Evidence retrievable from ACP for a named run, with the CAP-11, CAP-12 and CAP-15 gaps explicitly disclosed rather than papered over |

## Dependencies

| Dependency | Component / team | Type | Risk if it slips |
|---|---|---|---|
| Machine-to-machine authentication enabled on the ACP control plane | ACP platform | **Hard** | Column 1 cannot be built. `SERVICE_PRINCIPAL_AUTH_ENABLED` is `false` in every Sun Life environment today |
| A single trusted token issuer covering both parties | ACP platform + Vulcan | **Hard** | ACP's service-principal issuer is one configured value — Keycloak in dev, Authentik in UAT. Vulcan's services hold Okta tokens. Unresolved, this blocks column 1 |
| Bedrock access from ACP's own account, with model access approved | ACP platform + Cloud | **Hard** | Centralised inference has never been run for a real use case; this is its first exercise |
| Caller authentication on the Orchestration API | Vulcan | **Hard** | An approval check in front of an unauthenticated dispatch API constrains very little |
| A chargeback model reconciled with automated Bedrock cost distribution | Cloud FinOps (Manan Kshatriya) | **Hard** | Cost lands in the wrong cost centre and has to be unpicked retrospectively |
| Owners and MCP surfaces for Bitbucket, Snyk, Checkmarx and Jenkins | Respective tool owners | **Hard** for column 2b, soft for launch | Tool governance stays inventory rather than enforcement. ACP does not build these |
| Vulcan's containerised OpenShift deployment | Vulcan | **Hard** | Nothing can be verified against the target runtime |
| The complete vulnerability-source and repository inventory | Vulcan | Soft | Scope stays approximate and the value baseline cannot be set |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **The September fork.** Vulcan ships the interim Bedrock-plus-Okta path if ACP is not ready, and the interim becomes permanent | **High** | **High** | Treat the interim as expected, not as failure. Design the ACP provider so it is additive to the shipped Bedrock provider and switchable by one config key, so migrating later is a flag flip rather than a re-integration |
| ACP is promised as a budget control it cannot yet be | High | High | Say it in the capability conversation, not at D2. CAP-12 resolves quotas but nothing debits, and spend is not an expressible dimension. Offer measurement and alerting now, enforcement when the counter store lands |
| Tool governance is heard as "ACP will front our scanners" | Medium | High | ACP brokers registered MCP connections; it does not deploy or operate tools. Restate the boundary in D1, and be explicit that a PAT-fronted backend cannot be credentialed by the gateway today |
| Issuer mismatch is discovered during build rather than design | Medium | High | Resolve it in D1 as a named requirement with an owner, not as an integration detail |
| Two sources of usage truth | Medium | Medium | Vulcan already publishes to the AI Agent Usage Metrics API. Decide in D2 which system owns tokens and cost and which owns remediation outcomes, and have one read from the other |
| Latency or availability of a network inference hop degrades long batch runs | Medium | Medium | Vulcan runs are already minutes long and dominated by clone, build, test and scan. Measure the delta in the PoC rather than assuming it |
| Guardrails block legitimate payloads — source code and vulnerability detail resemble what scanners look for | Medium | Medium | Exercise real remediation prompts against guardrails during the PoC and tune before wider use |
| An agent that edits source and opens pull requests at scale needs a real stop control, and ACP does not have one | Medium | High | Disclose the CAP-11 gap; agree an interim containment path (deactivate in ACP plus stop dispatch at the orchestrator) and measure how fast it actually takes effect |
| Centralised inference is unproven at ACP | Medium | Medium | Vulcan is the first. Sequence it as an explicit PoC exit criterion rather than an assumption |

## Open Questions

- [ ] **Run the capability confirmation session** — walk the table above with the use case against
      named capability IDs and record the confirmations, priorities and declines. Carried as
      [D3 T19](d3-tasks.md); the only D0 exit condition still open after the 2026-09-03 approval.
- [ ] Which single issuer will ACP trust for machine callers, and does Vulcan's Orchestration API
      obtain a token from it — or does ACP need to accept more than one?
- [ ] What is the failure posture when ACP is unreachable at dispatch: refuse the run, or proceed
      on a cached approval, and for how long?
- [ ] Does the Job pod hold a static agent-scoped API key, or can it obtain a short-lived
      credential? A long-lived key in a Kubernetes Secret repeats the pattern this onboarding is
      trying to retire.
- [ ] Vulcan's registry uses `DRAFT`/`ACTIVE`/`DEPRECATED`/`REVOKED`; ACP uses
      `active`/`inactive`/`deprecated`/`unknown`. Which is authoritative, and how do the two map?
- [ ] Which model and region does Vulcan run on under ACP? The interim path was approved for
      `us-east-2` and `anthropic.claude-opus-4-8`; ACP's Sun Life deployment is `ca-central-1`.
- [ ] Who owns the provider billing relationship? ACP already exposes a chargeback feed as rows, a
      summary and a streaming CSV export, filterable by cost centre — which of those does the
      cost-recovery function actually consume, at what cadence, and keyed on what?
- [ ] Is the first tool to be brokered Bitbucket, and does an MCP server for it exist or need an
      owner?
- [ ] What is the baseline for remediation success rate and engineer time avoided, measured on the
      interactive Copilot version, so the ACP-served version can be compared to something?
- [ ] Confirm the business sponsor and the cost centre that carries Vulcan's inference spend.
- [ ] Does the `executedBy` field in the usage metrics payload — currently undecided and empty —
      become the ACP entity identifier, and does that satisfy per-user recovery?
