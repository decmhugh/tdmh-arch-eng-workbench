# Luminate Control Plane — D0 Discovery

## Problem Statement

**What pain exists today?**

Sun Life's AI governance landscape has become fragmented across 27+ regulatory frameworks and 14+ internal policies:

- **Compliance requirement fragmentation** — Regulatory obligations (NAIC, OSFI E-23, Colorado CAIA, EU AI Act, HIPAA, NIST, OWASP, Texas TRAIGA, NYDFS, PIPEDA) and internal policies (MBCT, ITR, Tech Architecture, AppSec, Privacy, Logical Access, Data Classification, Business Continuity, Records Management) are scattered across 40+ source documents with no unified platform consolidating them into actionable requirements
- **Manual compliance passport process** — Each new agent deployment requires manual hand-off across six governance tracks (ATG, ISRA, MBCT, PIA, TPRM, Records), with no automated workflow to confirm all tracks are complete before activation
- **No enforcement of risk-tier-driven controls** — Without automated risk classification (AA/A/B/C/D), the platform cannot enforce that high-risk agents have killswitches, human-in-the-loop gates, full-fidelity audit, and PIAs while low-risk agents do not
- **Unscalable manual audit evidence collection** — Compliance reporting requires manual assembly of logs, policy decision records, and validation evidence from disparate systems; no unified audit ledger
- **Lack of automated agent governance gates** — No platform-enforced mechanisms for multi-gateway killswitches, human-in-the-loop holds, key recertification workflows, or purpose-based access control
- **Identity and access control gaps** — AI agents are provisioned as human-like directory accounts rather than purpose-built non-human identities (NHIs) with governed lifecycles
- **No audit trail for compliance evidence** — Compliance decisions (risk tier assignments, policy approvals, validation sign-offs) are not recorded in an immutable, faceted audit ledger discoverable by regulators

---

## Opportunity

**What does Luminate Control Plane enable?**

Luminate Control Plane becomes the **enterprise-wide AI governance and compliance platform** consolidating all regulatory and policy obligations into a unified control plane:

- **Unified compliance requirement registry** — One platform that maps all 27+ regulatory frameworks and 14+ internal policies to specific product controls and artifacts, making the compliance load visible and auditable
- **Automated compliance passport workflows** — New agent registrations trigger T0 triage (GenAI Risk Governance Playbook), automatically routing governance evidence requests to ATG, ISRA, MBCT, PIA, TPRM, and Records tracks; activation blocked until all tracks complete
- **Risk-tier-driven governance enforcement** — Agent risk tier (AA/A/B/C/D) automatically gates killswitch attachment, PIA requirements, validation cadence, audit fidelity, key rotation schedule, and remediation priorities
- **Immutable compliance audit ledger** — All governance decisions (approvals, risk classifications, policy evaluations, audit events) are recorded in an append-only ledger supporting regulatory discovery and incident investigation
- **Graduated governance primitives** — Kill-switches (per-agent / per-project / per-org), human-in-the-loop review gates, automated key recertification workflows, and purpose-based access control (PBAC) prevent uncontrolled agent proliferation and drift
- **Non-human identity lifecycle management** — Agent API keys managed as service accounts with provisioning, recertification, and revocation tracked in enterprise IAM (Okta / Azure AD)
- **Regulatory evidence collection** — Automated dashboard showing compliance status across OSFI E-23, NAIC Model Bulletin, Colorado CAIA, HIPAA, PIPEDA, and internal policy requirements; exportable evidence packs for regulator reviews
- **Multi-jurisdiction policy enforcement** — Deployments in different regions enforce region-appropriate constraints (Colorado consumer notification, Texas discrimination prohibitions, Canadian data residency, HIPAA safeguards)

---

## Stakeholders

**Who is invested in success?**

| Stakeholder | Role | Need |
|---|---|---|
| **Sun Life US BG Technology Leadership** | Strategic sponsor, ATG approver | Platform approval for production deployment; assurance that Luminate meets all regulatory and policy gates before go-live |
| **MBCT Review Track Owner** (Enterprise Risk) | Governance owner | Automated risk classification, tier-driven enforcement, validation workflow integration with MVU |
| **IT Risk Policy Owner** | Platform compliance owner | Demonstration that Luminate platform infrastructure meets Critical Application standards; change management gate enforcement |
| **Privacy & Data Governance** | Data protection owner | PIA gating, data minimization enforcement, cross-border transfer controls, PIPEDA audit trail requirements |
| **Internal Audit & CMRM** (MBCT/Model Validation) | Audit and validation owner | SOX ITGC compliance evidence, monitoring lifecycle, per-agent validation status, audit evidence export |
| **Technology Architecture Office (ATG)** | Architecture governance | Platform design review; approval of MCP, LLM routing, A2A protocol, and federated deployment patterns |
| **Application Security** | Security ownership | SAST/SCA/DAST pipeline confirmation, API security controls, credential management, penetration test requirements |
| **Compliance & Regulatory Affairs** | Regulator liaison | Evidence package for OSFI E-23, NAIC, Colorado CAIA, HIPAA compliance; quarterly regulatory reporting |
| **US DCP Infrastructure Team** | Operational ownership | Once deployed to US DCP, run/operate/incident management responsibilities; feature requests flow through consortium governance |
| **Agent Developer Teams** | End users | Simplified governance workflow; clear risk tier definitions; fast path for Level D internal agents; approval gates for Level A/AA customer-facing agents |
| **FCP Board Sponsors** (Eric Robson, Lalit Summan) | Executive oversight | Evidence that Luminate governance is enterprise-grade and defensible; path to cross-BG (Canada, SLC, MFS) adoption |

---

## Scope

### MVP (First Production Release)

**What must be true for go-live to US DCP:**

- **Compliance requirement registry** — Consolidated mapping of 40+ requirement sources to 5 core Luminate primitives (Registry, APIKey, AccessPolicy, Guardrail, AuditEvent, Deployment); CR-ID unique identifiers for every requirement
- **Risk tier enforcement** — `risk_tier` field on Agent model (AA/A/B/C/D); automatic gating of killswitch, PIA reference, validation_status, audit fidelity based on tier
- **Killswitch primitive** — Atomic multi-gateway suspension API (per-agent / per-project / per-org); immediate halt across all gateway instances; event logged to AuditEvent
- **Human-in-the-Loop (HITL) primitive** — Hold/review/decision/release workflow for agent responses; portal reviewer interface; HITL event lifecycle in AuditEvent
- **Key recertification lifecycle** — Automated reminders N days before API key expiry; recertification action in portal; auto-revoke on expiry if not certified; tier-driven rotation schedule (L1=365d, L2=180d, L3/L4=90d)
- **Non-human identity provisioning** — Integration handshake with Okta and Azure Entra ID; agent API keys registered as service accounts; NHI inventory queryable by IAM team
- **Compliance passport workflow** — T0 triage gating per GenAI Risk Governance Playbook; structured fields for ATG ticket ref, ISRA ref, MBCT inventory ref, PIA ref, TPRM ref; deployment blocked until all required tracks complete
- **Input guardrails enforcement** — Banned-words and Presidio PII detection for all agents; ENFORCE/WARN modes; attachment scoping (Org/Project/APIKey/Agent level)
- **Output guardrails (new)** — PII detection and redaction on model responses; bias/discrimination classification on decision outputs; prompt-injection pattern detection
- **Full-fidelity audit for Level A/AA agents** — AuditEvent records with `fidelity=full`, `plane=control/data`, `event_class=change/decision/access`, protocol-typed (LLM/MCP/A2A)
- **Purpose-based access control (PBAC)** — Invocation-level purpose declaration; gating data access and tool calls by declared purpose; purpose-drift detection alerts
- **Provider risk diversification** — Model Catalog lists 9+ LLM providers; provider concentration dashboard showing distribution across agents; BAA-status field on regulated Model offerings
- **Data residency enforcement** — Location constraint on AccessPolicy made non-optional for SL Restricted data agents; deployment topology validation confirming boundary compliance
- **Cost attribution for SOX ITGC** — Immutable cost record persistence (not just Langfuse); per-entity cost attribution; budget-breach alerting; CMRM export hook for monitoring evidence
- **Capture governance policy** — Policy scoping which agents may have capture enabled; capture access RBAC; retention and deletion schedule
- **Regulatory evidence dashboard** — Compliance status across OSFI E-23, NAIC, Colorado CAIA, HIPAA, PIPEDA, internal policies; exportable evidence packs; audit trail integrity verification
- **Okta / Azure Entra ID validation** — Tested SSO, MFA enforcement, group-to-role mapping, JIT provisioning; Sun Life user can authenticate with production credentials

### Backlog (Future Phases)

- **Confidential computing / TEE attestation** — AWS Nitro Enclaves attestation mode; Intel TDX support for SL Restricted workloads; cryptographic trust model preference for high-risk agents
- **Inference governance** — Distinguish inference artefacts (AI-generated assertions) from input data in audit trail; separate retention and access controls for inferences
- **Cross-jurisdiction policy enforcement** — Region-specific Delaware, Colorado, Texas, EU, Canada compliance automation; multi-region agent deployments with appropriate guardrails per jurisdiction
- **Agentic operations directive** — Contribute enterprise-wide policy consolidating agent-specific clauses scattered across LASD, MBCT, AppSec, Tech Arch into unified directive
- **Memory governance sidecar** — Governed memory layer integration; session context recording in AuditEvent; access control for conversation history across agents
- **Advanced drift detection** — Automated monitoring for model degradation, data drift, adversarial patterns; predictive detection of compliance violations
- **Automated remediation workflows** — Self-healing for degraded agents (rollback to prior LLM, suspend underperforming agents, escalate to MVU)
- **Multi-BG consolidation** — Unified governance across US BG, Canada, SLC, MFS with region-appropriate policy carve-outs; cross-BG agent collaboration support

---

## Success Criteria

**How do we measure first-deployment success?**

- **100% regulatory requirement coverage** — Every CR-ID in the compliance registry (CR-EXT, CR-MBCT, CR-ITR, CR-ARC, CR-APP, etc.) is either LIVE, PARTIAL with roadmap, or explicitly out-of-scope with documented justification
- **Zero manual compliance passport steps** — Agent activation workflow is fully automated from T0 triage to deployment; no manual email requests to ATG, ISRA, MBCT, PIA, TPRM tracks; all evidence collected via platform
- **100% of Level A/AA agents have killswitches** — Every production agent at risk tier A or above has a working killswitch; halt tested and exercised in security drill
- **95%+ first-time activation success rate** — Agents registered and activated without rejection due to missing compliance evidence; support tickets for governance-related issues < 5% of new registrations
- **Regulatory audit readiness** — Evidence packs for OSFI E-23, NAIC, Colorado CAIA, HIPAA reviews are exportable within 1 business day; no manual assembly required
- **Key recertification cadence met** — Zero API keys active past expiry date; recertification reminders trigger with 80%+ completion rate within review window
- **Zero uncontrolled agent activation** — All agents follow risk-tier-driven gates; no Level A agents deployed without PIA, validation status, full-fidelity audit
- **Sub-second compliance evaluation latency** — AuthZ evaluation (AccessPolicy + purpose + risk tier constraints) completes in <100ms per request; no measurable impact on agent latency
- **Cost attribution accuracy** — Token costs accurately attributed to agents, projects, business units; CMRM monitoring evidence export aligns with SOX ITGC audit timeline
- **Cross-region deployment** — Agents in Colorado, Texas, Canada, EU environments automatically enforce jurisdiction-specific constraints (consumer notification, discrimination prohibitions, residency, HIPAA)

---

## Dependencies

**What must be resolved before success is possible?**

1. **ATG platform approval** — Technology Architecture Office must formally approve Luminate's architecture (MCP proxy, A2A protocol, LLM routing patterns, federated deployment model) before production deployment; required by Technology Architecture Directive CR-ARC-01
2. **Legal/Procurement agreement** — Luminate repository licensing and vendor agreement must be finalized; Sun Life Legal must sign off on TELUS Digital / edaeacp project terms; agentgateway open-source compliance cleared
3. **MBCT and IT Risk Policy alignment** — MBCT track owner (Enterprise Risk) must confirm that risk_tier field and governance passport workflow correctly encode BCT EOG requirements; IT Risk Policy owner must confirm platform infrastructure audit readiness
4. **CMRM handshake design** — Information Management and Model Validation Unit must define the automated workflow triggering CMRM inventory record creation from Luminate Registry entry; avoids dual-entry maintenance burden
5. **Okta / Azure Entra ID IDP integration validation** — Identity team must test and validate SAML attribute mapping, group-to-role binding, MFA enforcement against Sun Life's production IDPs before user onboarding
6. **Data residency topology validation** — Enterprise Architecture must confirm that Luminate's LLM proxy path does not introduce unintended cross-border data flows; location constraint enforcement architecture reviewed and approved
7. **Compliance requirements finalization** — CR-ID registry (§3 Master Requirements Table) must be baselined and approved by stakeholders; any future policy changes go through consortium governance backlog process
8. **SOX ITGC audit integration** — Internal Audit and CMRM must confirm that immutable cost records and validation evidence are discoverable in the annual IT audit cycle; audit procedures documented
9. **Regulatory engagement plan** — Compliance & Regulatory Affairs must schedule pre-submission briefings with OSFI (E-23), state insurance departments (NAIC adoption), Colorado insurance commissioner (CAIA) to validate Luminate's compliance approach before first regulated agent deployment
10. **Agent runtime PBAC implementation** — Agent framework (AgentCore / JEAP / customer SDKs) must support purpose declaration and enforcement; platform provides the policy evaluation, runtime applies decisions

---

## Risks

**What could derail deployment or compliance?**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Policy churn invalidates CR-ID registry** | Medium | High | Baseline CR-ID registry by 2026-08-31; establish consortium governance process for policy amendments; any new policy creates CR-IDs via structured intake process, not ad-hoc |
| **Regulator challenge to risk tier mapping** | Medium | High | Early regulator engagement: brief OSFI (E-23), state insurance departments (NAIC), Colorado commissioner (CAIA) on L1–L4 / AA–D mapping before go-live; obtain written feedback |
| **Agentic operations directive fails to launch** | Low | Medium | US BG sponsors directive authorship by 2026-09-01; if enterprise-wide adoption stalls, Sun Life can proceed with regional carve-out for US BG pending broader consensus |
| **CMRM integration deadlock** | Medium | Medium | Define handshake spec by 2026-07-15; if CMRM unavailable, platform records all required metadata locally with export capability; IM team ingests exports via batch process |
| **Colorado CAIA federal preemption occurs** | Low | High | Executive Order 14365 sought to preempt CAIA; if preempted, HITL and consumer notification requirements drop, reducing L4 agent complexity; Legal monitors; platform remains forward-compatible |
| **Killswitch atomic consistency fails under high concurrency** | Low | High | Implement consensus-based halt (etcd or Consul backed); test under 1000+ concurrent agent load; rollback procedure documented |
| **Presidi o PII detection false-negative on member data** | Medium | High | Specialized bias testing for financial/medical/insurance entity names; output guardrail tuning per data domain; annual revalidation of guardrail performance |
| **Okta / Azure Entra ID IDP integration does not support group-to-role binding** | Low | Medium | Fallback to manual role assignment initially; work with Identity team on custom SAML mappers; migrate to automated binding post-MVP |
| **Provider concentration creates LLM vendor risk** | Medium | Medium | Model Catalog already lists 9 providers; enforce affirmative provider diversification rule for any single-provider concentration >40%; promote alternative providers in agent templates |
| **Regulatory gap discovered post-deployment** | Medium | High | Quarterly compliance review cycle; CR-ID registry published and discoverable by all stakeholders; open GitHub issues for gaps; prioritization via consortium governance |
| **Audit trail immutability compromised by PostgreSQL bug** | Low | Critical | Implement append-only validation layer (hash chain or cryptographic signing); periodic audit record integrity verification; backup to immutable external store (S3 object lock) |
| **MVU capacity insufficient for validation surge** | Medium | Medium | Define SLA for validation turnaround (10 business days for L4, 20 for L3); queue visibility in portal; escalation process for critical-path agents; backfill with external auditors if needed |
| **Purpose-based access control adds unacceptable latency** | Low | High | PBAC evaluation in AccessPolicy evaluation (existing fast path); pre-compute purpose-compatibility matrix; cache warm-up on deployment updates; target <10ms additional latency |
| **Agent memory contamination enables cross-BG data leakage** | Medium | High | Memory sidecar interface spec requires AccessPolicy enforcement; cross-agent memory access audit logging; memory isolation testing per Red Team exercise |
| **Killswitch false-positive suspension disrupts operations** | Low | High | Require escalation via Slack/PagerDuty before org-level suspension; per-agent / per-project suspensions are fast-path; post-incident automation review; audit trail of all suspension events |

---

## Next Steps

1. **Stakeholder alignment** — Present D0 to BCT track owner (Enterprise Risk), ATG, Legal, CMRM, Compliance & Regulatory Affairs for feedback and priority sequencing
2. **CR-ID registry baselineing** — Lock compliance registry (§3 Master Requirements Table) by 2026-08-31; publish as enterprise artifact; establish change control via consortium governance
3. **Compliance passport workflow design** — Technical design for T0 triage automation; handoff to ATG, ISRA, MBCT, PIA, TPRM tracks; evidence collection and gating logic
4. **Risk tier enforcement architecture** — Detailed design for risk_tier field, tier-driven gates (killswitch, PIA, validation_status, audit fidelity), and deployment activation workflow
5. **ATG submission preparation** — Platform team prepares architecture document, security design, operational runbooks for Architecture Office review
6. **D1 requirements** — Transform CR-ID registry into user stories and acceptance criteria; define API signatures for new primitives (killswitch, HITL, recertification, PBAC); rig orous acceptance criteria per primitive

---

**Document Classification:** SL Confidential — Internal  
**Version:** 1.0 — 2026-08-12  
**Author:** US BG FCP Strategy Team  
**Status:** D0 Discovery in progress — Stakeholder review phase  
**Next Review:** 2026-08-25 post-stakeholder alignment
