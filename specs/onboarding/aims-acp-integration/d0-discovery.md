# AIMS (AI-Powered Incident Management System) - D0: Discovery

> **Gate**: D0 - Discovery | **Status**: In Progress | **Epic**: _(pending)_

---

## Problem Statement

**What pain exists today?**

AIMS currently operates as an isolated incident management platform without centralized governance, observability, or policy enforcement:

- **No unified agent governance** — AIMS agents (RCA, Incident Correlation, Remediation) operate independently without ACP oversight
- **Model integrations not standardized** — Foundation models are consumed via direct integrations instead of through a governed registry
- **Fragmented MCP access** — Enterprise tools (Jira, Knowledge Base, AWS Operations) lack centralized connection management or policy controls
- **No cost visibility** — Operational costs for agent usage, model invocations, and MCP calls are not tracked or attributed
- **Limited audit trails** — Agent decisions and actions lack comprehensive logging for compliance and forensics
- **Custom governance per capability** — Each new agent (Remediation, Orchestration) requires building custom governance instead of inheriting platform controls
- **Autonomous execution risk** — Future Remediation Agent with infrastructure access lacks sufficient approval workflows and oversight mechanisms

---

## Opportunity

**What becomes possible?**

Integrating AIMS with ACP enables:

- **Governed multi-agent architecture** — All AIMS agents registered, monitored, and policy-controlled through ACP
- **Standardized model consumption** — Foundation models consumed through ACP model registry with version control and approval gates
- **Centralized enterprise connectivity** — MCP servers for Jira, Knowledge Base, AWS Ops managed and governed through ACP
- **Financial transparency** — Cost attribution and usage metrics for each agent visible in real-time
- **Comprehensive audit and compliance** — Full audit trail for all agent actions enabling regulatory compliance (SOX, SOC2, etc.)
- **Faster agent onboarding** — New AIMS agents inherit ACP's governance, observability, and controls without rebuilding
- **Safe autonomous operations** — Remediation agents can operate with confidence through ACP approval workflows and policy enforcement
- **Operational intelligence** — Unified dashboard showing agent effectiveness, cost/benefit, and failure patterns

---

## Stakeholders

**Who is impacted and their concerns?**

| Stakeholder | Role | Concern |
|-------------|------|---------|
| **AIMS Product Lead** | Drive AIMS roadmap | Reduce friction for agent onboarding; inherit ACP controls without custom builds |
| **Operations/SRE Team** | Use AIMS for incident diagnosis | Visibility into agent recommendations; confidence in automated remediation decisions |
| **Finance & Cost Management** | Track cloud spend | Understand cost drivers; attribute spend to AIMS agents and models |
| **Security & Compliance** | Audit and governance | Comprehensive audit trails; approval workflows for autonomous actions |
| **ACP Platform Team** | Provide governance infrastructure | Validate AIMS use cases drive ACP feature roadmap; ensure scalability |
| **Data Platform Engineers** | Own AWS Glue infrastructure | Maintain operational control; understand which agents can remediate vs. recommend |
| **Executive Stakeholders** | Cost reduction & reliability | Measure AIMS business impact; ROI on AI-powered operations |

---

## Scope

**What's in and out (explicit boundaries)?**

### **In Scope (MVP)**
- Register AIMS RCA Agent with ACP agent registry
- Register AIMS Incident Correlation Agent with ACP registry
- Migrate foundation model integrations to ACP model registry
- Register MCP servers (Jira, Knowledge Base, AWS Operations) with ACP MCP registry
- Implement cost tracking and attribution per agent
- Full audit trail for all agent executions and decisions
- Basic approval workflow for remediation recommendations (human-in-the-loop)
- Observability dashboard showing agent metrics, health, latency, costs
- Documentation for onboarding new AIMS agents to ACP
- Integration with ACP policies for data sensitivity and access control

### **Out of Scope (Backlog / Phase 2+)**
- Autonomous Remediation Agent execution (currently recommendations-only)
- Self-healing automation based on confidence scoring
- Advanced approval workflows with multi-stakeholder gates
- Cross-product incident correlation (e.g., database failures + application failures)
- Predictive failure detection and prevention (future roadmap)
- Integration with external ticketing systems beyond Jira
- Multi-region AIMS deployment and coordination
- Real-time policy enforcement (reactive monitoring in MVP)
- AIMS-specific memory persistence (use ACP shared memory infrastructure)
- Custom evaluation metrics (use ACP evaluation framework)

---

## Success Criteria

**Measurable outcomes:**

### **For Operations Teams**
- All AIMS agents discoverable and understandable via ACP agent catalogue
- Cost per agent per week visible in unified dashboard
- Remediation recommendations include confidence scores and impact assessment
- Manual approval required and tracked for all remediation actions

### **For AIMS Product**
- New agents can be onboarded to ACP in under 1 day without custom governance code
- Zero custom audit logging code required (inherited from ACP)
- Cost of agent operations reduced through shared infrastructure
- AIMS roadmap progressed from RCA → Correlation → Remediation → Self-Healing

### **For Security & Compliance**
- 100% audit trail coverage for agent decisions and actions
- Policy enforcement for approved models, tools, and data access
- Approval workflow compliance for all remediation actions
- Quarterly audit report showing AIMS activity and governance status

### **For Finance**
- Per-agent cost attribution visible within 1 day of execution
- Model invocation costs separately tracked from MCP call costs
- ROI metrics showing cost savings vs. cloud spend reduction

---

## Dependencies

**Blockers and prerequisites:**

| Dependency | Type | Status | Owner | Impact |
|------------|------|--------|-------|--------|
| **ACP Agent Registry API** | Technical | In progress (ACP team) | ACP Product Lead | Block: cannot register AIMS agents without this |
| **ACP Model Registry** | Technical | Backlog | ACP Product Lead | Block: cannot consume approved models; requires integration design |
| **ACP MCP Registry** | Technical | Backlog | ACP Product Lead | Block: cannot govern MCP server access; requires MCP connector architecture |
| **Cost tracking infrastructure** | Technical | Planning | ACP/AIMS joint | Block: cannot attribute costs without telemetry integration |
| **AIMS agent API definition** | Technical | In progress (AIMS team) | AIMS Lead | Block: agent registration spec requires API contract |
| **Security approval** | Process | Pending | Security & Compliance | Block: need approval for autonomous agent execution framework |
| **Data sensitivity tagging** | Data | Not started | Data Platform team | Block: MCP servers need data sensitivity policy labels |

---

## Risks

**Unknowns and mitigation ideas:**

| Risk | Likelihood | Severity | Mitigation |
|------|------------|----------|-----------|
| **Remediation agent goes rogue** | Medium | High | Implement hard approval gates for any infrastructure changes; require senior engineer approval; start with read-only recommendations only |
| **Cost explosion from model invocations** | Medium | High | Implement rate limiting per agent; set monthly cost budgets; alert on 80% threshold |
| **Latency impact on incident response** | Low | High | Profile ACP gateway latency under load; design agent caching strategy; cache model responses by failure pattern |
| **Audit trail compliance gaps** | Low | High | Validate audit schema with compliance team pre-launch; run audit gap analysis before production |
| **MCP server credential management** | Medium | Medium | Use ACP credential provider; rotate credentials on defined cadence; no credentials in logs |
| **Scalability of multi-agent coordination** | Low | Medium | Load test with 10+ agents; design agent priority queues; implement circuit breakers for cascading failures |
| **Knowledge base staleness** | Medium | Medium | Establish refresh SLA for knowledge base; implement cache invalidation; version knowledge base snapshots |

---

## Next Steps

- **Stakeholder Alignment**: Present D0 to AIMS product team, operations, and finance stakeholders
- **D1 Requirements**: Define agent APIs, model registry integration, MCP server contracts, cost telemetry schema
- **D2 Design**: Architecture diagrams for multi-agent orchestration, MCP server patterns, cost tracking implementation
- **D3 Tasks**: Sprint-ready implementation tasks, integration dependencies, testing strategy
