# Gaps — what is blocked, and the ask that unblocks it

Every gap below is verified against `AI-Consortium/luminate` `origin/main` @ `10d6ee89`
(2026-09-01) or against the live SLF dev estate on the same date. Each names an owner: a
**consortium** gap is a change to Luminate itself; a **Sun Life** gap is ours to close.

## G-1 · Tool-granular authorization does not exist — **consortium**

| | |
|---|---|
| **What is missing** | An access decision that can name a tool |
| **Proof** | `AccessPolicyTargetType` = `mcp_server`, `agent`, `model`, `location`, `environment` — none is a tool. `AccessPolicy.allowed_tool_ids` has **no runtime consumer** in the gateway tree, the policy engine or any Rego package. The gateway parses the JSON-RPC method *after* `check_access` returns, for telemetry |
| **Impact** | A grant covers every tool a server exposes, now and in future |
| **Workaround** | MSR-15 one server per trust boundary; MSR-16 server-side tool authorization where that is impossible |
| **Ask** | Add a tool target type — or make `allowed_tool_ids` load-bearing — and carry the JSON-RPC method into `AuthzRequest` |
| **Also** | Correct **CAP-03** in the capability map, which currently claims *"tools bound to agents rather than assumed"* at ✅ Available |

## G-2 · No tool discovery — **consortium**

| | |
|---|---|
| **What is missing** | Any automatic read of a server's `tools/list` into the catalogue |
| **Proof** | A search for `last_discovery` across the backend returns zero on `origin/main`. `pharmacy-mcp-server`, live on a corporate-ingress path, carries **zero** `MCPTool` rows |
| **Impact** | The catalogue is a manual claim, not an inventory. An ISRA that reads it is reading a copy |
| **Workaround** | MSR-6 makes catalogue accuracy a release-time obligation, verified by diffing against live `tools/list` |
| **Ask** | Land discovery — the work exists on an unmerged branch — with a recorded discovery timestamp, status and error so staleness is visible |

## G-3 · Two identity modes are enum-only — **consortium**

| | |
|---|---|
| **What is missing** | `injected_credential` (spend a stored per-deployment credential) and `external_exchange` (a second RFC 8693 exchange against the server's own authorization server) |
| **Proof** | The `MCPServerIdentityMode` docstring: *"Neither mechanism is implemented yet — a server in either mode is served like `GATEWAY_IDENTITY`, with no credential sent, until its mechanism lands"* |
| **Impact** | A server fronted by a third-party authorization server **cannot be onboarded**. Selecting either mode produces no error and no credential |
| **Workaround** | None. `gateway_identity` sends nothing; `token_forward` requires the third party to trust *our* issuer, which it does not |
| **Ask** | Implement one of the two. `injected_credential` is the smaller and serves the common SaaS case |
| **Per-user case** | Neither mode reaches a vendor *as the individual user*: `injected_credential` is one shared credential per deployment, so every caller gets the service account's reach and the vendor's audit loses the person. A server that must act with the user's own three-legged OAuth token is a separate consortium ask, [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) *Per-User Third-Party Connections* ([EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444)) |

## G-4 · The kill switch is a status edit and its propagation is unmeasured — **consortium + Sun Life**

| | |
|---|---|
| **What is missing** | A stop endpoint, an audited stop event, and a published propagation interval |
| **Proof** | Withdrawal is a `status` edit or a governance transition; the fact export filters to active resources so the resource drops out of the next bundle. Configuration reaches gateways by push, but the interval has never been measured on the SLF estate |
| **Impact** | Incident response has no stated time-to-effect. B-13 Principle 17 wants one |
| **Workaround** | Deleting the `AccessPolicy` is faster for a single caller — authorization is per request with no cache |
| **Ask** | Consortium: a first-class stop with an audited event. Sun Life: **measure and publish** the interval per environment (D3 T13) |

## G-5 · The platform never probes MCP server health — **consortium**

| | |
|---|---|
| **What is missing** | Any readiness or liveness check against a registered backend |
| **Proof** | Searches for health, probe and readiness across the MCP registry app and the gateway sync return zero. `MCPServer.status` is operator-set |
| **Impact** | A dead backend is discovered by a failing tool call. `status = active` is not a health signal |
| **Workaround** | Hosting-platform probes plus alerting on gateway 5xx per endpoint |
| **Ask** | A periodic backend probe that moves `status` and surfaces in the portal |

## G-6 · Scanning gates are disabled across the ACP estate — **Sun Life**

| | |
|---|---|
| **What is missing** | Enforcement. The libraries default to `ENFORCE_SNYK_GATE = true` and `ENFORCE_CHECKMARX_GATE = true`; `acp-agent-registry`, `acp-mcp-registry` and `agent-control-plane-ui` all set both to `false` |
| **Impact** | The supply-chain control is nominal. The scans run and nothing fails on them |
| **Workaround** | None — it is a configuration decision |
| **Ask** | Ship MCP server repositories with the gates on (MSR-20 to MSR-22); re-test and remove the two inherited `disable_gate_reason_*` strings, or convert them into exceptions with an owner and a review date |

## G-7 · The Checkmarx gate passes without scanning — **Sun Life**

| | |
|---|---|
| **What is missing** | Fail-closed behaviour when no scan exists |
| **Proof** | `libraries/checkmarx/steps/code_analysis.groovy` resolves the latest **merged PR**, reads the scan Checkmarx already ran for it, and reports the verdict. With no merged PR it logs `New repository PR does not exist. Checkmarx scan is skipped.` and continues. Default `branches_to_scan` is `["develop"]` |
| **Impact** | A new repository, or one whose integration branch is `main`, is unscanned and green |
| **Workaround** | MSR-20 requires the scan id and gate evaluation as evidence, not the stage colour |
| **Ask** | Sun Life AppSec / GDS: make a missing scan a failure rather than a skip, or require the evidence check in the ISRA. Every MCP server repo sets `branches_to_scan` explicitly |

## G-8 · No per-server quota or spend budget — **consortium**

| | |
|---|---|
| **What is missing** | Any enforced call or spend limit on an MCP server |
| **Proof** | The quota dimension enum stops at requests and tokens; the gateway tree has **zero** quota references; `matched_quota_ids` is put on a span as a count and returned on the decision — telemetry, not enforcement |
| **Impact** | A runaway agent's tool calls are unbounded by the platform |
| **Workaround** | Server-side rate limiting |
| **Ask** | Make quotas enforced at the gateway, with an MCP-call dimension |

## G-9 · The governance axis is inert — **Sun Life**

| | |
|---|---|
| **What is missing** | Applicability rules. The governance ruleset machinery, the guarded transition, the self-approval refusal and the suspension cascade preview all exist and work |
| **Impact** | Every MCP server sits at `not_evaluated`. Any gate reading governance state is vacuous |
| **Workaround** | None needed — the mechanism is ready; the content is not authored |
| **Ask** | `governance-intake` (EACPP-877) authors the rules. Do not present `governance_state` as an operating control until it does |

## G-10 · The AgentCore route decision is open — **Sun Life**

| | |
|---|---|
| **What is missing** | A recorded decision on whether an AgentCore-hosted MCP server is reached through `{gateway}/mcp/{endpoint}` or SigV4-direct to the runtime ARN |
| **Impact** | Only the gateway route is governed. A direct call has no policy, no audit event and no attribution. Luminate's MCP outbound modes emit a bearer token, not SigV4 |
| **Workaround** | Route through the gateway; accept that a SigV4-only backend is not yet expressible |
| **Ask** | Decide once, for agents and MCP servers together — the same question `integration-patterns` T5 raises |

## G-11 · AWS-native invoke auth (SigV4) is not expressible — **consortium**

| | |
|---|---|
| **What is missing** | Any way for the MCP outbound path to sign a request to an AWS target |
| **Proof** | At `origin/main` `1c4a00035` (2026-09-08) the translator emits exactly three backend-auth shapes — `token_exchange`, `forward` (passthrough), `none`. A search for SigV4 or AWS auth across `gateway/app/services` and `gateway/app/middleware` returns **zero** |
| **Impact** | Spans two substrates. An AgentCore runtime expecting a signed request (**S3**) and a Lambda Function URL with `AuthType: AWS_IAM` (**S5**) cannot be reached with their native auth |
| **Workaround** | Front the target with something that accepts a bearer (private API Gateway), or reach it as `gateway_identity` over a network-restricted path and carry no caller identity |
| **Ask** | A SigV4 backend-auth mode on the MCP and A2A outbound paths, so AWS-native targets are first-class rather than requiring a shim |

## Gap summary

| Gap | Owner | Blocks | Severity |
|---|---|---|---|
| G-1 tool-granular authorization | Consortium | Fine-grained least privilege | **High** — compensated architecturally |
| G-2 tool discovery | Consortium | A trustworthy inventory | **High** — compensated by process |
| G-3 third-party identity modes | Consortium | Vendor MCP onboarding; per-user vendor access ([ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165)) | **High** — no workaround |
| G-4 kill switch and propagation | Both | Stated incident response time | Medium |
| G-5 health probing | Consortium | Operational visibility | Medium |
| G-6 disabled scanning gates | Sun Life | Supply-chain assurance | **High** — ours to fix |
| G-7 vacuous Checkmarx gate | Sun Life | SAST assurance | **High** — ours to fix |
| G-8 quotas not enforced | Consortium | Bounded blast radius | Medium |
| G-9 inert governance rules | Sun Life | Governance gating | Medium |
| G-10 AgentCore route | Sun Life | The AgentCore substrate | Medium |
| G-11 SigV4 not expressible | Consortium | The AgentCore and Lambda substrates | Medium — shim available |

The three that are entirely ours — **G-6, G-7 and G-9** — are also the three that most directly
weaken an assurance submission. They need no consortium change and should not wait for one.
