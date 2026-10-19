# Engineer Onboarding for the ACP Program — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft (retroactive) | **D0 Approved**: n/a — written after delivery began

## The two stacks an engineer must understand

The ramp is shaped by this distinction; everything else follows from it.

| | **Alpha** — internal build | **Beta** — Luminate |
|---|---|---|
| Repo | `T1KACP/agent-control-plane` | `EDAEACP/luminate` |
| Bring-up | `task up` (+ `task smoke`) | `task start` (+ `task urls`) |
| UI | `localhost:3002` | portal `localhost:3000` |
| Gateway | in-stack | `localhost:18080` |
| Observability | Jaeger `localhost:16686` | Langfuse `localhost:3001` |
| Registration | SDK self-register | portal UI |
| Auth to gateway | `x-acp-agent-id` header | Bearer JWT via `/api/v1/iam/auth/token` |
| Model access | Ollama (`task up-llm`) or Bedrock cross-account assume-role (`task bedrock:up`) | no cross-account assume-role |
| Status | proved the concepts | **go-forward runtime** |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Each engineer obtains **AWS dev/test access** via `users_aws_edae_acp_run` (su account), can `aws sso login` to `t1k-agent-control-plane-dev-ca` and list resources. | Must |
| FR-2 | Each engineer obtains **Jenkins access** via `User_JenkinsProdACPMember_ML` (regular user) and can view a build and a deploy job in the `EDAEAgentControlPlane` folder. | Must |
| FR-3 | Each engineer has **Bitbucket access** to `T1KACP` and `EDAEACP` and has cloned the seven core repos. | Must |
| FR-4 | Each engineer has a working **kubectl context to `slf-eks-t1k-ca-dev`** and can list pods in an `acp-*` namespace. | Must |
| FR-5 | Each engineer runs the **Alpha stack** locally: `task up` succeeds, `task smoke` passes, UI and Jaeger reachable. | Must |
| FR-6 | Each engineer runs the **Beta (Luminate) stack** locally: `task start` succeeds; portal, gateway and Langfuse reachable. | Must |
| FR-7 | Each engineer **registers an agent, model and MCP server through each stack** — SDK self-register on Alpha, portal UI on Beta. | Must |
| FR-8 | Each engineer runs the **harness SDK local quickstart** against Alpha: self-register, list agents, register an MCP server/tool, route a governed LLM completion through the gateway. | Must |
| FR-9 | Each engineer **re-points the harness at their local Luminate gateway** using the `ACP_*` env vars. | Must |
| FR-10 | Each engineer reads the **two driving D3 specs** — `aws-harness-integration` (EACPP-707) and `acp-harness-sdk` (EACPP-791). | Must |
| FR-11 | Each engineer writes a **"what changes for Luminate" summary** covering: gateway `/llm` + Bearer JWT replacing `x-acp-agent-id`; the catalog viewsets `/api/v1/catalog/{agents,mcp-servers,models}`; the portal token provider `/api/v1/iam/auth/token`; dropping the cross-account Bedrock assume-role. | Must |
| FR-12 | Each engineer **picks one EACPP-707 or EACPP-791 task** to shadow or scope next. | Must |
| FR-13 | Setup **friction is recorded as ticket comments** and raised as candidate fixes to `acp-onboarding-guide` / `luminate-user-guides`. | Should |
| FR-14 | Each engineer reads the **Beta roadmap** so current state — and what is still marked *coming soon* — is understood. | Should |
| FR-15 | Optional model backend enabled on Alpha (`task up-llm` or `task bedrock:up`). | Could |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **Documentation-first.** The ramp consumes the published onboarding guide rather than restating it in tickets; a ticket links, it does not duplicate. | Must |
| NFR-2 | **Sequenced, not parallel.** Task 2 depends on Task 1 access; Task 3 depends on a running stack from Task 2. Attempting them out of order wastes the engineer's time. | Must |
| NFR-3 | **Both stacks, not one.** An engineer who has only run Alpha cannot reason about the migration work the D3 specs describe. | Must |
| NFR-4 | **Self-improving.** Every ramp run produces guide fixes; the ramp gets cheaper each time. | Should |
| NFR-5 | **Repeatable per engineer** — the same three tasks instantiate for each joiner without redesign. | Should |

## Constraints & Assumptions

- **Access lead time is outside the team's control** (EO-Q1). AD group membership is granted by
  the owning teams, so Task 1 can stall through no fault of the engineer. It is the critical path.
- The **environments, pipelines and tooling already exist** — no build-out is assumed or required.
- The **onboarding guide is live** and is the authoritative content; drift between guide and
  reality is the main quality risk, mitigated by FR-13.
- Luminate is **still evolving** — parts of the Beta experience are marked *coming soon*, so the
  ramp must set expectations rather than present Beta as finished (FR-14).
- The cohort is **four engineers onboarding concurrently**, so a guide defect blocks four people
  at once — which is also why the feedback loop pays for itself immediately.

## Open Questions

Carried from D0: EO-Q1 (ramp duration vs access lead time), EO-Q2 (definition of "ramped"),
EO-Q3 (does this scale past four engineers), EO-Q4 (does Alpha stay in the ramp).
