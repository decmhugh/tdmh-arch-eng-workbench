# Anthropic Client Product & ACP Integration

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: EACPP-1319

## Business Overview

Sun Life teams want to use Anthropic client products for knowledge work beyond software development. The initial use cases include spreadsheet analysis, presentation work, document and content work, and related activities performed by financial and other business teams.

The first phase includes **Claude Code, Claude Cowork, Claude Chat, and related Microsoft Office add-ins** installed on users' local machines. The products support third-party inference, allowing their model traffic to be routed through ACP rather than allowing uncontrolled direct calls. In this use case, non-production refers to the data boundary: no customer data and no substantive PII. Real employees are in scope from October 31, using approved knowledge-work content; incidental employee PII, such as a name, email address, or phone number appearing in code or a document, is acceptable.

### Business Value

- **Enable governed knowledge work** — Give teams access to Claude capabilities for spreadsheet, presentation, analysis, and other knowledge-work activities through a controlled enterprise path.
- **Centralize inference** — Route model calls through a common inference path instead of allowing each workload account or user group to manage separate direct Bedrock calls.
- **Improve financial visibility** — Establish a basis for understanding which teams and users generate inference usage and how token costs should be attributed.
- **Support chargeback** — Create the information needed to allocate centralized inference costs to the appropriate workload, team, or business area.
- **Reduce onboarding friction** — Provide a repeatable ACP path for Claude client products and their Office integrations.

## Cost Centre and Chargeback Model

Chargeback is a stated requirement of the use case, not only a future enhancement. The intended access model is that an AVP requests access for staff, usage is approved, and the resulting cost is attributed to the relevant cost centre. The Anthropic usage does not create a new vendor bill; the inference remains part of the existing AWS bill.

Two allocation mechanisms were identified for further design:

- **Central workload-account model** — Bedrock charges land in one workload-account cost centre, then downstream redistribution maps AD group to user and user to cost centre.
- **Existing AWS chargeback pipeline** — Reuse the existing workload-account chargeback pipelines so the App Tuner single-view experience continues to work.

Potential sources for the user-to-cost-centre mapping include ServiceNow, SailPoint, or Ariba, using the ACF2 ID as the lookup key. The chargeback ownership discussion identified Ellis and Corporate Finance, Kathy Kwan and the Finance Expense Management team, and Manan / Cloud FinOps as relevant owners or stakeholders.

## Governance Need

The basic governance requirement is to send Anthropic client model calls through ACP. Users need a control mechanism that determines who can access the products and ensures that the calls use the approved enterprise inference path.

- **Access control** — The desired direction is authentication through an AD group or a similar enterprise identity mechanism; the exact implementation remains to be confirmed.
- **Centralized control** — ACP should provide the governed route for model calls from the Anthropic client products through the ACP gateway endpoint. [CAP-08](../../../capability-map.md#cap-08) Governed AI gateway and [CAP-05](../../../capability-map.md#cap-05) SSO and human identity are the relevant available mandatory capabilities for this path.
- **Local tool-call boundary** — Local, non-MCP tool calls such as reading or writing files remain in scope for normal Claude client operation and must not be blocked or brokered by this initial ACP integration.
- **Data sensitivity** — The first-wave users are expected to work with approved non-PII content, including spreadsheets and presentations. Incidental employee PII, such as a name, email address, or phone number appearing in code or a document, is acceptable. Anything beyond incidental employee PII is outside this initial scope.
- **Phase 1 PII-control assumption** — PII handling is administrative in the initial phase. Users are expected to use the tools responsibly; programmatic gateway-side PII enforcement is explicitly not a day-one requirement.
- **Mandatory capability tension** — The ACP Capability Map lists CAP-10 Guardrails as available and mandatory, including request and response PII scanning with block, redact, and warn outcomes. The sponsor has deprioritized that programmatic enforcement for this first wave, so the exception and follow-up path must remain visible.
- **Risk classification** — The onboarding matrix records an LVT rating of **4**. The corresponding control expectations should be confirmed as the onboarding design progresses.
- **Governance timing** — The ISRA is being prepared for ETAB, with Justin on the ETAB slate for mid-October. The governance work is expected to land toward the tail end of October alongside the centralized-inference target.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| Justin Collery | Architect / point of contact for Claude | Enable the products through ACP from day one and avoid a throwaway gateway |
| Desktop team | Packaging and deployment | Roll out the Anthropic client products and Microsoft Office add-ins |
| Ellis + Corporate Finance | Chargeback ownership | Own the financial back end for cost-centre allocation |
| Manan / Cloud FinOps | AWS chargeback reporting | Pull Anthropic inference costs out of existing workload-account reporting |
| Pavithra Viswanathan | Product owner | Ensure the required governance artefacts are in place |
| Seth Chalmers | Technical lead | Deliver centralized inference and per-user attribution |
| Robert Chin | End-user services / finance routing | Own the billing process and solution ownership |

## Onboarding Assessment

| Area | Assessment |
|---|---|
| Products | Claude Code, Claude Cowork, Claude Chat, and Microsoft Office add-ins |
| Users | Knowledge workers, including financial teams and developers |
| Integration pattern | Existing model-call pattern; no new pattern required |
| Inference path | Claude third-party inference pointed at the ACP gateway endpoint |
| MCP | No MCP integration in the first wave |
| Local tools | Local non-MCP file and workspace tool calls remain enabled and are not brokered by ACP |
| Data | No customer data or substantive PII; incidental employee PII is acceptable within the stated boundary |
| PII enforcement | Administrative human controls in the initial phase; CAP-10 programmatic enforcement is not a day-one requirement |
| Initial phase | Real employees using the desktop-deployed package from October 31; no customer data or substantive PII |
| Connectivity proof | Use Justin's Claude Code installation, point it at the ACP gateway, and prove the routing works |
| Target | October 31 for centralized inference |
| LVT | 4 |

## Scope

### In Scope

- **Anthropic client product onboarding** — Establish the ACP path for Claude Code, Claude Cowork, Claude Chat, and the related Office add-ins.
- **Centralized model routing** — Route product model calls through ACP using the existing third-party inference capability.
- **Local non-MCP tool use** — Preserve normal local file and workspace tool calls, including read and write operations; these calls must not be blocked or routed through MCP as part of this phase.
- **Initial-phase validation** — Validate the integration with real employees using approved knowledge-work content, with no customer data or substantive PII; incidental employee PII remains permitted within the stated boundary.
- **Initial PII-control posture** — Record the administrative human-control assumption for Phase 1 and the later follow-up needed for CAP-10 request and response scanning.
- **Enterprise access control** — Define how user authentication and authorization will work, including the proposed AD-group approach.
- **Routing and connectivity proof** — Use Justin's Claude Code installation, point it at the ACP gateway, and prove that the model-call path works.
- **Usage and cost visibility** — Identify the usage data needed to understand token consumption and support chargeback decisions.
- **October 31 target** — Prepare the centralized-inference path for the stated target date.

### Out of Scope

- **Customer-data workloads** — Customer data and substantive PII workloads are not included in this initial phase. Real employee users and live cost-centre chargeback are in scope from October 31.
- **Microsoft Copilot Cowork** — Copilot Cowork is not included in this initial phase. The scope covers the Anthropic Claude client products and their Office add-ins only; any Copilot Cowork control-plane or billing treatment requires separate clarification.
- **MCP integration** — No MCP servers or remote MCP tools are included in the initial onboarding scope. This does not exclude local, non-MCP tool calls required by the client products.
- **Substantive PII workloads** — The initial scope excludes substantive PII. Incidental employee PII, such as a name, email address, or phone number appearing in code or a document, is permitted within the agreed boundary.
- **Final chargeback design** — The onboarding should identify the required cost and usage information, but the final ownership and allocation model remains to be determined.
- **Provider expansion** — The immediate path remains Bedrock direct; adding another inference provider is not part of this first wave.

## Capability Requirements

At D0, the capability discussion remains high level. Detailed capability mapping and enforcement design should be confirmed during D1.

- **Governed model routing** — ACP must provide the controlled path for Anthropic client model calls.
- **Identity and access** — The onboarding needs a confirmed user authentication and authorization approach, potentially based on an AD group, using [CAP-05](../../../capability-map.md#cap-05) SSO and human identity.
- **Gateway integration** — Point the Claude third-party-inference setting at the ACP gateway endpoint using [CAP-08](../../../capability-map.md#cap-08) Governed AI gateway.
- **Centralized inference** — The model-call path must support centralized inference across the participating workload accounts or user groups.
- **Usage and cost telemetry** — The path should expose enough usage information to support token-cost visibility and the chargeback model.
- **Cost accounting and chargeback** — Build on CAP-20, which the ACP Capability Map marks as available and mandatory, to expose usage and pricing data needed for cost-centre attribution and downstream chargeback.
- **Capability status** — Do not assume the ACP evaluation capability is available for this phase; CAP-17 is partial and remains a separate P1 capability gap.
- **PII guardrails** — CAP-10 is available and mandatory in the capability map, but its programmatic enforcement is not required on day one for this initial phase; the D1 plan must address the resulting control gap.

## Dependencies

| Dependency | Owner / Area | Status |
|---|---|---|
| Centralized inference path through ACP | ACP Product Team | In progress |
| User authentication and access-control approach | ACP Product Team + Desktop / Identity teams | To be confirmed |
| Model and inference account arrangement | ACP Product Team + platform owners | To be confirmed |
| Token usage, pricing, and cost-centre attribution data | ACP Product Team + financial / platform owners | To be defined |
| ISRA and ETAB governance | Product and governance stakeholders | ISRA in progress; ETAB slot targeted for mid-October; completion expected toward end of October |
| CAP-10 PII guardrail follow-up | ACP Product Team + governance stakeholders | Mandatory capability available; programmatic enforcement deferred for Phase 1 |
| CAP-20 observability and cost accounting | ACP Product Team + Cloud FinOps / Finance Expense Management | Available and mandatory; allocation design to be confirmed |
| Claude Code installation and ACP gateway connectivity proof | Justin Collery + ACP Product Team | To be demonstrated |
| CAP-17 Evaluation, quality gating and assurance | ACP Product Team | Partial; build in flight and not assumed available for this phase |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| User authentication and ACP access control are not agreed | Medium | Medium | Confirm the identity and access approach before centralized inference onboarding |
| Centralized inference does not provide sufficient usage data for chargeback | Medium | Medium | Define the minimum token, user, team, and workload attribution data needed for the first wave |
| Cost-centre allocation is not traceable from user activity | Medium | High | Define the mapping from AD group and user through ACF2 ID to cost centre, using an approved source such as ServiceNow, SailPoint, or Ariba |
| The allocation mechanism does not preserve existing financial reporting | Medium | Medium | Compare the central workload-account redistribution model with the existing AWS chargeback pipeline and App Tuner single view |
| ISRA and ETAB governance are not complete by the target | Medium | Medium | Track the ISRA, mid-October ETAB slot, and remaining governance work alongside the October 31 centralized-inference target |
| Client product or Office add-in routing differs from the expected API path | Low | Medium | Start with Justin's Claude Code installation, point it at the ACP gateway, and prove the routing path before extending validation |
| Administrative PII controls are insufficient for actual usage | Medium | High | Keep Phase 1 limited to real employee users, no customer data, and the stated incidental-PII boundary; define the CAP-10 follow-up before broader data use |

## Success Criteria

| Criterion | Target |
|---|---|
| Anthropic client products can route model calls through ACP | Claude Code, Claude Cowork, Claude Chat, and the in-scope Office add-ins validated |
| Access is controlled | An approved user authentication and authorization path is documented and tested |
| Initial-phase integration is demonstrated | Real employees can route model calls through ACP by October 31 using approved content with no customer data or substantive PII |
| Routing and connectivity are proven | Justin's Claude Code installation successfully routes model calls through the ACP gateway |
| Usage visibility is established | Token, pricing, user, workload, and cost-centre information is available at a level that supports chargeback |
| Scope remains controlled | No MCP integration or customer-data workload; substantive PII is excluded while real employee users and incidental employee PII remain within the agreed boundary |

## Open Questions

- [ ] Which Anthropic client products and Office add-ins are included in the initial validation set?
- [ ] How will users authenticate to the client products and be authorized to use the ACP route?
- [ ] Will centralized inference use one shared workload account or multiple workload accounts?
- [ ] Which chargeback mechanism will be used: central workload-account redistribution or the existing AWS workload-account chargeback pipeline?
- [ ] Which approved source will provide the user-to-cost-centre mapping: ServiceNow, SailPoint, Ariba, or another source keyed by ACF2 ID?
- [ ] How will costs be attributed to an agent identity when the workload is initiated by an agent rather than a human user and therefore cannot be resolved through a person-based cost-centre lookup?
- [ ] How will ownership be divided among Ellis / Corporate Finance, Kathy Kwan / Finance Expense Management, and Manan / Cloud FinOps?
- [ ] What governance activities remain open, and are they on track for the end-of-October target?
- [ ] What is the detailed control interpretation of the LVT 4 rating for this capability-validation scope?
- [ ] When and how will CAP-10 request and response PII scanning be enabled, given that programmatic enforcement is not required on day one?

## References

- Raw discovery transcript: [anthropic-client-acp-discovery-session.vtt](references/anthropic-client-acp-discovery-session.vtt)
- Readable discovery transcript: [anthropic-client-acp-discovery-session.txt](references/anthropic-client-acp-discovery-session.txt)
- ACP Capability Map: [capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
- Related inference work: [slm-pipeline](../../platform/slm-pipeline/d0-discovery.md)
