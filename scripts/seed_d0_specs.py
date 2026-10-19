#!/usr/bin/env python3
"""Generate D0 discovery specs for all 16 ACP components from EACPP epic data.

This script creates the initial spec directory structure with spec.yaml and
d0-discovery.md for each component, seeded from the QIP planner epic analysis data.

Usage:
    python3 scripts/seed_d0_specs.py
"""

import json
from pathlib import Path

# Component specs mapped from EACPP epics (E02-E17; E01 is meta/process)
COMPONENTS = [
    {
        "component": "acp-core",
        "title": "acp-core: Domain Contract Hardening",
        "description": "Harden the shared domain contract library that all services depend on — models, protocols, events, exceptions, adapter base.",
        "jira_epic": "EACPP-38",
        "agileplace_card": "2449525654",
        "repo": "acp-core",
        "depends_on": [],
        "problem": "acp-core is the foundation for all 14 downstream repos. At 1,205 LOC with only 16 tests, it lacks multi-tenant support, event schema versioning, and formalized adapter protocols. Changes here propagate everywhere — breakage is catastrophic.",
        "opportunity": "A hardened, well-tested domain contract library enables all downstream services to build on a stable foundation. Multi-tenant models unlock enterprise deployment. Formalized adapter protocols allow platform-agnostic integration.",
        "success_criteria": [
            ("Test coverage", "pytest --cov", ">= 90%"),
            ("Multi-tenant models", "Tenant isolation in all domain entities", "All models support tenant_id"),
            ("Event versioning", "Schema registry with version negotiation", "All events have version field"),
            ("Adapter protocol", "Platform-agnostic interface", "3+ platform adapters conforming"),
        ],
        "risks": [
            ("Breaking changes propagate to all repos", "High", "High", "Semantic versioning + coordinated release"),
            ("Event schema migration complexity", "Medium", "Medium", "Version negotiation protocol"),
        ],
        "stories_summary": "5 stories: align domain models for multi-tenant, formalize adapter protocol, define versioned event schema, add comprehensive pydantic validation, establish exception hierarchy with error codes.",
    },
    {
        "component": "management-plane",
        "title": "Management Plane Hardening",
        "description": "Harden the governance brain — policy compilation, propagation, audit, multi-tenant governance, and escalation workflows.",
        "jira_epic": "EACPP-39",
        "agileplace_card": "2449525656",
        "repo": "acp-management-plane",
        "depends_on": ["acp-core", "storage-persistence"],
        "problem": "The management plane (port 8000) has 4,959 LOC but only 14 tests. It handles ~40 endpoints for policy, audit, evaluation, and propagation. Multi-tenant isolation is missing, escalation workflows are incomplete, and policy compilation needs hardening for production load.",
        "opportunity": "A hardened management plane becomes the enterprise governance API — compiling CEL/OPA policies, propagating bundles to gateways, maintaining audit trails, and supporting multi-tenant SaaS deployment.",
        "success_criteria": [
            ("Test coverage", "pytest --cov", ">= 90%"),
            ("Multi-tenant isolation", "Policy isolation per tenant", "Zero cross-tenant leakage"),
            ("Policy compilation", "Bundle generation performance", "< 500ms for 1000 rules"),
            ("Escalation workflow", "ALLOW → ESCALATE → human review", "End-to-end flow working"),
        ],
        "risks": [
            ("Policy compilation performance under load", "Medium", "High", "Caching and profiling"),
            ("Multi-tenant isolation correctness", "Medium", "High", "Property-based testing"),
        ],
        "stories_summary": "7 stories: multi-tenant policy isolation, bundle compilation/versioning, escalation workflow, audit trail with retention, policy dry-run, ETag incremental sync, operational health endpoints.",
    },
    {
        "component": "agent-registry",
        "title": "Agent Registry Hardening",
        "description": "Build the agent registry into a governance-by-design service — registration, classification, approval, lifecycle management through enterprise governance.",
        "jira_epic": "EACPP-37",
        "agileplace_card": "2449525113",
        "repo": "acp-agent-registry",
        "depends_on": ["acp-core", "storage-persistence", "governance-integration"],
        "problem": "The agent registry (port 8001) has 1,068 LOC with only 1 test. It's not just CRUD — it's the intake point where governance processes (GenAI Risk Triage, privacy review, security assessment) feed into the ACP. Missing: test coverage, governance intake APIs, clearance model.",
        "opportunity": "A governance-by-design agent registry ensures every AI agent is registered, classified, approved, and lifecycle-managed before deployment. It becomes the single source of truth for 'what agents exist and what can they do.'",
        "success_criteria": [
            ("Test coverage", "pytest --cov", ">= 90%"),
            ("Governance intake", "Risk Triage → Agent Registry API", "End-to-end flow working"),
            ("Kill switch latency", "Time from kill command to agent stopped", "< 100ms"),
            ("Lifecycle state machine", "Valid state transitions only", "All invalid transitions rejected"),
        ],
        "risks": [
            ("Risk Triage may lack structured outputs", "Medium", "Medium", "Flexible intake API with manual override"),
            ("Kill switch must be < 100ms", "Low", "High", "Cache layer + async cascade"),
        ],
        "stories_summary": "7 stories: align data model with governance, design governance intake API, implement lifecycle state machine, build clearance-based access control, implement kill switch with cascade, add agent classification (OSFI E-23), design agent-to-tool binding governance.",
    },
    {
        "component": "model-registry",
        "title": "Model Registry Hardening",
        "description": "Build a governance-driven model registry aligned with OSFI E-23 risk tiering, Archer integration, approval workflows, and model lifecycle management.",
        "jira_epic": "EACPP-36",
        "agileplace_card": "2449525733",
        "repo": "acp-model-registry",
        "depends_on": ["acp-core", "storage-persistence", "governance-integration"],
        "problem": "The model registry (port 8003) has 1,173 LOC with only 1 test. It governs which AI models are approved for use, by which agents, under what constraints. Missing: test coverage, Archer integration, OSFI E-23 risk tiering enforcement, budget governance.",
        "opportunity": "A governance-driven model registry ensures every AI model is risk-tiered, approved, and budget-constrained before any agent can invoke it. Archer integration connects to existing risk management processes.",
        "success_criteria": [
            ("Test coverage", "pytest --cov", ">= 90%"),
            ("OSFI E-23 risk tiering", "Models classified by risk tier", "All 4 tiers enforced"),
            ("Approval workflow", "Multi-level review based on risk tier", "Correct approvers per tier"),
            ("Budget governance", "Token/cost caps per model per agent", "Hard cutoff at budget limit"),
        ],
        "risks": [
            ("Archer API access may require long lead time", "High", "Medium", "Manual intake initially"),
            ("Model deprecation from providers", "Medium", "Medium", "Automated lifecycle tracking"),
        ],
        "stories_summary": "7 stories: OSFI E-23 risk tiering, Archer integration, approval workflow, lifecycle state machine, model-to-agent binding, model card generation, budget governance.",
    },
    {
        "component": "mcp-registry",
        "title": "MCP Registry Governance",
        "description": "Evolve the MCP registry from a tool catalog into a governance-first service with approval workflows, tool hash pinning, security guardrails, and classification-based access control.",
        "jira_epic": "EACPP-30",
        "agileplace_card": "2449525480",
        "repo": "acp-mcp-registry",
        "depends_on": ["acp-core", "ai-gateway", "deployment-infrastructure"],
        "problem": "MCP tools are the hands of AI agents — ungoverned tools means ungoverned actions. The registry (port 8002, 3,723 LOC, 126 tests) needs: hash pinning for integrity, classification-based filtering, production guardrails, and security threat mitigations (tool poisoning, rug pulls, SSRF).",
        "opportunity": "A governance-first MCP registry ensures every tool is classified, approved, hash-pinned, and monitored. AI4Ops Waldo convergence brings domain MCP servers under ACP governance without changing their logic.",
        "success_criteria": [
            ("Hash pinning", "SHA-256 integrity verification", "All tools hash-pinned at approval"),
            ("Classification filtering", "Agent clearance vs tool classification", "Correct access decisions"),
            ("Security intake", "Tool description scanning for injection", "All registration passes security scan"),
            ("Waldo convergence", "AI4Ops servers registered in ACP", "Pilot with 1 domain server"),
        ],
        "risks": [
            ("Hash pinning false positives on legitimate updates", "Medium", "Medium", "Versioned pins with re-approval flow"),
            ("Tool classification requires initial manual effort", "High", "Low", "Sane defaults + bulk classification"),
        ],
        "stories_summary": "11 stories: tool approval workflow, hash pinning, classification-based access, guardrails (input/output), schema validation, discovery API, health monitoring, branch merge, AI4Ops Waldo alignment spike, Waldo onboarding pilot, MCP security threat model.",
    },
    {
        "component": "ai-gateway",
        "title": "AI Gateway & Multi-Gateway Architecture",
        "description": "Implement multi-gateway architecture — ACP pushes policy bundles to AgentGateway OSS, AWS AgentCore, and future gateways.",
        "jira_epic": "EACPP-31",
        "agileplace_card": "2449525482",
        "repo": "acp-gateway",
        "depends_on": ["management-plane", "acp-core"],
        "problem": "The ACP needs to be gateway-agnostic — pushing policy bundles to any compliant gateway. The bundle protocol is designed but not implemented. CEL engine works but isn't integrated with the gateway. ExtAuthz fallback isn't built.",
        "opportunity": "A gateway-agnostic governance layer means the ACP can govern AI workloads regardless of where they run — AgentGateway OSS on K8s, AWS Bedrock via AgentCore, Snowflake via Cortex. One set of rules, multiple enforcement points.",
        "success_criteria": [
            ("Bundle protocol", "Gateway consumes policy bundles", "AgentGateway polls and applies bundles"),
            ("CEL delegation", "CEL policies evaluated at gateway", "< 5ms policy evaluation"),
            ("ExtAuthz fallback", "Complex auth delegated to ACP", "< 50ms round-trip"),
            ("Multi-gateway", "2+ gateway types consuming bundles", "AgentGateway + 1 adapter"),
        ],
        "risks": [
            ("AgentGateway OSS is early-stage (v1.1.0)", "Medium", "Medium", "Pin version, contribute upstream"),
            ("ExtAuthz latency under load", "Medium", "High", "CEL-first, extAuthz-fallback pattern"),
        ],
        "stories_summary": "8 stories: AgentGateway integration spike, bundle compilation, bundle distribution with ETag, CEL policy delegation, extAuthz fallback, gateway adapter protocol, audit event ingestion, load testing.",
    },
    {
        "component": "aws-adapter",
        "title": "AWS Platform Adapter — AgentCore, Bedrock, Cedar",
        "description": "Deep integration with AWS Bedrock AgentCore — sync governance decisions to Gateway, Policy (Cedar), Identity, Runtime, Memory, Evaluations, and Observability.",
        "jira_epic": "EACPP-29",
        "agileplace_card": "2449525308",
        "repo": "acp-adapter-aws",
        "depends_on": ["ai-gateway", "agent-registry", "mcp-registry"],
        "problem": "AWS AgentCore provides a comprehensive suite that overlaps with ACP responsibilities. Without integration, teams bypass ACP governance by registering directly in AgentCore. The adapter (865 LOC, 12 tests) is scaffolded but not functional — no live AgentCore access.",
        "opportunity": "ACP becomes the approval authority while AgentCore handles execution. Kill switch cascades through IAM, Cedar, and Runtime. Drift detection catches ungoverned resources.",
        "success_criteria": [
            ("Cedar compilation", "ACP rules → Cedar permits/forbids", "Deterministic, tested compilation"),
            ("Kill switch cascade", "Agent killed in ACP → stopped in AWS", "< 30s end-to-end"),
            ("Drift detection", "Find unregistered tools/policies in AgentCore", "Scheduled scan, alerts on drift"),
            ("Tool sync", "ACP tools → AgentCore Gateway", "Bidirectional sync working"),
        ],
        "risks": [
            ("AgentCore API access requires AWS SA engagement", "High", "High", "Start engagement early"),
            ("Cedar policy complexity", "Medium", "Medium", "Deterministic compilation + Cedar Playground testing"),
            ("IAM role proliferation", "Medium", "Low", "Role-per-agent-type, not role-per-agent"),
        ],
        "stories_summary": "9 stories: AgentCore sandbox spike, Gateway adapter, Cedar compiler, Identity adapter, Bedrock model access, CloudWatch audit ingestion, Runtime deployment gating, drift detection, evaluation score ingestion.",
    },
    {
        "component": "snowflake-adapter",
        "title": "Snowflake Platform Adapter — Cortex, RBAC, Sirius Snowfort",
        "description": "Sync ACP governance to Snowflake RBAC, manage Cortex Agent lifecycles, register Cortex Search/Analyst as governed tools, ingest AI Observability events.",
        "jira_epic": "EACPP-28",
        "agileplace_card": "2449525560",
        "repo": "acp-adapter-snowflake",
        "depends_on": ["acp-core", "mcp-registry"],
        "problem": "Snowflake Cortex agents, Search services, and Analyst semantic views are ungoverned. The adapter (1,169 LOC, 22 tests) is scaffolded but needs Cortex REST API integration, RBAC sync via Sirius Snowfort, and classification tag mapping.",
        "opportunity": "ACP governance extends into Snowflake — clearance-based RBAC, tool classification, audit integration. Sirius Snowfort IaC provides the enforcement mechanism. Cortex AI Observability provides the telemetry.",
        "success_criteria": [
            ("RBAC sync", "ACP clearances → Snowflake roles", "All clearance levels mapped"),
            ("Cortex Agent governance", "CRUD sync via REST API", "Create/update/delete/kill working"),
            ("Tool registration", "Cortex Search/Analyst → ACP tools", "Auto-discovery and registration"),
            ("Audit ingestion", "AI Observability events → ACP", "Real-time event forwarding"),
        ],
        "risks": [
            ("Cortex Agents REST API is relatively new", "Medium", "Medium", "Early validation spike"),
            ("Sirius Snowfort changes need platform team coordination", "High", "Medium", "Engage platform team early"),
            ("Snowflake model deprecation cycle", "Medium", "Low", "Automated tracking"),
        ],
        "stories_summary": "8 stories: Cortex API validation spike, agent governance CRUD, RBAC adapter, Cortex Search registration, Cortex Analyst registration, AI Observability ingestion, Snowfort integration, drift detection.",
    },
    {
        "component": "kubernetes-adapter",
        "title": "Kubernetes & API Platform Adapter",
        "description": "AgentGateway CRD sync, KServe model serving, OPA/Gatekeeper admission control, network enforcement, and Enterprise API Platform alignment.",
        "jira_epic": "EACPP-26",
        "agileplace_card": "2449525491",
        "repo": "acp-adapter-k8s",
        "depends_on": ["acp-core", "ai-gateway"],
        "problem": "The K8s adapter (838 LOC, 12 tests) is scaffolded but non-functional. AgentGateway CRD sync, KServe integration, and OPA admission control are designed but not implemented. API Platform integration patterns (LNL Lambda) need analysis.",
        "opportunity": "ACP governs AI workloads on Kubernetes — pushing MCPServerRoute CRDs to AgentGateway, deploying models via KServe, enforcing governance labels via OPA Gatekeeper. API Platform alignment enables production-grade API exposure.",
        "success_criteria": [
            ("CRD sync", "ACP tools → MCPServerRoute CRDs", "Automatic sync on tool approval"),
            ("Model serving", "ACP models → KServe InferenceService", "Model deployment from registry"),
            ("Admission control", "Ungoverned workloads rejected", "OPA Gatekeeper constraints active"),
            ("API Platform", "ACP APIs exposed via LNL pattern", "Production ingress configured"),
        ],
        "risks": [
            ("AgentGateway CRD schema may change", "Medium", "Medium", "Pin version, contribute upstream"),
            ("KServe cluster access requirements", "Medium", "Low", "Coordinate with platform team"),
        ],
        "stories_summary": "9 stories: AgentGateway K8s deployment spike, API Platform analysis spike, MCPServerRoute CRD sync, extAuthz endpoint, KServe adapter, OPA Gatekeeper constraints, OPA bundle generation, network enforcement, LNL API exposure.",
    },
    {
        "component": "storage-persistence",
        "title": "Storage & Persistence Layer",
        "description": "Production-grade PostgreSQL stores for agents, models, audit, evaluations, tool bindings. Alembic migrations, connection pooling, multi-tenant isolation.",
        "jira_epic": "EACPP-27",
        "agileplace_card": "2449525749",
        "repo": "acp-store-postgres",
        "depends_on": ["acp-core"],
        "problem": "acp-store-postgres provides SQLAlchemy stores for all services but needs: production-grade connection pooling, Alembic migration workflow, multi-tenant data isolation, query optimization, and comprehensive testing with testcontainers.",
        "opportunity": "A robust persistence layer enables all services to scale independently while sharing a proven storage pattern. Multi-tenant isolation supports SaaS deployment.",
        "success_criteria": [
            ("Connection pooling", "PgBouncer or SQLAlchemy pool", "Handles 100 concurrent connections"),
            ("Alembic migrations", "Schema versioning", "Automated migration on deploy"),
            ("Multi-tenant isolation", "Row-level security or schema-per-tenant", "Zero cross-tenant leakage"),
            ("Test coverage", "testcontainers + real PostgreSQL", ">= 90%"),
        ],
        "risks": [
            ("Migration ordering across services", "Medium", "Medium", "Centralized migration registry"),
            ("Performance under concurrent writes", "Medium", "Medium", "Connection pooling + query optimization"),
        ],
        "stories_summary": "5 stories: connection pooling and health checks, Alembic migration workflow, multi-tenant data isolation, query optimization and indexing, comprehensive integration testing.",
    },
    {
        "component": "deployment-infrastructure",
        "title": "Deployment & Infrastructure",
        "description": "Production deployment on OpenShift/EKS — Kustomize manifests, CI/CD pipelines, observability stack, demo environment hardening.",
        "jira_epic": "EACPP-25",
        "agileplace_card": "2449525676",
        "repo": "agent-control-plane-demo",
        "depends_on": [],
        "problem": "The demo stack (21 containers) works locally but needs: production Kustomize overlays, Jenkins CI/CD pipelines for each microservice, Prometheus/Grafana dashboards hardening, container security (non-root, read-only FS), and image scanning.",
        "opportunity": "Production-grade deployment enables the ACP to run on enterprise OpenShift/EKS clusters with proper observability, security, and CI/CD automation.",
        "success_criteria": [
            ("Production manifests", "Kustomize overlays for dev/staging/prod", "All services deployable"),
            ("CI/CD pipelines", "Jenkins pipelines per microservice", "Build + test + scan + deploy"),
            ("Observability", "Grafana dashboards with real metrics", "All services instrumented"),
            ("Container security", "Non-root, read-only FS, Snyk clean", "All images pass security scan"),
        ],
        "risks": [
            ("OpenShift cluster access", "Medium", "High", "Coordinate with platform team"),
            ("Jenkins pipeline complexity", "Medium", "Medium", "Template reuse across services"),
        ],
        "stories_summary": "12 stories: Kustomize production overlays, Jenkins build/deploy pipelines, Quay image registry, Prometheus scrape configs, Grafana dashboards, container security hardening, resource limits/HPA, secrets management, ConfigMap externalization, health probes, namespace isolation, image scanning.",
    },
    {
        "component": "ui-management-console",
        "title": "UI Management Console",
        "description": "Harden the React 18 / MUI v7 management UI — single pane of glass for agents, models, tools, policies, audit.",
        "jira_epic": "EACPP-24",
        "agileplace_card": "2449525311",
        "repo": "agent-control-plane-ui",
        "depends_on": [],
        "problem": "The UI (port 3002/3005) is functional but needs: test coverage (199 Playwright tests, but limited Jest unit tests), accessibility compliance, CSP headers, performance optimization, and production security hardening.",
        "opportunity": "A production-grade management console provides the single pane of glass for ACP operations — managing agents, models, tools, policies, and viewing audit trails.",
        "success_criteria": [
            ("Test coverage", "Jest unit + Playwright e2e", ">= 80% unit, 200+ e2e"),
            ("Accessibility", "WCAG 2.1 AA compliance", "axe audit clean"),
            ("CSP headers", "Content Security Policy", "No unsafe-inline/unsafe-eval"),
            ("Performance", "Lighthouse score", ">= 90"),
        ],
        "risks": [
            ("Helios design system version conflicts with MUI", "Medium", "Low", "Theme layer abstraction"),
            ("CSP may break inline styles from MUI", "Medium", "Medium", "Nonce-based CSP"),
        ],
        "stories_summary": "6 stories: Jest unit test coverage, Playwright test expansion, accessibility audit and remediation, CSP header implementation, performance optimization, production nginx hardening.",
    },
    {
        "component": "governance-integration",
        "title": "Governance Process Integration",
        "description": "Connect ACP to enterprise governance — GenAI Risk Triage, Archer, privacy review, security assessment, ITRM/ServiceNow, Collibra.",
        "jira_epic": "EACPP-21",
        "agileplace_card": "2449525494",
        "repo": "acp-management-plane",
        "depends_on": ["agent-registry", "model-registry"],
        "problem": "ACP governance is self-contained but needs to connect to Sun Life's existing governance processes: GenAI Risk Triage for agent approval, Archer for model risk assessment, ITRM/ServiceNow for operational tracking, Collibra for data contract lineage.",
        "opportunity": "Enterprise governance integration means the ACP is not a silo — it feeds from and reports to existing risk management, compliance, and operational systems. Governance decisions are auditable end-to-end.",
        "success_criteria": [
            ("Risk Triage integration", "Triage output → Agent Registry", "Structured intake API"),
            ("Archer integration", "Risk assessment → Model Registry", "Automated risk tier mapping"),
            ("Audit export", "ACP audit → ITRM/ServiceNow", "Scheduled export or webhook"),
            ("Collibra lineage", "Data product → agent → model → tool chain", "Lineage visible in Collibra"),
        ],
        "risks": [
            ("External system APIs may be poorly documented", "High", "Medium", "Early API exploration spikes"),
            ("Governance process changes outside ACP control", "Medium", "Medium", "Flexible adapter pattern"),
        ],
        "stories_summary": "10 stories: GenAI Risk Triage intake API, Archer risk assessment adapter, privacy review workflow, security assessment intake, ITRM/ServiceNow export, Collibra lineage publishing, governance dashboard, compliance reporting, audit trail federation, exception handling workflow.",
    },
    {
        "component": "evaluation-strategy",
        "title": "Model & Agent Evaluation Strategy",
        "description": "Systematic evaluation framework for AI model quality, agent behavior, and governance compliance — LLM-as-judge, benchmark suites, regression detection.",
        "jira_epic": "EACPP-22",
        "agileplace_card": "2449525395",
        "repo": "acp-management-plane",
        "depends_on": ["model-registry", "agent-registry"],
        "problem": "No systematic evaluation of model quality or agent behavior exists. Models are approved based on manual assessment. Agent behavior is monitored reactively. No benchmark suites, no regression detection, no quality gates tied to deployment.",
        "opportunity": "A comprehensive evaluation framework enables data-driven model selection, agent quality gates, automated regression detection, and continuous improvement. LLM-as-judge patterns scale quality assessment.",
        "success_criteria": [
            ("Benchmark suite", "Standard evaluations for models", "Coverage of key capabilities"),
            ("Quality gates", "Minimum scores for deployment approval", "Automated gate in CI/CD"),
            ("Regression detection", "Score comparison across model versions", "Automated alerting"),
            ("Agent behavior eval", "Task completion, safety, cost metrics", "Per-agent scorecards"),
        ],
        "risks": [
            ("LLM-as-judge reliability varies by task", "Medium", "Medium", "Multi-judge consensus"),
            ("Evaluation cost for large model catalogs", "Medium", "Low", "Sampling + tiered evaluation"),
        ],
        "stories_summary": "10 stories: evaluation framework architecture, LLM-as-judge implementation, benchmark suite design, model quality scorecard, agent behavior evaluation, quality gate integration, regression detection, A/B test evaluation, cost-quality tradeoff analysis, evaluation dashboard.",
    },
    {
        "component": "inference-economics",
        "title": "Inference Economics & Intelligent Routing",
        "description": "Cost-aware model routing, budget enforcement, token tracking, and cost optimization across providers and deployment tiers.",
        "jira_epic": "EACPP-20",
        "agileplace_card": "2449525832",
        "repo": "acp-gateway",
        "depends_on": ["model-registry", "ai-gateway"],
        "problem": "No cost tracking or budget enforcement for AI model usage. Agents can consume unlimited tokens. No intelligent routing based on cost-quality tradeoffs. No visibility into inference economics across providers.",
        "opportunity": "Inference economics enables cost governance at scale — budget caps per agent, intelligent routing to cheaper models for low-risk tasks, provider cost comparison, and FinOps dashboards.",
        "success_criteria": [
            ("Token tracking", "Per-agent, per-model usage tracking", "Real-time metrics"),
            ("Budget enforcement", "Hard caps on monthly spend", "Automatic cutoff at limit"),
            ("Intelligent routing", "Route to cheaper model when quality allows", "Configurable routing rules"),
            ("FinOps dashboard", "Cost visibility across providers", "Drill-down by agent, model, team"),
        ],
        "risks": [
            ("Provider pricing models change frequently", "Medium", "Low", "External pricing table, manual updates"),
            ("Routing latency overhead", "Medium", "Medium", "Sub-millisecond routing decisions"),
        ],
        "stories_summary": "10 stories: token usage tracking, budget enforcement engine, cost allocation model, intelligent routing engine, provider cost comparison, usage anomaly detection, FinOps dashboard, chargeback reporting, cost optimization recommendations, budget alerting.",
    },
    {
        "component": "ui-advanced-features",
        "title": "UI Advanced Features",
        "description": "Advanced UI capabilities — real-time dashboards, policy simulation, agent topology visualization, audit search, and role-based access.",
        "jira_epic": "EACPP-19",
        "agileplace_card": "2449525947",
        "repo": "agent-control-plane-ui",
        "depends_on": ["ui-management-console", "management-plane"],
        "problem": "The current UI handles basic CRUD but lacks: real-time operational dashboards, policy simulation (what-if), agent/tool topology visualization, advanced audit search, and role-based view restrictions.",
        "opportunity": "Advanced UI features transform the management console from a CRUD interface to an operational command center — real-time visibility, policy experimentation, and visual topology mapping.",
        "success_criteria": [
            ("Real-time dashboards", "Live metrics and status updates", "WebSocket or SSE refresh"),
            ("Policy simulation", "What-if analysis without enforcement", "Dry-run mode in UI"),
            ("Topology visualization", "Agent → model → tool dependency graph", "Interactive graph view"),
            ("Audit search", "Full-text search with filters", "Sub-second query response"),
        ],
        "risks": [
            ("WebSocket infrastructure on OpenShift", "Medium", "Medium", "SSE fallback"),
            ("Graph visualization performance with large datasets", "Medium", "Low", "Virtualization + pagination"),
        ],
        "stories_summary": "10 stories: real-time dashboard framework, agent status dashboard, policy simulation UI, topology visualization, audit log search and filtering, role-based view restrictions, notification system, export/reporting, keyboard shortcuts, dark mode.",
    },
]


def generate_spec_yaml(c: dict) -> str:
    depends = "\n".join(f'  - "{d}"' for d in c["depends_on"]) if c["depends_on"] else '  []'
    if c["depends_on"]:
        depends_block = f"depends_on:\n{depends}"
    else:
        depends_block = "depends_on: []"

    return f"""component: "{c['component']}"
title: "{c['title']}"
description: "{c['description']}"

current_gate: D0
status: draft
spec_type: platform

owner: "Seth Chalmers"
team: "EDAE ACP"

jira_epic: "{c['jira_epic']}"
agileplace_card: "{c['agileplace_card']}"
confluence_page: ""
repo: "{c['repo']}"

{depends_block}

gates:
  d0:
    status: draft
    pr: ""
    approved_date: ""
    reviewers: []
  d1:
    status: not-started
    pr: ""
    approved_date: ""
    reviewers: []
  d2:
    status: not-started
    pr: ""
    approved_date: ""
    reviewers: []
  d3:
    status: not-started
    pr: ""
    approved_date: ""
    reviewers: []
  d4:
    status: not-started
    pr: ""
    approved_date: ""
    reviewers: []
"""


def generate_d0(c: dict) -> str:
    success_rows = "\n".join(
        f"| {s[0]} | {s[1]} | {s[2]} |" for s in c["success_criteria"]
    )
    risk_rows = "\n".join(
        f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |" for r in c["risks"]
    )
    depends_rows = "\n".join(
        f"| {d} spec at D1+ | {d} | Hard | Blocks detailed design |"
        for d in c["depends_on"]
    ) if c["depends_on"] else "| None | — | — | — |"

    return f"""# {c['title']} — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: {c['jira_epic']}

## Problem Statement

{c['problem']}

## Opportunity

{c['opportunity']}

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| ACP Engineering Team | Implementers | Technical feasibility, test coverage, maintainability |
| Platform Architecture | Reviewers | Architectural consistency, integration patterns |
| Product Owner | Approver | Business value, priority, timeline |
| Enterprise Governance | Consumer | Compliance, audit, risk management |
| AI4Ops / Consumer Teams | Consumers | API stability, onboarding experience |

## Scope

### In Scope

{c['stories_summary']}

### Out of Scope

- Performance optimization beyond stated NFRs (future epic)
- UI changes (handled in UI-specific epics)
- Cross-platform federation (future roadmap)

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
{success_rows}

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
{depends_rows}

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
{risk_rows}

## Open Questions

- [ ] Are the acceptance criteria sufficiently detailed for AI-agent-assisted implementation?
- [ ] Are there additional regulatory requirements beyond those identified?
- [ ] What is the target sprint for D1 requirements completion?

## References

- Jira Epic: [{c['jira_epic']}](https://sunlife.atlassian.net/browse/{c['jira_epic']})
- Source Repo: `{c['repo']}`
- AgilePlace Card: {c['agileplace_card']}
"""


def main():
    specs_dir = Path("specs") / "platform"
    created = 0

    for c in COMPONENTS:
        component_dir = specs_dir / c["component"]
        component_dir.mkdir(parents=True, exist_ok=True)

        # Write spec.yaml
        spec_yaml = component_dir / "spec.yaml"
        spec_yaml.write_text(generate_spec_yaml(c))

        # Write d0-discovery.md
        d0_file = component_dir / "d0-discovery.md"
        d0_file.write_text(generate_d0(c))

        created += 1
        print(f"  Created: specs/platform/{c['component']}/  (epic: {c['jira_epic']})")

    print(f"\n✅ Created {created} component specs with D0 discovery documents")


if __name__ == "__main__":
    main()
