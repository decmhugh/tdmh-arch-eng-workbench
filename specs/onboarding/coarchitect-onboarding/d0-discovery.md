# CoArchitect Onboarding — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: see `spec.yaml`
>
> Onboards Enterprise Architecture's **CoArchitect** platform onto ACP (Luminate).
> Scope of this round is the **dev Luminate install only** — tenancy, access and the first
> governed call. Production onboarding is a later, separate decision (D3 T13).

## Problem Statement

CoArchitect is Enterprise Architecture's AI architecture assistant (the AI4EA programme,
tracked in Jira project **DAL2 — DBTS-AI4IT Lane 2**). It generates draft architectures from
certified patterns and prior solutions, carries a Knowledge Studio for approved patterns and
enterprise context, and runs a family of architecture agents (Architecture Agent, Trade-off
Analysis, Documentation / Co-documentation). It is already past the prototype stage:

- **Six containerised services** packaged with Kustomize base/overlays (DAL2-34, ADR-022).
- **Its own Dev and SIT environments** — SIT was promoted in June for EA testers (DAL2-200)
  and is being isolated onto its own MongoDB, S3 and storage (DAL2-143).
- **Okta machine-to-machine auth between its services** (DAL2-105), replacing a hardcoded
  `Bearer internal` fallback that blocked production.
- **Model calls to AWS Bedrock**, with an open question about why the usable context window is
  far below the model's advertised one (DAL2-146).

None of that traffic is governed. The agents and the models they call are not in the
enterprise inventory, their calls do not pass through a policy decision, and there is no audit
or cost record ACP can produce on CoArchitect's behalf. The team asked for ACP access in
DAL2-317 (*Get access to ACP*); until now that produced a sign-in, not a tenancy — a user with
no project binding sees a read-only catalogue and can register nothing.

## Opportunity

- **Inventory by default.** Every CoArchitect agent and the models it uses become registered
  resources with an owner, inside a project that EA controls.
- **One governed egress.** Calls to Bedrock go through the ACP gateway, so policy, guardrails,
  audit and cost attribution apply without CoArchitect building any of them.
- **EA owns its own access.** Razi Chaudhry, as project Owner, grants and revokes teammates
  without coming back to the ACP Product Team.
- **A pattern for architecture tooling.** CoArchitect is a natural consumer of the pattern
  specs ACP is putting in front of EA (e.g. [MCP Server Patterns](../../pattern/mcp-server-patterns/pattern.md)) —
  its Knowledge Studio ingest of approved architecture patterns (DAL2-337) points the same way.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| Razi Chaudhry (Enterprise Architecture) | Business owner; **Owner** of the `CoArchitect` Luminate project | Who can act in the project; that EA can self-serve access |
| Tony Xu | Tech lead / developer; **Administrator** on the project | Registering, deploying and wiring CoArchitect to the gateway without waiting on anyone |
| Partho Mondal | Product / design lead (AI4EA epics); **Editor** on the project | Visibility of what is registered; registration of agents and models |
| Anirban Ukil | Engineer (raised DAL2-317 access); **Editor** on the project | Registration and deployment work |
| ACP Product Team (Seth Chalmers) | Platform owner; provisions tenancy, gateways and the production path | Correct scope of grants; a working first governed call |

## Scope

### In Scope

- A folder **Enterprise Architecture** and a project **CoArchitect** on the **dev** Luminate
  install, with Owner, admin and member bindings for the four named people.
- Handover: portal and gateway addresses, the guides to start from, and what the team can do
  itself versus what comes back to ACP.
- Capability walkthrough against the [ACP Capability Map](../../../capability-map.md).
- Asset inventory, model access path, network reachability, and **one** governed round trip
  from CoArchitect dev through the Dev gateway.

### Out of Scope

- The **production** Luminate install (`slf-eks-t1k-ca-prod`) and its four workload gateways.
  Recorded as the exit decision of this round (D3 T13), not done here.
- Changes to CoArchitect's own architecture, its Okta M2M between its own services, or its
  MongoDB / S3 data tier.
- Governing Knowledge Studio content (patterns, documents) — Luminate has no document or
  retrieval surface; a Bedrock Knowledge Base call would bypass the gateway.

## Capability Requirements

> **Proposed, not confirmed.** Drafted from the DAL2 backlog, not walked with the team. It is
> confirmed — or corrected — in session in D3 **T4**, against named capability IDs, and only
> then does it become the onboarding scope.

### Mandatory baseline — acknowledged

| Confirmed with | Date | Notes |
|---|---|---|
| *pending — D3 T4* | — | CAP-12 quotas/budgets is ⚠️ modelled-not-enforced: no spend cap exists. CAP-11 kill switch and CAP-15 risk tiering deny only under a rule in *enforce* mode. |

### Selected capabilities (proposed)

| Capability | Why this use case needs it | Priority | Status today | Confirmed by |
|---|---|---|---|---|
| [CAP-01](../../../capability-map.md#cap-01) Agent Registry | Architecture agents become inventoried, owned resources | P0 launch | ✅ | — |
| [CAP-02](../../../capability-map.md#cap-02) Model Registry | The Bedrock models CoArchitect calls are in the enterprise inventory | P0 launch | ✅ | — |
| [CAP-05](../../../capability-map.md#cap-05) SSO | Every human action in the project attributable | P0 launch | ✅ | — |
| [CAP-06](../../../capability-map.md#cap-06) Machine identity | The CoArchitect workload authenticates to the gateway as itself | P0 launch | ✅ | — |
| [CAP-07](../../../capability-map.md#cap-07) RBAC and access policy | EA-controlled grants; agent→model policy | P0 launch | ✅ | — |
| [CAP-08](../../../capability-map.md#cap-08) Governed AI gateway | Single egress for Bedrock calls | P0 launch | ✅ | — |
| [CAP-18](../../../capability-map.md#cap-18) Audit trail | Evidence of what each agent called | P0 launch | 🟡 | — |
| [CAP-20](../../../capability-map.md#cap-20) Observability and cost | Per-project cost for EA | P1 fast follow | ✅ | — |
| [CAP-10](../../../capability-map.md#cap-10) Guardrails | PII control on prompts that carry enterprise context | P1 fast follow | ✅ | — |
| [CAP-24](../../../capability-map.md#cap-24) Delegated access | Agents acting for an architect, and agent-to-agent calls between the AI4EA agents | P2 later | 🟡 | — |

### Capabilities explicitly not required

| Capability | Why not |
|---|---|
| — | Nothing declined yet; recorded in T4. |

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| SC-1 Tenancy exists and resolves | Owner/admin/member bindings proven by Rego decision **and** by driving the real portal viewsets, with a negative control | Done 2026-10-01 |
| SC-2 Every member is in | Each of the four signs in and sees `CoArchitect` under `Enterprise Architecture` | 4 / 4 |
| SC-3 Scope agreed | Capability table walked and signed off with Razi and Tony | T4 closed |
| SC-4 First governed call | One CoArchitect agent call through the Dev gateway, with the audit pair and a trace attributed to the project | 1 call, evidenced |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
| Dev Luminate install, portal and Dev gateway | ACP Product Team | Hard | Low — gateway re-probed 401 on 2026-10-01 |
| Network path from the CoArchitect runtime to the dev gateway | CoArchitect / hosting platform | Hard | Medium — unknown which cluster CoArchitect runs in (T8) |
| An approved Bedrock model reachable from the gateway | ACP Product Team | Hard | Low for an approved model; see [GenAI Approved LLMs](https://sunlife.atlassian.net/wiki/spaces/EAP/pages/110211170614) |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Team reads "dev Luminate" as their own SIT and points SIT at it | Med | Med | Handover states the environment mapping explicitly; SIT on the dev install has no public gateway |
| A registered resource lands in the wrong project and is stranded | Low | High | Registration only inside `CoArchitect`; inventory (T5) before registration (T9) |
| Expectation of a spend cap | Med | Med | CAP-12 acknowledged in T4; cost is reported, not capped |
| Context-window ceiling (DAL2-146) attributed to the gateway | Med | Low | Settled in T7 against the model's registered `context_window` / `max_tokens` |

## Open Questions

- [ ] Which cluster and namespace does CoArchitect run in, and through which proxy? (T8)
- [ ] Which of the six services call a model, and which are agents vs applications? (T5)
- [ ] Platform-registered model or CoArchitect's own Bedrock account? (T7)
- [ ] Cost centre for the project? (T6)
