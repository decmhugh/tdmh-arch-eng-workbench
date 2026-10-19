# ACP & Galileo Integration

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1378

## Business Overview

Galileo is an existing platform used by Sun Life Canada (SLC) business users. Its production platform includes Galileo Code, Galileo Gateway, Galileo Workflows, and Galileo Chat. It supports team-scoped access, model selection, skills, MCP connections, agent creation, and multi-agent orchestration. At least two use cases were covered, including a POC; business agents were described as being in UAT, with four use cases identified as candidates for production progression.

The integration is framed as platform-to-platform, not as a one-off agent migration. The initial step is to test model inference through ACP while retaining LightLLM as a transition path; broader Galileo-to-ACP integration is the longer-term goal.

## Business Value

- **Governed Galileo integration** - Provide SLC Galileo use cases with a standard ACP path for model and tool interactions.
- **Reusable onboarding pattern** - Establish an integration approach for Galileo's current and future use cases.
- **Controlled model access** - Use ACP's registered models, application relationships, policies, credentials, and gateway routing.
- **Support current users and future use cases** - Preserve the Galileo experience while expanding governed ACP use.
- **Cost visibility** - Investigate token and LLM costs, account-owner treatment, and user-level attribution.
- **Operational controls** - Assess team/agent budgets, rapid shutdown, log/trace visibility, and treatment of sensitive content.

## Governance Need

The SLC Galileo integration needs a clear boundary between Galileo-owned behavior and ACP-owned governance. ACP provides the path for registering applications, agents, models, and MCP servers; creating policies; issuing credentials; and routing model calls through the gateway.

- **Application and agent registration** - Determine which Galileo applications, agents, and use cases require ACP registration.
- **Gateway routing** - Establish how Galileo calls the ACP gateway and how gateway credentials are used.
- **Phased integration** - Begin with LLM inference through ACP. LightLLM may remain available alongside ACP during transition; coexistence boundaries and cutover criteria are not decided.
- **Policy configuration** - Determine who creates and maintains policies between Galileo applications, agents, models, and governed services.
- **Provider choice** - Confirm whether Galileo initially uses Bedrock models through ACP, the SLC team's own Bedrock account, or another supported path.
- **Production distinction** - The POC is expected to run in development. One use case is already used by people in a production-like manner, and both use cases were targeted for production by the end of Q4, subject to governance approval.
- **Governance approvals** - ATG and ISRA are part of the path toward production.
- **Data protection expectation** - Current use cases were described as internal and without PII. A future PII use case was raised, with an expectation that sensitive input be protected before reaching an LLM; whether ACP can provide the requested redaction behavior is unresolved.
- **Automatic model routing** - Galileo raised interest in routing requests to an appropriate model, including fallback behavior. The required decision logic and ACP support remain to be assessed.

## Scope

### In Scope for D0

- SLC Galileo's current platform, skills, runtime, and multi-agent use-case boundary.
- The two use cases, including the Galileo POC.
- Current Galileo team, skill, MCP, agent, and runtime workflows that interact with ACP.
- ACP application, agent, model, and MCP-server registration questions.
- Gateway routing, policy configuration, credentials, and provider/account topology questions.
- An initial ACP LLM-inference trial and LightLLM coexistence during transition.
- Cost, token usage, account-owner billing, and user-level chargeback questions.
- Team/agent budgets, rapid disable expectations, log/trace visibility, and PII handling expectations.
- Production-readiness questions for monitoring, assessments, governance, and support.

### Not Decided in D0

- Final Galileo architecture or deployment design.
- Final model/provider and Bedrock account arrangement.
- Final policy, credential, and application-administration ownership model.
- Final chargeback mechanism and user-level attribution approach.
- LVT rating for the use cases.
- Detailed milestone plan beyond the end-of-Q4 target.

## Onboarding Assessment

| Area | Assessment |
|---|---|
| Subject | Existing SLC Galileo platform and its use cases |
| Current users | SLC business users are already using Galileo |
| Production platform | Galileo Code, Galileo Gateway, Galileo Workflows, and Galileo Chat were described as in production |
| Use cases | At least two, including a Galileo POC and a broader production direction |
| Agent state | Business agents were described as in UAT; four use cases were identified as production candidates |
| Team/model access | Teams have roles/privileges; model access is associated with teams |
| Agent credential | Agent creation generates a virtual key associated with its team and inheriting team model access |
| Skills workflow | Skills are stored in a Galileo Skills Git repository with environment branches; a PR/review flow allows approval and merge before skills are available for agent creation |
| MCP workflow | Administrators register/expose MCP servers and grant them to teams; users may connect an account/tenant when the MCP requires user authentication |
| Agent execution | Chat can route a request to a matching skill; a sandbox runner clones the skill, fetches files, executes it, and disposes of the sandbox |
| Runtime scale | Galileo described EKS container execution with warm worker slots and overflow containers for concurrent requests; the demonstrated slot count is an example, not a capacity commitment |
| ACP integration path | Initial LLM inference through ACP, with LightLLM retained as a possible transition option; broader integration remains a target |
| Provider options | Bedrock through ACP, the SLC team's own Bedrock account, and other provider options |
| POC state | Development POC |
| Production direction | One use case is already used in a production-like manner; both use cases targeted for production by end of Q4 subject to governance approval |
| LVT | Not determined in the source material |
| Cost | Exact token/LLM cost, account-owner billing, and user-level attribution remain open |
| Requested controls | Budgets, shutdown behavior, PII handling, logs/traces, and automatic model routing require discovery; they are not confirmed ACP features or commitments |

## Capability and Design Questions

- Application, agent, model, and MCP-server registration.
- Identity and credentials for calls into the gateway.
- Policies between applications, agents, models, and governed services.
- Gateway routing and provider/account topology.
- Monitoring, metrics, and evaluation frameworks.
- Production assessments and governance approvals.
- Token cost, account-owner billing, and user-level attribution.
- Team/agent budgets and shutdown expectations.
- PII redaction behavior and log/trace treatment across Galileo and ACP.
- Automatic model selection/routing and fallback behavior.
- LightLLM/ACP coexistence and transition approach.
- Mapping Galileo team/model permissions, virtual keys, skill approvals, authenticated MCP connections, sandboxed skill execution, and memory scopes to ACP governance.
- Scale registry needs: the deep dive noted that this capability was not then available in Luminate and was described as upcoming; roadmap and interim approach need confirmation.

## Capability Map Exposure

The capabilities below are the relevant Luminate surfaces for Galileo. Status and governance overlays are taken from the repository capability map; this D0 does not assume that every capability is complete or that every conditional capability applies.

| Capability | Status | Governance overlay | Galileo implication |
|---|---|---|---|
| [CAP-01](../../../capability-map.md#cap-01) - Agent Registry | Available | Mandatory | Register Galileo agents and owners where the integration governs agents directly. |
| [CAP-02](../../../capability-map.md#cap-02) - Model Registry | Available | Mandatory | Register and select the approved model/provider path. |
| [CAP-03](../../../capability-map.md#cap-03) - MCP Tool Registry | Available | Conditional - mandatory if Galileo calls MCP tools | Apply if the Galileo use case uses registered MCP servers or tools. |
| [CAP-05](../../../capability-map.md#cap-05) - SSO and human identity | Available | Mandatory | Establish attributable human access and identity federation. |
| [CAP-06](../../../capability-map.md#cap-06) - Machine identity and programmatic access | Available; hardening in flight upstream | Mandatory | Define the non-human identity used by Galileo services and applications. |
| [CAP-07](../../../capability-map.md#cap-07) - RBAC and access policy | Available | Mandatory | Govern application, agent, model, and tool relationships through policy. |
| [CAP-08](../../../capability-map.md#cap-08) - Governed AI gateway | Available | Mandatory | Route applicable Galileo model and tool calls through the ACP gateway. |
| [CAP-14](../../../capability-map.md#cap-14) - Lifecycle governance and approvals | Partial | Mandatory | Define assessment, approval, promotion, suspension, and production-readiness gates. |
| [CAP-17](../../../capability-map.md#cap-17) - Evaluation, quality gating and assurance | Partial - build in flight | Conditional - mandatory where the use case makes or influences a customer-affecting decision | Confirm the evaluation and quality-gating approach for Galileo before production promotion. |
| [CAP-20](../../../capability-map.md#cap-20) - Observability and cost accounting | Available | Mandatory | Capture traces, usage, token costs, and attribution data for monitoring and chargeback. |

## Open Questions

- What is the exact boundary of each SLC Galileo use case and which is the initial POC?
- Which Galileo components are applications, agents, orchestration services, skills, or runtime infrastructure?
- Which Galileo calls must route through ACP and which remain local to the platform?
- Which models and providers are required first, and which Bedrock account owns the model calls?
- Which ACP objects must be registered for the first use case?
- Who owns policy creation, credential lifecycle, application administration, and production support?
- What monitoring, assessment, and evaluation approach will be used?
- What are the ATG and ISRA requirements and their expected completion timing?
- How will ACP service charges, token/LLM costs, account-owner billing, and user-level attribution be handled?
- What LVT rating applies to each use case?
- What should team/agent budgets and rapid shutdown do, and which system owns those controls?
- What PII must be redacted before inference, and which component owns redaction and safe logging?
- What automatic model-routing and fallback behavior is required, and is it provided by Galileo, ACP, or both?
- During transition, when may users use LightLLM versus ACP, and what are the criteria for moving to ACP-only routing?
- How should Galileo's personal, agent, and team memory scopes map to identity, policy, retention, and audit requirements?
- What is the scale registry requirement, and what is the confirmed Luminate delivery timeline or interim design?
- How should Galileo team/model permissions, virtual keys, skills approvals, authenticated MCP connections, and sandboxed skill execution map to ACP registration and policy?
- Which of the listed capabilities are required for each Galileo use case, and which conditional capabilities apply?
- What detailed milestones support the end-of-Q4 production target?

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Galileo's application and agent boundary is unclear | Scope and integration effort cannot be estimated | Confirm the two-use-case boundaries in D1 |
| Provider, Bedrock account, or gateway topology is unresolved | The integration path may be redesigned | Decide the initial provider/account path before detailed design |
| Policy and credential ownership is unclear | Access and onboarding may be blocked | Assign ownership before implementation |
| Production-like use is mistaken for approved production readiness | Required monitoring and governance may be bypassed | Keep the POC, production-like current use, and ACP production readiness distinct |
| Cost and user-level attribution is unresolved | Financial reporting and chargeback remain incomplete | Define usage identifiers and accounting ownership with Finance/platform teams |
| LVT and governance requirements are incomplete | Production promotion may be delayed | Confirm LVT, ATG, ISRA, monitoring, and assessment requirements |
| LightLLM coexistence permits inconsistent policy or logging | Calls may receive different controls or produce fragmented evidence | Define coexistence boundaries and compare gateway policy, redaction, and log handling before broad rollout |
| Galileo capabilities are mistaken for ACP capabilities | Integration scope or platform commitments may be overstated | Keep current Galileo mechanisms separate from ACP support until each mapping is confirmed |
| Scale registry is required before Luminate support is available | The target integration may be blocked or require a workaround | Confirm roadmap timing, requirements, and any acceptable interim approach |

## Success Criteria

| Criterion | Target | Measured at |
|---|---|---|
| Galileo scope is defined | Applications, agents, skills/runtime boundary, models, and two use cases documented | D1 |
| ACP integration boundary is agreed | Registration, gateway, policy, credential, and ownership responsibilities documented | D1/D2 |
| Provider path is selected | Initial model/provider and Bedrock account topology recorded | D1/D2 |
| Production distinction is documented | POC, production-like current use, and ACP production readiness are separately described | D1 |
| Platform transition is defined | Initial inference trial, LightLLM coexistence, and ACP transition criteria are documented | D1/D2 |
| Galileo-to-ACP mappings are agreed | Teams/models, virtual keys, skills, MCP connections, runtime, and memory scopes are mapped to ACP concepts | D1/D2 |
| Governance path is defined | ATG, ISRA, monitoring, assessment, and support requirements documented | D1/D2 |
| PII and routing expectations are resolved | Redaction/log handling and automatic model-routing requirements have an accountable design | D1/D2 |
| Cost direction is agreed | ACP service cost, token/LLM cost, account-owner billing, and user attribution options documented | D1 |

## References

- Raw discovery transcript: [galileo-acp-discovery-session.vtt](references/galileo-acp-discovery-session.vtt)
- Readable discovery transcript: [galileo-acp-discovery-session.txt](references/galileo-acp-discovery-session.txt)
- Raw deep-dive transcript: [galileo-acp-integration-deep-dive.vtt](references/galileo-acp-integration-deep-dive.vtt)
- Readable deep-dive transcript: [galileo-acp-integration-deep-dive.txt](references/galileo-acp-integration-deep-dive.txt)
- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
