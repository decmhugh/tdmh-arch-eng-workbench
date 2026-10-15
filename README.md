# tdmh-arch-eng-workbench
VS Code-centred multi-agent system that converts business requirements into BTABoK- aligned architecture viewpoints, architectural decisions, JIRA work items, Python application code, AWS infrastructure and tests—with human governance and end-to-end traceability.

> **Architecture & Engineering Agent Workbench** — Project Initiation & Delivery Blueprint
> Version 0.1 · 14 October 2026 · Status: working draft

## 1. Executive summary

The workbench is an architecture-led, specification-driven delivery environment. A lead agent orchestrates specialist agents and shared context, but cannot bypass explicit approval gates. The initial product is a repository-based VS Code workflow; a durable LangGraph/Bedrock runtime is an optional later stage.

### Target outcomes

- Reduce effort to create consistent architecture and delivery artefacts from an approved requirement.
- Maintain bidirectional links from business objective through requirement, viewpoint, ADR, JIRA story, code and test.
- Make design rationale and trade-offs explicit, including alternatives, risks and non-functional requirements.
- Keep generated code, Terraform and documentation version-controlled, reviewable and testable.

## 2. Scope and boundaries

| In scope (MVP) | Deferred / out of scope |
| -------------- | ----------------------- |
| VS Code custom agents, project instructions, shared templates | Autonomous production deployment |
| Business-context capture and viewpoint generation | Automatic approval of architecture decisions |
| ADRs, traceability manifest, diagrams | Full BTABoK knowledge corpus reproduction |
| Python service + Terraform generation and tests | General-purpose IDE extension |
| JIRA draft work items with approval before creation | Enterprise-wide agent platform from day one |

## 3. Users, use cases and success criteria

| Persona | Primary job |
| ------- | ----------- |
| Solution/enterprise architect | Capture context; select viewpoints; review decisions and trade-offs |
| Engineer | Generate and refine code, infrastructure and tests |
| Product owner | Review outcomes, scope and delivery backlog |
| Security/platform reviewer | Review permissions, NFRs, controls and deployability |

### MVP demonstration scenario

Input: design a serverless PDF ingestion service in eu-west-1. Upload to S3, process asynchronously using Python/Lambda, invoke an approved Bedrock model, persist metadata/results in DynamoDB, and expose status via API Gateway. The agent must clarify data sensitivity, throughput, retention, latency, cost and failure recovery before committing to a design.

### Definition of MVP success

- One end-to-end demo produces a business-context summary, stakeholder/viewpoint matrix, 2+ architecture diagrams, 2+ ADRs, a traceability register, JIRA story drafts, runnable Python, Terraform and tests.
- Every generated implementation story references at least one requirement and one approved ADR or documented design rule.
- Generated Python passes lint and unit tests; Terraform passes fmt and validate; security scans run with findings reported.
- No external JIRA write, repository push or AWS apply occurs without an explicit approval step.
- An independent reviewer can follow one requirement from source to implementation and test evidence.

## 4. Reference architecture

VS Code (chat + custom agents) → Lead Architect agent → specialist agents (Business/BTABoK, Solution Architecture, JIRA, Python, AWS, Assurance). All specialists read the same Git-backed project context and write structured artefacts. MCP provides tool access to JIRA, GitHub and approved AWS operations. CI validates generated outputs. Future orchestration: LangGraph with durable state and Bedrock model access.

### Core design principles

- **Architecture before implementation**: requirements and ADRs are approved before build.
- **Git is the source of truth** for versioned artefacts; JIRA is the execution tracker, not the canonical requirement repository.
- **Deterministic templates and schemas** wherever possible; model-generated narrative is explicitly marked as proposal.
- **Least privilege**: read-only cloud discovery by default; no direct production mutation.
- **Human-in-the-loop** for high-impact decisions and writes.
- **Reproducibility**: record model/provider, prompts, tool actions, version, and validation evidence where permitted.

## 5. Agent contracts

| Agent | Inputs | Required outputs / authority |
| ----- | ------ | ---------------------------- |
| Lead Architect | Request + shared project context | Plan, dependencies, task routing, review gates; no silent external writes |
| Business / BTABoK | Drivers, stakeholders, constraints | Business context, concerns, capability impacts, viewpoint selection; no code |
| Solution Architect | Approved requirements and context | C4-style views, interfaces, NFRs, ADRs, options and rationale |
| JIRA | Approved work breakdown | Epic/story drafts, criteria, dependencies; publish only after approval |
| Python Engineer | Approved specs, ADRs | Python modules, tests, README; no infra apply |
| AWS Engineer | Approved architecture and NFRs | Terraform modules, IAM, observability, cost assumptions; no apply |
| Assurance | All outputs and test evidence | Quality/security/cost/traceability findings and release recommendation |

## 6. Canonical artefact model

| Type | Suggested fields |
| ---- | ---------------- |
| Requirement | id, source, description, business_outcome, priority, acceptance_criteria, status |
| Viewpoint | id, stakeholders, concerns, model_kind, linked_requirements, assumptions, version |
| ADR | id, context, options, criteria, decision, consequences, evidence, status |
| Work item | id, type, summary, criteria, dependencies, requirement_ids, adr_ids, jira_key |
| Implementation | path, component_id, requirement_ids, adr_ids, tests |
| Test evidence | test_id, requirement_ids, result, execution_timestamp, build_ref |

Traceability example: `OBJ-001 → REQ-014 → VIEW-003 → ADR-007 → STORY-012 → src/processor.py → TEST-028`. Referential integrity is enforced in CI; unstructured hyperlinks alone are not relied on.

## 7. Repository blueprint

```text
architecture-workbench/
  .github/agents/                 # specialist agent instructions
  .github/copilot-instructions.md
  .vscode/                        # workspace settings and tasks
  knowledge/btabok/               # licensed excerpts / curated guidance
  knowledge/standards/            # security and architecture principles
  templates/                      # viewpoint, ADR, requirement, story
  requirements/                   # structured requirement files
  architecture/viewpoints/
  architecture/decisions/
  architecture/diagrams/
  specs/                          # approved contracts and schemas
  traceability/                   # manifest and validation scripts
  src/                            # generated / reviewed Python
  infrastructure/terraform/
  tests/
  scripts/
  docs/                           # runbooks and decisions
```

## 8. Workflow and approval gates

| Stage | Exit evidence | Gate |
| ----- | ------------- | ---- |
| 1. Intake | Objectives, constraints, unknowns and requirements | User confirms scope |
| 2. Architecture | Viewpoints, alternatives, ADRs, NFRs | Architect approves ADRs |
| 3. Planning | Epics/stories, estimates as ranges, dependencies | Owner approves JIRA publication |
| 4. Build | Python, Terraform, tests and documentation | PR review |
| 5. Assurance | CI, threat review, cost and traceability reports | Reviewer approves release |
| 6. Deployment | Change record and approved execution plan | Separate authorised AWS apply |

## 9. Non-functional requirements and controls

- **Security**: scoped credentials, no secrets in prompts/repo, tool allowlists, short-lived AWS roles, prompt-injection-aware retrieval.
- **Data protection**: classify source documents; redact personal/sensitive content where feasible; define retention and model data policies.
- **Reliability**: idempotent work item creation, retry policies, resumable workflows and explicit partial-failure states.
- **Observability**: agent-run IDs, structured action logs, token/cost telemetry, validation outcomes and correlation IDs.
- **Quality**: schema validation, code tests, Terraform checks, SAST/dependency checks and traceability completeness.
- **Governance**: record who approved decisions and external changes; maintain audit trail and segregation of duties.
- **Licensing**: use approved BTABoK materials; do not assume permission to redistribute proprietary framework content.

## 10. Implementation backlog

| ID | Work item | Acceptance criteria | Priority |
| -- | --------- | ------------------- | -------- |
| EPIC-01 | Workspace foundation | VS Code repository, conventions, instructions, example request | P0 |
| ST-01 | Agent role definitions | Lead + six specialists, tool boundaries, outputs documented | P0 |
| ST-02 | Requirement schema and intake | Validated YAML/JSON, ambiguity questions, stable IDs | P0 |
| ST-03 | BTABoK viewpoint templates | At least 3 reusable viewpoints with concern mapping | P0 |
| ST-04 | ADR generation and review | Options, criteria, rationale and approval state | P0 |
| ST-05 | Traceability validator | Missing/broken links fail CI with actionable report | P0 |
| ST-06 | Python generation pipeline | Sample API/worker with pytest and lint passing | P1 |
| ST-07 | Terraform generation pipeline | fmt, validate, IAM review and scan pass | P1 |
| ST-08 | JIRA MCP integration | Preview + explicit confirmation + idempotent create | P1 |
| ST-09 | Assurance checks | Security, NFR and cost findings surfaced in PR | P1 |
| ST-10 | Golden-path demonstration | One complete scenario and reviewable evidence | P1 |
| EPIC-02 | Durable orchestration | Evaluate LangGraph/Bedrock after MVP metrics | P2 |

## 11. Proposed six-week MVP plan

| Week | Focus | Demonstrable result |
| ---- | ----- | ------------------- |
| 1 | Repo, instructions, roles, schemas | Structured intake and agent delegation |
| 2 | BTABoK context and viewpoint templates | Business + architecture document pack |
| 3 | ADRs, traceability, review gates | Decision-led architecture baseline |
| 4 | Python and AWS Terraform generation | Runnable code and validated infrastructure |
| 5 | JIRA MCP, assurance and CI | Controlled task publishing and quality reports |
| 6 | End-to-end demo, fixes, documentation | Reproducible golden-path workflow |

The timeline is a planning hypothesis for a focused prototype, not a delivery commitment. Re-estimate after week 1.

## 12. Key risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Invented business context | Explicit unknowns, evidence references and approval before design |
| Inconsistent agent outputs | Canonical schemas, shared IDs, validation and single source of truth |
| Incorrect BTABoK interpretation | Curated approved templates and expert review |
| Over-permissioned MCP tools | Least privilege, allowlists and manual approval for writes |
| Unreliable generated Terraform | Static checks, sandbox deployment and human review |
| Premature orchestration complexity | Begin with VS Code custom agents; add LangGraph only for demonstrated need |
| JIRA duplication or drift | Idempotency keys, dry-run previews and reconciliation |

## 13. Decisions to make before development

- Primary VS Code runtime: GitHub Copilot custom agents, or another supported coding agent? Default: Copilot for MVP.
- Models: hosted coding model initially; Bedrock as an enterprise-controlled later option.
- JIRA project, issue types, naming conventions and permission boundaries.
- BTABoK source material and approved viewpoint templates.
- Terraform conventions, AWS sandbox account, eu-west-1 deployment policy.
- Diagram format: Mermaid first; optionally Structurizr/C4 or PlantUML.
- Canonical requirement format: YAML with JSON Schema validation.

## 14. First build session: actionable checklist

- [ ] Create Git repository `architecture-workbench` and VS Code workspace.
- [ ] Add a representative requirement in `requirements/REQ-001.yaml`.
- [ ] Create `lead-architect` and `btabok-architect` instructions.
- [ ] Create templates for business context, stakeholder concerns, viewpoints and ADRs.
- [ ] Generate and review first architecture pack without writing code.
- [ ] Add a traceability manifest and a basic validator.
- [ ] Only then add Python, Terraform and JIRA agent capabilities.

## 15. Initial project definition / working agreement

- **Project name**: Architecture & Engineering Agent Workbench (working title)
- **Product owner**: TBD · **Technical owner**: TBD
- **Primary user**: architect/developer working in VS Code
- **Pilot use case**: serverless document processing
- **Success review**: end of week 6
- **Decision log location**: `architecture/decisions/`
- **Definition of done**: version-controlled outputs, validation evidence, traceability, approved external changes and repeatable demo

**Open questions**: Who will approve architecture outputs? Which JIRA Cloud project is available? Which BTABoK templates can be used? Is the initial AWS environment a sandbox? What data classification is permitted in prompts?

## Architecture artefacts

Use the [architecture artefact workflow](docs/architecture-workflow.md) to capture business context, map stakeholder concerns to viewpoints, and record architecture decisions with explicit human approval. Reusable, project-authored templates are in [templates/architecture/](templates/architecture/).

## Current implementation (this repository)

Serverless AWS application managed with Terraform: one Lambda per API endpoint behind an API Gateway HTTP API. Specs live in [specs/](specs/) (spec → plan → tasks → implement, with approval between phases).

### MCP endpoints and Bearer authentication (spec 007, in progress)

| Route | Purpose | Auth |
| ----- | ------- | ---- |
| `ANY /agent/mcp` | MCP server for the deployed AI agent (`ask_agent` tool) | `Authorization: Bearer <token>` |
| `ANY /gateway/mcp` | SigV4-signing proxy to the AgentCore gateway (`project1-dev-agent-gateway`) | `Authorization: Bearer <token>` |

A Lambda authorizer compares the presented token, in constant time, with a shared secret held in Secrets Manager (KMS-encrypted; value is never in Terraform or the repo). Results are cached for up to 5 minutes. A missing header returns 401; a malformed or wrong token returns 403.

Set the token after `terraform apply` (apply requires explicit approval):

```powershell
aws secretsmanager put-secret-value --secret-id <mcp_token_secret_arn output> --secret-string "<your-token>"
```

Add to VS Code (`.vscode/mcp.json`):

```json
{
  "inputs": [
    { "id": "mcp-token", "type": "promptString", "description": "MCP bearer token", "password": true }
  ],
  "servers": {
    "project1-dev-agent-gateway": {
      "type": "http",
      "url": "<gateway_mcp_url output>",
      "headers": { "Authorization": "Bearer ${input:mcp-token}" }
    },
    "project1-dev-agent": {
      "type": "http",
      "url": "<agent_mcp_url output>",
      "headers": { "Authorization": "Bearer ${input:mcp-token}" }
    }
  }
}
```

### Common commands

- Format: `terraform -chdir=infra fmt -recursive`
- Validate: `terraform -chdir=infra init -backend=false && terraform -chdir=infra validate`
- Lint: `tflint --chdir=infra`
- Security scan: `checkov -d infra`
- Plan: `terraform -chdir=infra plan -var-file=env/dev.tfvars`
- Tests: `python -m pytest tests`
