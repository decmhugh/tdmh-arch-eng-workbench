# MDx (AI-Native SDLC Platform) - D0: Discovery

> **Gate**: D0 - Discovery | **Status**: In Progress | **Epic**: _(pending)_

---

## Problem Statement

**What pain exists today?**

MDx Forge currently operates without centralized governance or observability:

- **Ungoverned model invocations** — Forge directly calls Bedrock models, leaving organizations without centralized policy enforcement or approval gates
- **Audit and compliance risk** — Model invocations leave compliance gaps without audit trails or regulatory evidence for OSFI and NIST requirements
- **Cost tracking blind spot** — Model token usage remains untracked and unattributed, preventing cost attribution to teams, projects, or business units
- **CLI governance exposure** — Forge's agent-based code execution creates risk by operating outside governance frameworks
- **Consumption visibility gap** — Model consumption patterns across teams and business units remain hidden, preventing cost optimization and capacity planning
- **Regulatory compliance risk** — Regulatory compliance evidence is not automatically collected, creating audit trail and reporting gaps
- **Technical debt accumulation** — Each governance requirement forces custom audit/logging solutions, creating inconsistent controls and technical debt

---

## Opportunity

**What becomes possible?**

Integrating MDx with ACP enables:

- **Governed model access** — Route Forge model traffic through ACP gateway with centralized policy enforcement
- **Comprehensive audit trails** — Capture all model invocations with context for regulatory compliance (OSFI, NIST evidence collection)
- **Cost visibility and attribution** — Track model token usage per squad, project, and business unit for chargeback
- **Observability dashboard** — Real-time visibility into Forge model consumption, performance, and governance health
- **Policy enforcement** — Centralized guardrails for model selection, usage limits, and data sensitivity
- **Scalable governance** — Future MDx capabilities (Fleet multi-agent, expanded squads, new business units) inherit ACP governance without custom builds
- **Compliance automation** — Regulatory evidence collection and reporting without manual audit processes
- **Performance insights** — Understand model latency, token efficiency, and cost drivers

---

## Stakeholders

**Who is impacted and their concerns?**

| Stakeholder | Role | Concern |
|-------------|------|---------|
| **MDx Product Lead** | Drive MDx vision for governed SDLC | Validate ACP integration doesn't degrade performance; cost governance unlocks scaling opportunity |
| **SL Canada Tech Leadership** | Sponsor pilot and future expansion | Demonstrate PoC value; establish governance framework for multi-unit rollout; risk management |
| **Finance & Cost Management** | Track cloud spend and implement chargeback | Understand model costs per squad; enable cost attribution and chargeback mechanisms |
| **Compliance & Risk Management** | Regulatory and audit requirements | Capture evidence for OSFI/NIST compliance; maintain audit trail for controlled pilot |
| **ACP Platform Team** | Provide governance infrastructure | Validate model gateway patterns; ensure observability and cost tracking work for SDLC use case |
| **Security & Governance** | Control access and policy enforcement | Ensure CLI-based agent activity is understood; define acceptable automation scope |
| **Pilot Squad Leaders** | Use MDx for software development | Maintain development velocity; avoid governance friction; understand cost impact |
| **Future MDx Users** | Scale MDx across Canada | Inherit consistent governance; no custom audit builds; cost visibility for decisions |

---

## Scope

**What's in and out (explicit boundaries)?**

### **In Scope (MVP/PoC)**
- Route Forge model traffic through ACP gateway
- Implement model governance and policy enforcement (model selection, usage)
- Cost tracking and attribution per model invocation by squad and business unit
- Audit trail collection for all model invocations with decision context
- Observability dashboard showing Forge model usage metrics (tokens, latency, costs)
- Ledger integration between MDx and ACP for comprehensive audit coverage
- PoC validation of agent traffic routing and governance effectiveness
- Documentation and runbooks for future MDx onboarding to ACP
- Performance impact measurement and optimization
- Integration with ACP policies for data sensitivity and access control

### **Out of Scope (Backlog / Phase 2+)**
- CLI-based activity governance (code execution, repository operations) — requires architectural evaluation
- Kill switch and graduated termination capabilities (future production concerns)
- Advanced cost governance with budget controls and spending limits
- Team-level spending limits and cost governance policies
- MCP tool governance for tool registries and tool-level policy enforcement
- Multi-agent governance for Forge Fleet (coordinated multi-agent execution)
- Production deployment and operational readiness
- Multi-region MDx scaling and distributed governance
- Integration with downstream cost management and chargeback billing systems

---

## Success Criteria

**Measurable outcomes:**

### **For MDx Product**
- Forge model invocations successfully routed through ACP gateway without degrading latency
- ACP model governance policies enforced and validated in PoC environment
- Zero custom audit code required (all audit via ACP)
- Future MDx features inherit ACP governance framework automatically

### **For SL Canada Finance & Operations**
- Cost attribution per squad and business unit visible in real-time dashboard
- Cost per model invocation tracked (token usage × model cost)
- Roadmap established for multi-unit chargeback mechanism
- PoC demonstrates cost governance value for scaling decision

### **For Compliance & Risk Management**
- 100% audit trail coverage for all model invocations
- OSFI/NIST compliance evidence automatically collected and available for audit
- CLI governance evaluation complete with technical feasibility documented
- No manual audit processes required for model governance compliance

### **For ACP Platform**
- Model gateway patterns validated for SDLC use case
- Observability infrastructure proven effective for cost and usage tracking
- PoC success demonstrates model governance market fit
- Learnings inform future multi-agent orchestration patterns

### **For Pilot Squads**
- Development velocity maintained (no noticeable latency increase from ACP gateway)
- Cost visibility enables informed model selection decisions
- Governance provides confidence for controlled expansion

---

## Dependencies

**Blockers and prerequisites:**

| Dependency | Type | Status | Owner | Impact |
|------------|------|--------|-------|--------|
| **ACP Model Gateway API** | Technical | In progress (ACP team) | ACP Product Lead | Block: cannot route Forge traffic without this |
| **ACP Policy Engine** | Technical | In progress (ACP team) | ACP Product Lead | Block: cannot enforce model governance without policy framework |
| **Cost tracking infrastructure** | Technical | Planning | ACP/MDx joint | Block: cannot attribute costs without telemetry |
| **MDx Forge API contracts** | Technical | In progress (MDx team) | MDx Product Lead | Block: model routing requires stable Forge model invocation API |
| **Ledger integration design** | Technical | Not started | MDx/ACP technical leads | Block: need to define audit data flow between MDx and ACP |
| **CLI governance evaluation** | Technical | Not started | MDx/ACP architects | Block: CLI governance is key PoC question; requires design work |
| **Compliance & governance approval** | Process | Pending | Security & Compliance | Block: need approval for what constitutes "governed" model usage |
| **Performance baseline** | Operational | Not started | MDx/ACP technical | Block: need to establish acceptable latency for model gateway routing |

---

## Risks

**Unknowns and mitigation ideas:**

| Risk | Likelihood | Severity | Mitigation |
|------|------------|----------|-----------|
| **ACP gateway adds unacceptable latency** | Medium | High | Establish performance baseline in PoC; implement caching strategies; measure impact on squad velocity |
| **Ledger duplication and sync complexity** | Medium | Medium | Design audit data flow carefully; potentially deprecate MDx ledger in favor of ACP; version audit schema |
| **Cost model complexity for chargeback** | Medium | High | Start with simple squad-level attribution; establish cost model evolution roadmap; involve Finance early |
| **CLI governance remains undefined** | High | Medium | Conduct architectural spike; evaluate isolation VM approach; define acceptable automation scope before scaling |
| **Pilot squad adoption resistance** | Low | Medium | Demonstrate zero latency impact; emphasize compliance/risk benefits; involve squads in PoC design |
| **Regulatory requirements emerge unexpectedly** | Low | High | Work with Compliance pre-launch to validate audit schema; build flexibility into design; plan for requirements evolution |
| **Model cost explosion with scale** | Medium | High | Implement rate limiting and cost controls early; set spending alerts; design budget framework for future phases |
| **Integration complexity with pilot-stage platform** | Medium | Medium | Start with PoC scope; avoid over-engineering; plan for refactoring as MDx matures; document technical debt |
| **ACP platform reliability concerns** | Low | High | Validate ACP availability SLA; establish fallback routing; implement circuit breakers; clear runbooks for failures |

---

## Next Steps

- **Stakeholder Alignment**: Present D0 to MDx product team, SL Canada tech leadership, Finance, and Compliance
- **PoC Planning**: Define PoC scope, success criteria, timeline, and pilot squad participation
- **Architecture Review**: Evaluate CLI governance options; design ledger integration; establish performance baselines
- **D1 Requirements**: Define Forge model invocation API contracts, cost tracking schema, audit data model, policy enforcement rules
- **D2 Design**: Architecture diagrams for model gateway routing, cost tracking pipeline, observability dashboards, compliance reporting
- **D3 Tasks**: Sprint-ready implementation tasks, PoC validation checklist, rollback procedures, squad communication plan
