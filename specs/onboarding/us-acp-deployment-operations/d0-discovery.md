# Onboard US team members to test ACP — D0 Discovery

## Problem Statement

**What pain exists today?**

The U.S. business is experiencing rapid demand for AI agents across multiple divisions, but lacks the infrastructure and operational capability to scale agent deployments with appropriate governance and compliance controls:

- **No centralized agent governance in US region** — Multiple US divisions developing agents independently without a unified registry, risk classification, or policy enforcement mechanism
- **Manual compliance processes cannot scale** — Current manual governance approaches work for a handful of agents but will not sustain deployment across multiple divisions and business units
- **Fragmented agent implementations** — Agent development is occurring across divisions without standardized oversight, audit trails, or compliance evidence collection, creating regulatory risk
- **No operational ownership model for ACP in US** — The ACP control plane exists as a consortium product, but no dedicated US operations team has been staffed or trained to run/manage an ACP instance serving US divisions
- **Lack of agent registry and risk-ranking** — No unified inventory of which agents exist, what data they access, or how they are risk-classified, preventing regulators from validating governance
- **Regulatory readiness gap** — OSFI, NAIC, and state insurance regulators expect evidence of agent governance, risk classification, audit trails, and compliance evidence; Sun Life US cannot demonstrate these today
- **Training and enablement gap** — US DCP infrastructure team and business unit stakeholders have not been trained on ACP platform capabilities, agent registration workflow, or governance responsibilities

---

## Opportunity

**What does US ACP deployment enable?**

Deploying a dedicated ACP instance into the US DCP environment and onboarding the US operations team creates a foundation for scaled, governed agent deployment across US divisions:

- **Unified agent registry for US divisions** — All agents developed across US divisions are registered in a single ACP instance, providing federated visibility and risk-based governance per division
- **Scalable governance framework** — Agent inventory, risk classification, policy enforcement, and audit trails scale seamlessly as more divisions adopt agents without manual governance overhead
- **Compliance evidence ready** — OSFI, NAIC, state insurance regulators, and internal auditors can access ACP's governance registry, audit ledger, and compliance evidence without manual assembly
- **Regulatory confidence** — ACP demonstrates that Sun Life US has implemented consistent agent governance, risk ranking, and due diligence controls across all divisions
- **Operational handoff to DCP infrastructure team** — US DCP team becomes the operational owner of ACP, decoupling day-to-day platform support from the consortium engineering teams
- **Live pilot and validation environment** — Connect existing US agent implementations to the ACP instance to validate agent routing, governance policies, and compliance evidence collection in production-like conditions
- **Competitive advantage through faster deployment** — Risk-based governance allows lower-risk agents to be deployed quickly while maintaining rigorous controls on high-risk agents, enabling US divisions to outpace competitors
- **Federated multi-region foundation** — Design US deployment for future federation across Canada, SLC, and other regions, avoiding rework when cross-BG governance scales

---

## Stakeholders

**Who is invested in success?**

| Stakeholder | Role | Need |
|---|---|---|
| **US Business Unit Heads** (Insurance, Health, Investment Management, etc.) | Agent sponsors, use case owners | Fast onboarding to ACP; clear governance requirements per division; ability to deploy agents quickly without compliance friction |
| **US DCP Infrastructure Team** | Operational owner of ACP instance | Training on ACP architecture and operational procedures; runbooks for agent deployment, policy management, incident response; escalation paths for compliance issues |
| **Enterprise Risk / MBCT Track** | Governance owner | Assurance that US ACP instance enforces risk tier classification, killswitch capability, audit fidelity, and validation workflows from Luminate platform |
| **Regulatory Affairs & Compliance** | Regulator liaison | Evidence package for OSFI, NAIC, state insurance departments demonstrating US agent governance; quarterly compliance reporting capability |
| **Data Privacy & Security** | Security ownership | HIPAA compliance validation for US ACP instance; data residency enforcement; access control policies per data sensitivity; audit trail integrity |
| **ACP Engineering Team** (consortium) | Platform steward | Feedback from US pilot on agent integration patterns; requirements for multi-region federation; feature prioritization for US-specific use cases |
| **Internal Audit & CMRM** (Model Validation Unit) | Audit and validation owner | Access to ACP governance registry for SOX ITGC compliance; validation evidence collected and tracked per risk tier |
| **IT / DCP Operations** | Infrastructure management | US ACP deployment architecture; network/security requirements; disaster recovery and failover procedures; change management integration |
| **Agent Developer Teams** (per division) | End users | Clear agent registration workflow; governance gate clarity; feedback on policy enforcement; access to compliance evidence for their agents |

---

## Scope

### MVP (First Production Deployment to US DCP)

**What must be true for US operations team to be ready:**

- **Dedicated ACP instance deployed in US DCP** — ACP platform running in AWS/Azure US region(s), accessible to US divisions; network/security configuration validated; disaster recovery and failover tested
- **US DCP infrastructure team trained** — Platform operations team trained on ACP architecture, agent deployment workflow, policy engine, audit ledger, and operational runbooks; on-call procedures defined
- **Agent registry connected to active US implementations** — One or more existing US agent implementations connected to ACP instance; agent registration and governance policies tested end-to-end
- **Risk tier classification framework in place** — Risk tier (AA/A/B/C/D) classification criteria defined for US divisions; training materials for business units on how to classify agents
- **Compliance evidence collection live** — Audit trail, governance decisions, and validation evidence automatically collected and queryable; reports generated for OSFI, NAIC, internal audit
- **Killswitch and HITL gates operational** — Atomic suspension capability tested; human-in-the-loop review workflow functional for high-risk agents; incident response procedures defined
- **HIPAA compliance validated** — Data residency constraints enforced; HIPAA-regulated data routing policies tested; access controls per sensitivity tier validated
- **Multi-division policy model defined** — Governance policies scoped per division; access controls prevent cross-division policy conflicts; audit trail distinguishes actions by division
- **Team escalation and support model** — Escalation paths defined for governance issues, agent approvals, compliance questions; support handoff from consortium engineers to US DCP team documented
- **Regulatory evidence package generated** — Sample compliance reports generated for OSFI E-23, NAIC Model Bulletin, Colorado CAIA, HIPAA requirements; export capability tested
- **Go-live checklist completed** — ATG approval of US ACP deployment; security assessment passed; operational readiness validation complete; change management ticket approved

### Backlog (Post-MVP Enhancements)

- **Cross-division policy federation** — Support for agents spanning multiple divisions with inherited parent policies and conflict resolution
- **Advanced compliance reporting** — Automated quarterly regulatory reporting; regulator-facing dashboard for audit evidence
- **Cost attribution and chargeback** — Cost tracking per division/business unit; chargeback models for shared ACP infrastructure
- **Multi-region federation** — Extend US deployment pattern to Canada, SLC, MFS; cross-region agent policies and handoffs
- **Advanced threat detection** — Anomaly detection on agent behavior; automated alerting on unusual access patterns or policy violations
- **Inference governance** — Separate governance for AI-generated inferences vs. input data; retention policies per inference type
- **Self-healing governance** — Automated rollback of degraded agents; automated recertification of overdue agent keys
- **CLI-based agent governance** — CLI tool for agent developers to test governance policies before deployment

---

## Success Criteria

**How do we measure US ACP deployment success?**

- **100% of active US agents registered in ACP** — Every agent developed across US divisions has an entry in the ACP registry with risk tier, owner, and governance policies applied
- **Zero governance exceptions** — No agents deployed to production bypassing ACP governance gates; all agents follow risk-tier-driven controls for killswitch, HITL, audit fidelity
- **US DCP team operational independence** — DCP infrastructure team can manage agent deployments, policy updates, incident response, and compliance reporting without escalation to consortium engineers within defined SLAs
- **Regulatory audit ready** — Full compliance evidence package (agent registry, audit trail, validation records, risk classifications) exportable within 1 business day for OSFI/NAIC/state regulator review
- **First-time agent deployment success rate >95%** — New agents from US divisions can be registered and activated without rejection due to governance or compliance issues; support tickets <5% of new registrations
- **Multi-division governance isolation** — Access controls prevent Division A agents from invoking Division B tools/data; audit trail clearly distinguishes actions by division; no cross-division policy conflicts
- **HIPAA compliance validation** — Third-party audit confirms ACP US deployment meets HIPAA Security Rule requirements; data residency constraints verified in deployment topology
- **Killswitch exercised and tested** — Atomic suspension tested in security drill; halt time <5 seconds globally; post-exercise report filed with IT Risk
- **Team adoption and satisfaction** — Agent developers and business unit stakeholders report clear governance requirements and fast approval workflows; NPS >4.0 on onboarding experience
- **Cost transparency** — ACP cost per division/business unit calculated and verified against budget; chargeback model tested with finance team

---

## Dependencies

**What must be resolved before success is possible?**

1. **ATG platform approval for US ACP deployment** — Technology Architecture Office must formally approve US ACP deployment architecture (network topology, security controls, failover design, federated model)
2. **AWS/Azure US region capacity and configuration** — Cloud infrastructure team must provision US ACP instance with multi-AZ/region failover; network security group rules and encryption configured
3. **Luminate Control Plane governance primitives operational** — Killswitch, HITL, risk_tier field, key recertification, and output guardrails must be live in Luminate platform before US instance can enforce these controls
4. **US DCP infrastructure team assigned and trained** — Named platform operations team (3-5 FTE) assigned to own US ACP; training schedule completed; on-call rotation established
5. **Agent registry connected to active implementations** — At least one existing US agent implementation identified and network connectivity to ACP established; agent registration workflow tested end-to-end
6. **Compliance requirements framework locked** — Risk tier classification criteria, governance policies per tier, and compliance evidence requirements must be baselined and approved by Enterprise Risk + Legal
7. **HIPAA Business Associate Agreement** — If ACP uses third-party LLM providers with HIPAA-regulated data, BAA must be in place with provider before any ePHI routing
8. **Disaster recovery and failover tested** — DR plan documented; failover from primary US region to backup tested; RTO/RPO confirmed; runbook validated
9. **Regulatory engagement** — Early briefing with OSFI, NAIC, state insurance departments on US ACP governance approach; obtain feedback on compliance evidence requirements
10. **Internal audit pre-assessment** — Internal Audit team reviews US ACP deployment; confirms compliance evidence collection matches audit expectations; audit procedures documented

---

## Risks

**What could derail US deployment or team onboarding?**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Luminate platform governance primitives slip** | Medium | High | Killswitch, HITL, risk_tier must be LIVE before US go-live; identify hard dependency on Luminate roadmap; escalate if delays |
| **US DCP infrastructure team capacity unavailable** | Medium | High | Identify and commit platform operations team by 2026-08-31; if capacity unavailable, defer US deployment or backfill with contractors |
| **Agent implementations not ready to onboard** | Low | Medium | Identify pilot agents early; confirm development teams can support ACP integration; allow 4-week lead time for agent routing setup |
| **HIPAA compliance validation fails** | Low | High | Engage third-party HIPAA compliance auditor early; conduct pre-deployment assessment; address gaps before go-live |
| **Network latency unacceptable** | Low | Medium | Baseline latency of agent routing through ACP; if degradation >100ms, optimize network path or deploy ACP sidecar in agent VPC |
| **Regulatory misalignment on governance requirements** | Medium | High | Conduct early regulator engagement (OSFI, NAIC) on US ACP governance approach; obtain written feedback before go-live |
| **Cross-division policy conflicts** | Medium | Medium | Define clear policy scoping rules per division; test conflict resolution in staging; document escalation path for policy disputes |
| **US DCP team overwhelmed by support load** | Medium | Medium | Implement tiered support model; consortium engineers support L2/L3 issues; establish SLA for escalation response |
| **ATG approval delayed** | Low | Medium | Submit ATG package by 2026-08-15; identify approver early; escalate if blockers arise |
| **Operational handoff incomplete** | Medium | High | Create detailed runbooks; pair consortium engineers with DCP team for first 30 days post-go-live; establish weekly sync during transition period |
| **Agent developer adoption slow** | Medium | Medium | Market ACP benefits clearly; provide self-service onboarding docs; offer live training sessions per division; measure adoption metrics |

---

## Next Steps

1. **Team assignment** — Identify and commit US DCP infrastructure team (3-5 FTE) to own ACP operations by 2026-08-22
2. **Requirements finalization** — Lock compliance requirements framework and risk tier classification criteria with Enterprise Risk + Legal by 2026-08-31
3. **ATG submission** — Submit US ACP deployment architecture to Technology Architecture Office by 2026-08-15; target approval by 2026-09-15
4. **Pilot agent identification** — Confirm 1-2 existing US agent implementations ready for ACP onboarding; begin network/integration planning by 2026-08-25
5. **Training plan** — Develop platform operations training curriculum (2-week program); schedule cohort 1 for 2026-09-15
6. **Regulatory pre-engagement** — Schedule briefing with OSFI + NAIC on US ACP governance approach by 2026-09-01
7. **Infrastructure procurement** — Provision AWS/Azure US region resources; network/security validation by 2026-09-30
8. **D1 requirements** — Transform governance framework into detailed platform requirements; define risk tier policies, audit evidence schema, compliance reporting formats
9. **Go-live planning** — Establish target go-live date (recommend 2026-11-15); create detailed go-live checklist and readiness criteria
10. **Post-go-live support** — Plan 30-day paired operations period with consortium engineers; establish weekly sync for DCP team ramp-up

---

**Document Classification:** SL Confidential — Internal  
**Version:** 1.0 — 2026-08-12  
**Author:** US BG ACP Strategy Team  
**Status:** D0 Discovery — Team onboarding and US deployment scope definition  
**Next Review:** 2026-08-25 post-team assignment
