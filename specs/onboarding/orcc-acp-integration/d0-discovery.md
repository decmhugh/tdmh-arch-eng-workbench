# ORCC (Operational Risk & Compliance Committee Reporting Agent) - D0: Discovery

> **Gate**: D0 - Discovery | **Status**: In Progress | **Epic**: _(pending)_

---

## Problem Statement

**What pain exists today?**

ORCC risk reporting today is a manual, time-intensive process:

- **Data collection burden** — Risk teams gather data from disparate sources (Archer, ServiceNow, BGRO, SharePoint, S3) requiring weeks of coordinated effort
- **Manual narrative creation** — Subject matter experts manually draft risk narratives, trend analysis, and findings for executive presentations
- **PowerPoint assembly complexity** — Assembling slide decks with standardized formatting, diagrams, and executive commentary is labor-intensive and error-prone
- **Tight reporting deadlines** — Quarterly reporting cycles leave little room for iteration or quality assurance
- **No centralized governance** — ORCC reporting agents operate without unified policy controls, data access restrictions, or unified oversight
- **Lack of observability** — No visibility into agent-generated content quality, execution metrics, or decision rationale
- **No audit trail** — Report creation, content generation, and human approvals lack comprehensive logging for compliance and forensics
- **Cost invisibility** — Model invocations and agent resource usage are not tracked or attributed

---

## Opportunity

**What becomes possible?**

Integrating ORCC with ACP enables:

- **Automated data integration** — MCP-governed access to enterprise data sources (Archer, ServiceNow, BGRO, SharePoint, RDR)
- **Intelligent content generation** — Foundation models sourced through ACP registry generate baseline narratives, summaries, and slide content
- **Orchestrated reporting workflow** — Multi-agent system coordinates data ingestion, analysis, slide mapping, and assembly under ACP governance
- **Reduced manual effort** — Risk teams focus on review and refinement instead of data collection and slide assembly (70% time savings target)
- **Comprehensive audit trail** — All data access, agent decisions, model invocations, and approvals logged for compliance and forensics
- **Unified observability** — Real-time dashboard showing agent execution, content quality metrics, approval status, and operational health
- **Financial transparency** — Cost attribution per agent per reporting cycle enables capacity planning and ROI analysis
- **Faster agent onboarding** — New reporting agents (trend analysis, advanced reasoning, etc.) inherit ACP controls without rebuilding governance

---

## Stakeholders

**Who is impacted and their concerns?**

| Stakeholder | Role | Concern |
|-------------|------|---------|
| **ORCC Risk Team Lead** | Drive risk reporting process | Reduce manual effort; accelerate delivery timelines; maintain quality and accuracy |
| **Data Stewards/Analytics Team** | Manage data quality and integration | Reliable data ingestion from sources; version control; audit trail for data lineage |
| **Finance & Compliance Officer** | Regulatory and audit requirements | Comprehensive audit trail; policy enforcement; data access controls; compliance reporting |
| **ACP Platform Team** | Provide governance infrastructure | Validate enterprise reporting use case; ensure multi-agent orchestration patterns work at scale |
| **Chief Risk Officer** | Executive risk oversight | Faster insights; confidence in AI-generated narratives; transparent decision-making |
| **IT & Security** | Manage enterprise data access | Control access to sensitive risk data; credential management for MCP servers; encryption at rest/transit |
| **Finance & Budget Management** | Track cloud and model costs | Understand cost drivers for AI-powered reporting; ROI on agent platform investments |

---

## Scope

**What's in and out (explicit boundaries)?**

### **In Scope (MVP)**
- Register ORCC orchestrator agent with ACP agent registry
- Register specialized worker agents (data ingestion, slide mapping, content generation, assembly) with ACP registry
- Migrate foundation model integrations to ACP model registry
- Register MCP servers for enterprise data sources (SharePoint, Archer, ServiceNow, BGRO)
- Implement AI-assisted baseline narrative generation
- Conversational refinement of slide content (human-in-the-loop)
- Full audit trail for all generated content and human approvals
- Observability dashboard showing agent execution metrics and content quality
- Cost tracking and attribution per agent per reporting cycle
- Documentation for onboarding new ORCC reporting agents to ACP
- Integration with ACP policies for data sensitivity and access control

### **Out of Scope (Backlog / Phase 2+)**
- Risk Data Repository (RDR) deep integration (phase 2 roadmap)
- Quarter-over-quarter trend analysis and comparative insights
- Enhanced reasoning and explainability for risk narratives
- Autonomous report generation and distribution without human review
- Multi-stakeholder approval workflows with escalation and delegation
- Integration with downstream capital allocation and risk management systems
- Predictive risk pattern detection and forward-looking scenario analysis
- Real-time continuous data synchronization (batch processing in MVP)
- Multi-language reporting (English-only in MVP)
- Mobile/remote access to reporting workflows

---

## Success Criteria

**Measurable outcomes:**

### **For Risk Teams**
- Quarterly reporting deck generation reduced from 4-5 weeks to 1-2 weeks (70% time savings)
- AI-generated baseline narratives reduce manual drafting effort by 60%
- All ORCC agents discoverable and monitored via ACP agent catalogue
- Conversational slide refinement enables rapid iteration without re-generation

### **For ORCC Product**
- All ORCC agents (orchestrator, data ingestion, slide mapping, content generation, assembly) registered with ACP
- New reporting agents can be onboarded in under 1 day without custom governance builds
- Zero custom audit logging code required (inherited from ACP)
- Model usage and costs visible per reporting cycle

### **For Security & Compliance**
- 100% audit trail covering data access, agent decisions, model invocations, and approvals
- Policy enforcement for approved models, data sources, and MCP servers
- Compliance reports generated automatically for regulatory audits
- Data sensitivity labels enforced on all MCP server access

### **For Finance**
- Per-agent cost attribution visible within 1 day of reporting cycle completion
- Model invocation costs separately tracked from MCP data access costs
- ROI metrics showing time savings vs cloud/model spend

### **For Executives**
- Executive dashboard showing quarterly reporting readiness and timeline
- Risk insights delivered 70% faster with auditable AI-generated narratives
- Confidence in report accuracy through comprehensive approval workflows

---

## Dependencies

**Blockers and prerequisites:**

| Dependency | Type | Status | Owner | Impact |
|------------|------|--------|-------|--------|
| **ACP Agent Registry API** | Technical | In progress (ACP team) | ACP Product Lead | Block: cannot register ORCC agents without this |
| **ACP Model Registry** | Technical | Backlog | ACP Product Lead | Block: cannot consume approved models; requires evaluation framework |
| **ACP MCP Registry** | Technical | Backlog | ACP Product Lead | Block: cannot govern enterprise data source access |
| **Audit logging infrastructure** | Technical | Planning | ACP/ORCC joint | Block: cannot meet compliance requirements without audit trail |
| **Data source APIs and credentials** | Technical | In progress (IT team) | IT & Security | Block: MCP connectors require stable API contracts and credential management |
| **ORCC agent API definition** | Technical | In progress (ORCC team) | ORCC Product Lead | Block: agent registration spec requires orchestration and data flow contracts |
| **Policy framework for data access** | Process | Not started | Security & Compliance | Block: need approval for data sensitivity tagging and access controls |
| **Executive stakeholder alignment** | Process | Planning | CRO/CFO | Block: need approval for target timeline and quality expectations |

---

## Risks

**Unknowns and mitigation ideas:**

| Risk | Likelihood | Severity | Mitigation |
|------|------------|----------|-----------|
| **Model hallucinations in risk narratives** | High | Critical | Implement human-in-the-loop review for all generated content; validate against source data; maintain version history |
| **Data quality issues impacting insights** | Medium | High | Implement data validation and cleansing in ingestion agent; audit trail for data lineage; confidence scores on generated content |
| **Incomplete audit trail for compliance** | Low | High | Work with compliance team to validate audit schema pre-launch; test audit coverage with sample reports |
| **Latency in data ingestion delays reporting** | Medium | High | Implement caching and incremental updates; pre-populate baseline data before reporting deadline |
| **Unauthorized access to sensitive risk data** | Medium | High | Use ACP credential provider; implement fine-grained MCP access controls; encrypt data in transit and at rest |
| **Approval workflow bottlenecks under deadlines** | Medium | Medium | Implement escalation paths and parallel approvals; automated routing based on content type and sensitivity |
| **Agent failure cascades during critical periods** | Low | High | Implement fallback strategies; circuit breakers for failed agents; automated retry with exponential backoff |
| **Model vendor cost changes** | Low | Medium | Lock in model pricing or implement cost controls; design for model swapping via ACP registry |
| **Change management resistance from Risk teams** | Medium | Medium | Pilot with early adopter team; demonstrate time savings early; provide training and documentation |

---

## Next Steps

- **Stakeholder Alignment**: Present D0 to ORCC team, CRO, CFO, and compliance stakeholders
- **D1 Requirements**: Define agent orchestration APIs, data flow contracts, model requirements, MCP server patterns
- **D2 Design**: Architecture diagrams for multi-agent reporting workflow, data ingestion pipeline, approval flow
- **D3 Tasks**: Sprint-ready implementation tasks, integration dependencies, testing and validation strategy
- **Pilot Program**: Identify early adopter reporting cycle for MVP validation
