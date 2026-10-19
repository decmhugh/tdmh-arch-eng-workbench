# Engineer Onboarding for the ACP Program — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft (retroactive) | **D2 Approved**: n/a
> **Epic**: [EACPP-896](https://sunlife.atlassian.net/browse/EACPP-896) · Board label `acp-product-team`

> ## ⚠️ Tickets already exist — do not run `create_jira_from_spec.py` on this spec
>
> The 12 tickets below were created by hand on 2026-08-12, before this spec was written. Their
> summaries use the form `Task 1 - …`, not the `T<n>: …` form the generator matches on, so a run
> would create a **second, duplicate set of 12 tickets** rather than recognising these.
>
> The step tables below deliberately avoid a `Task` / `Description` header so the generator's
> table parser skips them. If this spec ever needs generated tickets, reconcile the summaries
> first.

## Ramp steps

Three steps, run in order, instantiated once per engineer.

| Ramp step | Covers | Sequence |
|-----------|--------|----------|
| **Step 1 — Access & Environment Onboarding** | AWS SSO via `users_aws_edae_acp_run`; Jenkins via `User_JenkinsProdACPMember_ML`; Bitbucket `T1KACP` + `EDAEACP` and the seven core clones; kubectl context to `slf-eks-t1k-ca-dev`; read `acp_links_and_groups.md` and the onboarding guide (*Choosing Your Path*, *Alpha*, *Beta*). (DD-7, FR-1→FR-4) | first — externally gated |
| **Step 2 — Run Both Builds Locally** | Alpha: `task up`, `task smoke`, UI `:3002`, Jaeger `:16686`, optional `task up-llm` / `task bedrock:up`. Beta: `task start`, portal `:3000`, gateway `:18080`, Langfuse `:3001`, `task urls`. Sign in to the portal, walk *Signing In* / *Getting Access* / *Register an MCP Server*, register an agent/model/MCP server through **each** stack, read the Beta roadmap, log friction as comments. (DD-2, DD-6, FR-5→FR-7, FR-14, FR-15) | after Step 1 |
| **Step 3 — Harness SDK + Product-Specs Ramp** | Run `examples/local/quickstart_local.py` against Alpha; read the SDK user guide and review `ACPSettings`, `GatewayClient`, `RegistryClient`, `OktaAuthProvider`; walk `acp-agentcore-sample` and re-point the harness at local Luminate via `ACP_*` env vars; read `aws-harness-integration` D3 and `acp-harness-sdk` D3; write the "what changes for Luminate" summary; pick one EACPP-707 / EACPP-791 task to shadow or scope. (DD-3, DD-4, FR-8→FR-12) | after Step 2 |

## Ticket matrix

One ticket per step per engineer, all parented to EACPP-896.

| Ramp step | Alex Mckenzie | Kieran Gibney | Sam Mamelli | Rushik Patel |
|-----------|---------------|---------------|-------------|--------------|
| Step 1 — Access & Environment | [EACPP-897](https://sunlife.atlassian.net/browse/EACPP-897) | [EACPP-900](https://sunlife.atlassian.net/browse/EACPP-900) | [EACPP-903](https://sunlife.atlassian.net/browse/EACPP-903) | [EACPP-906](https://sunlife.atlassian.net/browse/EACPP-906) |
| Step 2 — Both builds locally | [EACPP-898](https://sunlife.atlassian.net/browse/EACPP-898) | [EACPP-901](https://sunlife.atlassian.net/browse/EACPP-901) | [EACPP-904](https://sunlife.atlassian.net/browse/EACPP-904) | [EACPP-907](https://sunlife.atlassian.net/browse/EACPP-907) |
| Step 3 — Harness + specs ramp | [EACPP-899](https://sunlife.atlassian.net/browse/EACPP-899) | [EACPP-902](https://sunlife.atlassian.net/browse/EACPP-902) | [EACPP-905](https://sunlife.atlassian.net/browse/EACPP-905) | [EACPP-908](https://sunlife.atlassian.net/browse/EACPP-908) |

## The "what changes for Luminate" summary

Step 3's write-up is the comprehension check (DD-4). It must cover all four points:

| # | Change | From (Alpha) | To (Beta / Luminate) |
|---|--------|--------------|----------------------|
| 1 | Gateway auth | `x-acp-agent-id` header | `/llm` with a Bearer JWT |
| 2 | Catalog access | internal registry calls | `/api/v1/catalog/{agents,mcp-servers,models}` |
| 3 | Token acquisition | SDK-local | portal token provider `/api/v1/iam/auth/token` |
| 4 | Model access | cross-account Bedrock assume-role | dropped |

## Definition of Done

Per engineer:

- Access confirmed across AWS, Jenkins, Bitbucket and kubectl — able to list pods in an `acp-*` namespace.
- Both stacks running locally, with an agent/model/MCP server registered through each.
- Harness quickstart run against Alpha and re-pointed at local Luminate.
- Both driving D3 specs read; the four-point summary written as a ticket comment.
- One EACPP-707 / EACPP-791 task named to shadow or scope.
- Friction logged as comments and raised against the onboarding guide.

## Reporting follow-up

`acp-reporting-agent` routes EACPP-896 to Workstream 3 via a hardcoded fallback:

```python
# reporting/connectors/slf_o7_jira.py
# Delete an entry once its spec lands with `spec_type: onboarding` — routing then comes
# from the spec and the swimlane picks up the spec title automatically.
WS3_EPICS_WITHOUT_SPEC = { "EACPP-786": ..., "EACPP-876": ..., "EACPP-896": ... }
```

This spec is `spec_type: onboarding`, so **once it is merged to `main`** the `EACPP-896` entry
should be deleted and routing will come from the spec. `load_spec_map()` reads spec.yaml from the
Bitbucket default branch, so removing the entry before the merge would drop EACPP-896 into
*"No component"* and flag its tickets as unmapped. Order matters.

## References

- Spec: [D0](d0-discovery.md) · [D1](d1-requirements.md) · [D2](d2-design.md)
- Epic: [EACPP-896](https://sunlife.atlassian.net/browse/EACPP-896)
- [ACP Onboarding Guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-onboarding-guide/bb-pages/browse/)
- Downstream delivery: [`aws-harness-integration`](../../integration/aws-harness-integration/d3-tasks.md) (EACPP-707) ·
  [`acp-harness-sdk`](../../platform/acp-harness-sdk/d3-tasks.md) (EACPP-791) ·
  [`sunlife-deployment`](../../platform/sunlife-deployment/d3-tasks.md) (EACPP-596)
