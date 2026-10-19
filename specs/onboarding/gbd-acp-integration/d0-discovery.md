# Onboard Governance-by-Design Agents to ACP — D0 Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Source**: GbD × ACP integration session (Niall, Lalit, Seth, Duncan, Kathryn, Anirban)
> **Related**: [`governance-intake`](../../governance/governance-intake/d0-discovery.md) governs *how risk is
> assessed*; this spec governs *how GbD's own agents get onto the platform*. They are different
> problems and are deliberately not merged.

## Problem Statement

- **Governance-by-Design runs agents that are not themselves governed by ACP** — the intake
  assistant and the AI4EA agent estate call models and tools directly; there is no registration,
  no gateway routing, and no audit ledger entry for the agents that assess everyone else.
- **No named inventory exists.** The specific GbD and AI4EA agents, their owners and their
  onboarding requirements have not been enumerated, so nothing can be converted into engineering
  tickets. This is the single largest blocker and it is an input we do not hold.
- **MCP server routing is undefined for GbD.** GbD agents reach ServiceNow, Archer and internal
  knowledge sources through tooling that is not registered in the MCP registry, so tool calls are
  neither clearance-scoped nor audited.
- **Gateway access has no agreed path.** Whether GbD agents authenticate to the Luminate gateway
  as first-party workloads, via the harness SDK, or through a delegated service identity has not
  been decided — and it changes the onboarding work materially.
- **Architectural review is a hard gate and has not started.** The ACP communication patterns are
  not documented in ServiceNow, ETG assignment is outstanding, and formal approval of the
  integration pattern is required before production onboarding.
- **Two front doors, no decision.** Users may stay in the GbD UI or move into ACP/Luminate. Until
  that is settled, the onboarding surface GbD builds against is unknown.
- **Pilot has a date, dependencies do not.** A GbD pilot is targeted for **mid-October**; the
  dependency chain behind it is unsequenced.

## Opportunity

- **Governance that is itself governed** — the agents performing assessment are registered, routed
  and audited on the same control plane as the workloads they assess, which is the credibility
  argument for the whole programme.
- **Reference onboarding for a governance workload** — GbD is the first use case whose agents read
  and write regulated systems of record (ServiceNow, Archer). Getting its MCP registration and
  clearance scoping right produces the template for ORCC, Waldo and AI4EA.
- **A single approved integration pattern** — one ServiceNow-documented, ETG-approved
  communication pattern that later use cases inherit instead of re-litigating.
- **Closes the loop with `governance-intake`** — GbD agents become both a producer of governance
  data and a consumer of the governance data product (FR-12), exercising that contract for real
  rather than on paper.
- **Mid-October pilot as a forcing function** — a dated, scoped pilot that proves registration,
  routing, audit and the UI handoff end to end.

## Stakeholders

| Stakeholder | Role | Interests |
|---|---|---|
| **Duncan Wyllie (GbD Lead)** | Product Owner | Agent inventory and onboarding requirements; whether the GbD UI remains the front door |
| **Niall** | GbD Delivery | Agent contacts, onboarding requirements, pilot readiness |
| **Kathryn Vandenberg (GbD)** | Governance | Persona definition; consistency across risk domains; UX ownership |
| **Anirban** | Architecture | Deployment architecture, ACP communication patterns, ETG submission and formal approval |
| **Lalit Summan (ACP PO)** | Product | Phased delivery plan, backlog conversion, timeline commitment |
| **Seth Chalmers (ACP Product)** | Implementer | Luminate registration, gateway access, harness integration, API contracts |
| **Pavithra** | ACP Delivery | Conversion of finalized requirements into engineering tickets |
| **AI4EA agent teams** | Consumers | Frictionless onboarding; clear requirements; minimal rework |
| **Enterprise Architecture / ETG** | Approvers | Integration pattern approval; template and standards conformance |

## Scope (MVP)

**In Scope:**

- **GbD + AI4EA agent inventory** — enumerate the agents, owners, contacts and per-agent onboarding
  requirements in a form that converts directly into engineering tickets.
- **Agent registration in Luminate** — register each in-scope agent with owner, environment, risk
  band and lifecycle state, across the environments the agent is promoted through.
- **MCP server registration + routing** — register the MCP servers GbD agents depend on
  (ServiceNow, Archer, knowledge sources), scoped and audited, and route tool traffic through the
  governed gateway.
- **Gateway access pattern** — decide and document how GbD agents authenticate to the Luminate
  gateway (harness SDK vs. first-party workload identity) and implement one path.
- **Promotion lifecycle across environments** — ACP registers agents per environment and tracks
  promotion; define the states and who authorises each transition.
- **Audit logging** — every GbD agent invocation and tool call lands in the audit ledger.
- **Architectural review package** — document the ACP communication patterns in ServiceNow, assign
  ETG and user information, and obtain formal approval of the integration pattern.
- **UI handoff decision + design** — settle whether users remain in the GbD UI or move into
  ACP/Luminate, and specify the API handoff. *(Design work tracked in
  [`governance-intake-ui`](../governance-intake-ui/d0-discovery.md); the decision is an input here.)*
- **Mid-October pilot** — a named subset of GbD agents onboarded end to end.

**Out of Scope (Backlog):**

- The risk-assessment process itself — questionnaire, obligations, bands, evidence — owned by
  [`governance-intake`](../../governance/governance-intake/d0-discovery.md) and
  [`governance-content-packs`](../../governance/governance-content-packs/d0-discovery.md).
- Archer bi-directional sync — [`archer-grc-sync`](../../integration/archer-grc-sync/d0-discovery.md).
- Building GbD's assessment module or risk-scoring engine — GbD's own build; ACP integrates via API.
- **Imagineers integration pattern** — refined in its own workshop and explicitly **non-blocking**
  for this work.
- Onboarding non-GbD use cases — `aims`, `mdx`, `nova`, `orcc`, `waldo` have their own specs.
- Multi-region deployment of GbD agents.

## Success Criteria

- ✅ **Named agent inventory delivered** — GbD and AI4EA agents, owners and contacts documented and
  converted into engineering tickets on the ACP backlog.
- ✅ **In-scope agents registered in Luminate** with owner, environment and lifecycle state visible
  in the catalog.
- ✅ **MCP servers registered and routed** — GbD tool traffic flows through the governed gateway;
  no direct, unaudited tool calls remain for onboarded agents.
- ✅ **Gateway access pattern implemented** — one documented authentication path, working in dev.
- ✅ **Promotion lifecycle demonstrated** — an agent promoted between environments with the
  transition recorded.
- ✅ **Audit ledger populated** — invocations and tool calls retrievable per agent.
- ✅ **Integration pattern formally approved** — ServiceNow documentation complete, ETG assigned,
  approval obtained.
- ✅ **UI handoff decided** — front-door decision recorded, API handoff specified.
- ✅ **Mid-October pilot live** — the named pilot subset running under ACP governance.

## Dependencies

**Critical blockers:**

1. **Agent inventory and onboarding requirements** *(Duncan, Niall)* — the specific agents,
   contacts and requirements. **Nothing downstream can be ticketed without this.**
2. **Architectural review + deployment architecture clarification** *(Anirban, Lalit)* — the ACP
   onboarding use case and deployment architecture, and the review it must pass.
3. **Integration pattern approval** *(Anirban, Seth)* — ServiceNow documentation, ETG and user
   assignment, formal sign-off.
4. **Front-door / persona decision** *(Duncan, Kathryn, Seth)* — whether the GbD UI stays the entry
   point and how ACP capabilities are reached through APIs.
5. **Luminate dev availability** — [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md)
   (EACPP-596) must expose registration, gateway and catalog APIs in the pilot environment.
6. **Gateway auth path** — Luminate Bearer-JWT client credentials, and whether the harness SDK's
   Luminate target ([`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md),
   EACPP-707) is required first.
7. **MCP server ownership + metadata** — owners, access scope and classification for each MCP
   server GbD depends on.
8. **Model-risk governance alignment** *(Seth, Kathryn)* — continuing cross-functional discussion
   with risk and compliance stakeholders.

## Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **Agent inventory not delivered in time** | Pilot slips; nothing can be ticketed | High | Named owners (Duncan, Niall) with a date ahead of the mid-October pilot; start with one agent rather than waiting for the full list |
| **Architectural review gates the pilot** | Onboarding blocked on approval | Medium-High | Start the ServiceNow pattern documentation now, in parallel with build; treat dev onboarding as pre-approval work |
| **Front-door decision reopens after build starts** | UI and API handoff rework | Medium | Force the decision in the dedicated UI session before implementation; record it as an ADR |
| **Harness SDK Luminate support not ready** | GbD agents cannot authenticate cleanly | Medium | Sequence behind EACPP-707, or use direct client-credentials as an interim with a documented migration |
| **GbD agents reach regulated systems through unregistered tools** | Governance gap persists in the governance function itself | Medium | MCP registration is in the pilot scope, not deferred |
| **Two teams govern the same agent from different systems** | Duplicate or conflicting state | Medium | Reuse the reporting scope boundary already agreed in `governance-intake` T9/D7 |
| **Mid-October pilot scoped too broadly** | Date missed | Medium | Pilot is a named subset, not the estate |
| **Imagineers workshop pulls scope in** | Distraction from the pilot | Low | Explicitly non-blocking; tracked separately |

## Next Steps

| Milestone | Owner | Action |
|---|---|---|
| **Agent inventory + onboarding requirements** | Duncan, Niall | Provide agents, contacts and requirements for ticket conversion |
| **Architectural alignment** | Anirban, Lalit | Clarify onboarding use case + deployment architecture; confirm the required review |
| **Governance UX / front door** | Duncan, Kathryn, Seth | Define personas and end-to-end experience; decide whether the GbD UI remains the front door |
| **Integration pattern approval** | Anirban, Seth | Document ACP communication patterns in ServiceNow; assign ETG; obtain approval |
| **Model-risk governance alignment** | Seth, Kathryn | Continue cross-functional alignment with risk and compliance |
| **Backlog conversion** | Lalit, Pavithra, Seth | Convert finalized requirements into engineering tickets |
| **Imagineers integration pattern** | Anirban, Niall, Duncan | Refine at the scheduled workshop — non-blocking |
| **Biweekly coordination cadence** | Anirban, Niall | Standing touchpoint to track progress and resolve overlaps |
| **GbD pilot** | GbD + ACP | Mid-October — named agent subset onboarded end to end |

## References

- Onboarding path + harness usage: [ACP Onboarding Guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-onboarding-guide/bb-pages/browse/)
- Luminate user guides: [`EDAEACP/luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse)
- Harness SDK: [`T1KACP/acp-harness-sdk`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-harness-sdk/browse) ·
  [user guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-harness-sdk/bb-pages/browse/user-guide/)
- Related specs: [`governance-intake`](../../governance/governance-intake/d0-discovery.md) ·
  [`governance-intake-ui`](../governance-intake-ui/d0-discovery.md) ·
  [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md) ·
  [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md)
