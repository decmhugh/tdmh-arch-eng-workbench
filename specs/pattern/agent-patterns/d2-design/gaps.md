# Gaps — what is blocked, and who owns the ask

Split by owner, because the two lists move at different speeds and through different forums. A
**consortium** gap needs Luminate itself to behave differently and goes to the AI Consortium via
the design and delivery process. A **Sun Life** gap is something ACP must do to reach a Sun Life
system, or to operate what already exists, and stays here.

The delineation rule is
[`docs/process/capability-gap-escalation.md`](../../../../process/capability-gap-escalation.md):
*does Luminate itself have to behave differently, or does ACP just have to reach a Sun Life
system?*

---

## Consortium asks — Luminate must behave differently

### G-1 · The kill switch does not stop egress · **CAP-11** · Severity: **high**

`authz.rego`'s source rule is `_source_matches(policy) if { policy.source_id == input.jwt.sub }`.
It never consults `input.agents`, so `Agent.status` is irrelevant to whether an agent may call.
`_collect_policies()` filters on `AccessPolicyStatus.ACTIVE` and not on the source's status, and
`AuthNService.verify_api_key` checks the key's status and never `owner_agent.status`.

**Ask.** Add a source-side status check symmetric with `allowed_agents`, so a non-`active` source
agent (and an API key whose owner is non-`active`) is denied. The fact bundle already carries
`input.agents` keyed by id, so the data is present.

**Interim.** ASR-32: revoke the credential and revoke or suspend the source access policies; the
runbook says so and the drill measures it. → D3 **T25**

### G-2 · A guardrail cannot be bound to an agent as a callee · **CAP-10** · Severity: **high**

`GuardrailAttachment` has `target_model` and `target_mcp_server` and no `target_agent`
(`grep -rn "target_agent" backend/app/guardrails/` → 0), and
`_TARGET_SCOPED_FLOWS = frozenset({"model", "mcp_server"})` because *"`authz.rego` has a model
branch and an mcp_server branch and no agent branch"*.

An agent accepting A2A traffic therefore cannot require a prompt-injection or PII scan of its own
inbound requests. This is the sharpest asymmetry with the MCP lane, which does have
target-scoped guardrails — and the agent lane is the one where the inbound payload was composed
by a model.

**Ask.** A `target_agent` attachment scope and an agent branch in the Rego, mirroring
`target_mcp_server`.

**Interim.** ASR-22: every caller granted the endpoint carries a source-scoped attachment with
`agent` in `applies_to_target_types`, and the callee records the requirement. → D3 **T26**

### G-3 · Governance state enforces nothing · **CAP-14** · Severity: **high**

```text
grep -rn "governance_state" backend/app/policy_engine/ backend/app/access_policies/ gateway/app/  → 0
grep -rn "governance"       backend/app/policy_engine/rego/                                        → 0
```

`backend/app/governance/suspension.py` is explicit that this is known and deliberate: the
enforcement half belongs to a later epic, and *"the state is real and the denial is not"*.

**Ask.** Land the enforcement epic so a `suspended` or non-`approved` resource is denied at the
access layer, and expose the derivation so an assessor can see which state produced which outcome.

**Interim.** ASR-10 records it as evidence. Declared as residual risk R-3 and never cited as a
control. → D3 **T27**, tracked with `governance-intake` (EACPP-877)

### G-4 · No reachability or health signal for an agent backend · **CAP-01** · Severity: medium

The asymmetry is in the data model. `MCPServerDeployment` carries `health_status`,
`last_checked_at` and `last_error`, fed by a `ProbeMcpCommand` the gateway acts on and reported
back on the health report. **`AgentDeployment` has exactly two fields** — `endpoint_name` and
`backend_endpoint` — and no probe anywhere. Registration accepts any well-formed URL, nothing
calls it, and `Agent.status` is operator-set and means "should this be served", not "is this up".

**Ask.** An agent equivalent of the MCP probe, and a registration-time reachability check.

**Interim.** ASR-7 makes a post-registration call a release obligation; alert on gateway 5xx per
endpoint name. → D3 **T28**

### G-5 · No agent card, and none can be fetched through the gateway · **CAP-01** · Severity: medium

```text
grep -rin "agent-card|agent.json|agentcard" gateway/app backend/app --include=*.py  → 0
```

and `/.well-known/` is **served locally** by the gateway rather than proxied, so a caller cannot
reach a callee's own card even where the agent publishes one. A2A clients that bootstrap from an
agent card cannot do so through the platform.

**Ask.** Either serve an agent card derived from the catalogue at
`{gateway}/a2a/{endpoint_name}/.well-known/agent-card.json`, or proxy the backend's own.

**Interim.** ASR-12 makes the catalogue record the capability inventory. → D3 **T29**

### G-6 · The agent lane stamps no GenAI operation name · **CAP-20** · Severity: medium

`_stash_genai_operation` is explicit that this is a deliberate deferral: *"The agent lane stamps
nothing for now — it is a proxied A2A call, and which operation name fits it is a question for
whoever brings that lane's measures up."* Langfuse therefore types an A2A hop as a plain span.

The consequence is not the hop's own cost — it genuinely has none — but that a delegation chain
has no first-class shape in the usage model. `ProjectUsageDaily` aggregates by `usage_date` with
no run dimension, so "what did this chain cost" is answerable only by Langfuse session grouping.

**Ask.** An operation name for the A2A lane from the OTel GenAI vocabulary (`invoke_agent` is the
obvious candidate), and a chain-aware view in the usage model.

**Interim.** ASR-31 (forward the delegated token) plus ASR-33 (propagate the session id). →
D3 **T30**

### G-7 · The registered query string is discarded on the A2A hop · Severity: low

`_split_api_base` returns `parsed.path` and drops the query. Prod registers
`…/invocations?qualifier=DEFAULT` and the emitted rewrite is `…/invocations`. Harmless for the
default qualifier; a silent mis-route for any other.

**Ask.** Preserve the registered query in `urlRewrite`, or reject a `backend_endpoint` carrying
one so the failure is loud.

**Interim.** ASR-6 states it; the AgentCore annex says to rely on the default qualifier. →
D3 **T31**

### G-8 · Quotas are not enforced on any lane · **CAP-13** · Severity: medium

`grep -ril quota gateway/app/` → 0 files. Already raised by
[`mcp-server-patterns`](../../mcp-server-patterns/d2-design/gaps.md); **not duplicated here**, but
it lands harder on this lane because an agent is an autonomous caller that can loop.

**Interim.** ASR-23 pushes the bound to the substrate. Residual risk R-5.

### G-14 · No governed path from an agent to a REST API · **CAP-08** · Severity: medium

The gateway matches `/llm/`, `/mcp/` and `/a2a/` and nothing else, and `AccessPolicyTargetType`
has no API member. An enterprise API can only be governed by wrapping it as an MCP server.

Andrew Culberson's **D1 — API Resources** (`luminate-designs` branch `d1/skills-registry`,
**Status: Draft, Decision: Pending, not merged**, 30 commits behind main) would make a plain HTTP
API a first-class target with gateway-injected upstream credentials and optional operation-level
grants. It also blocks the **Skills Registry** D1, which needs a governed API concept to bind
skill declarations to.

**This one is not purely a consortium ask.** Sun Life decided on 2026-09-02 (Enterprise
Architecture + EDAE ACP, Option 2) that the API Platform keeps the REST estate and that *"the MCP
boundary is where Luminate's remit ends"*. API Resources **as drafted** points the other way,
because it moves the REST estate inside Luminate's remit.

**The intended direction resolves that.** Sun Life wants direct API calls brought into governance
through an **Agent Skills / plugins registry integrating with the API Platform** — ACP governs
which agent may call which API; the API Platform keeps the hop and the Okta authentication.
Governance moves, the traffic path does not, and that shape is compatible with Option 2 where
API Resources as drafted is not. It is a **future roadmap item for the AI consortium** — no design,
no commitment, no date — and is **explicitly out of scope for this pattern**. The ask to carry to
the consortium is therefore the narrow one, not "adopt API Resources".

**Interim, and what this pattern assumes throughout.** ASR-36: reach APIs through an MCP server.
→ D3 **T32**

### G-15 · No cross-IdP exchange — the user's identity stops at the MCP server · **CAP-24** · Severity: medium

Luminate's provider registry holds `keycloak`, `authentik` and `entra`. **There is no Okta
`OAuthProvider`** — every Okta reference in the backend concerns *human* portal SSO federation.
And the exchange is single-provider by construction:

```python
def delegated_exchange_provider() -> OAuthProvider | None:
    """The active OAuth provider iff it supports RFC 8693 delegated exchange."""
    provider = registry.get(OAuthProvider, settings.SSO_OAUTH_PROVIDER)
```

So a **Keycloak → Okta on-behalf-of hop is not expressible**, and the enterprise REST API sees the
MCP server's own service identity rather than the end user.

**Two owners.** The platform side is a consortium ask (a second exchange target). The other side
is a **Sun Life trust-federation decision**: for the MCP server to exchange a Luminate token for
an Okta one, Okta must trust the Luminate issuer. Nobody has taken that decision, and it is not a
configuration change.

**Interim.** ASR-38 records which identity the API actually sees, and
[`mcp-server-patterns`](../../mcp-server-patterns/d1-requirements.md) MSR-16 makes the MCP server
enforce its own authorization from the identity it does receive. → D3 **T33**

---

## Sun Life work — ours to do

### G-9 · Prod runs a build that predates the A2A exchange · Severity: **high** · time-boxed

Every prod-cluster component is `sha-89356d7`, 49 commits behind `main`. At that revision
`backend/app/agents/audiences.py` does not exist and `_build_agent_assignments` carries the
docstring *"Agents aren't routed through agentgateway"*. All four prod A2A routes are therefore
emitted with `["a2a", "backendTLS"]` and **no `backendAuth`** — the caller's credential is
forwarded unchanged to `bedrock-agentcore.ca-central-1.amazonaws.com`.

Not exploitable today: prod holds **zero** `target_type = agent` access policies, so every A2A
request denies at `CheckAccess` before it is proxied. The control holding the line is the absence
of a grant.

**Fix.** Uplift the prod image past the exchange. **Until then, FR-11: no `target_type = agent`
policy is created in prod.** → D3 **T4**

### G-10 · The harness SDK cannot reach the A2A lane · Severity: **high**

Three independent defects in `A2AClient.invoke_gateway` at v0.13.0:

1. **No credential.** The method sets `content-type` and `x-acp-agent-id`; `build_http_client`
   adds only `x-session-id`. Searching `a2a.py` for `auth|authorization|bearer|get_token` returns
   three hits, all prose in docstrings. A Luminate gateway answers 401.
2. **Wrong credential shape.** `resolve_auth_provider(surface="gateway")` prefers a `lum_` API
   key, which a delegated A2A endpoint refuses with `api_key_not_exchangeable` — and every
   routable agent endpoint on `main` is delegated.
3. **Wrong key.** It builds `{a2a_gateway_url}/a2a/{target_agent_id}` while the gateway routes by
   **endpoint name**; and the default `a2a_gateway_url` already ends in `/a2a`, so the composed
   URL is `…/a2a/a2a/{id}`.

Plus: `x-session-id` and `x-acp-agent-id` are both unread by Luminate
(`grep -ri` over `gateway/` and `backend/` returns zero for each), so run correlation falls back
to `traceparent` or nothing.

**Fix.** Attach the resolved provider, select client credentials on the A2A surface, address by
endpoint name, and emit `x-luminate-session-id`. Each with a test. → D3 **W5** (T19)

### G-11 · The estate does not match its own grants · Severity: medium

`claims-intake → claims-adjudicator` is an active `target_type = agent` policy in dev against an
agent with no `AgentDeployment`. Ten of ten dev agents sit at `governance_state = not_evaluated`.
`framework` carries a typo, a stale package name and a blank. Prod registers one AgentCore runtime
under four gateways.

**Fix.** Run the FR-3 reconciliation queries, remediate, and put them on a schedule. →
D3 **W2** (T1, T10)

### G-12 · Scanning gates are disabled estate-wide · **INT-08** · Severity: medium

Re-verified 2026-09-08: `acp-harness-sdk` and `agent-control-plane-ui` both carry
`enforce_snyk_gate = false` and `enforce_checkmarx_gate = false` with setup-era reasons. Shared
with `mcp-server-patterns`; the Checkmarx step's PR-scan behaviour makes a green stage vacuous
where no merged-PR scan exists.

**Fix.** Enable the gates on agent repositories and evidence the scan id, not the stage. →
D3 **W3** (T11–T13)

### G-13 · No agent has been onboarded on OpenShift or Lambda · Severity: medium

S1 and S4 are specified and unexercised. The MCP lane needed two independent fixes before an
OpenShift-hosted backend worked — the CA bundle and the Gatekeeper init-container limits — and
the Lambda cold-start-versus-token-cache constraint is a design question, not a configuration one.

**Fix.** Prove one agent on each shape and fold the findings back into the annex. → D3 **W6** (T20, T21)

---

## Summary

| # | Gap | Owner | Capability | Severity | Interim | Ticket |
|---|---|---|---|---|---|---|
| **G-1** | Kill switch does not stop egress | Consortium | CAP-11 | **High** | Revoke credential + policies (ASR-32) | T25 |
| **G-2** | No guardrail can target an agent | Consortium | CAP-10 | **High** | Caller-side guardrails (ASR-22) | T26 |
| **G-3** | Governance state enforces nothing | Consortium | CAP-14 | **High** | Record only (ASR-10); R-3 | T27 |
| **G-4** | No reachability or health probe | Consortium | CAP-01 | Medium | Post-registration call (ASR-7) | T28 |
| **G-5** | No agent card through the gateway | Consortium | CAP-01 | Medium | Catalogue as inventory (ASR-12) | T29 |
| **G-6** | No GenAI operation name on the lane | Consortium | CAP-20 | Medium | Forward the delegated token (ASR-31) | T30 |
| **G-7** | Query string discarded | Consortium | — | Low | Use the default qualifier (ASR-6) | T31 |
| **G-8** | Quotas not enforced | Consortium | CAP-13 | Medium | Substrate bound (ASR-23) | *raised by MCP* |
| **G-14** | No governed agent→REST path | Consortium **+ SLF decision** | CAP-08 | Medium | Reach APIs via an MCP server (ASR-36) | T32 |
| **G-15** | No Keycloak→Okta exchange | Consortium **+ SLF federation** | CAP-24 | Medium | Record the identity the API sees (ASR-38) | T33 |
| **G-9** | Prod predates the A2A exchange | **Sun Life** | CAP-08 | **High** | No prod A2A grants (FR-11) | T4 |
| **G-10** | Harness SDK cannot reach the lane | **Sun Life** | — | **High** | — | T19 |
| **G-11** | Estate does not match its grants | **Sun Life** | CAP-01 | Medium | FR-3 queries | T1, T10 |
| **G-12** | Scanning gates disabled | **Sun Life** | INT-08 | Medium | — | T11–T13 |
| **G-13** | S1 and S4 unexercised | **Sun Life** | — | Medium | — | T20, T21 |

**Three of the four high-severity gaps are consortium-owned, and all three are the same shape**:
a governance surface that is modelled, visible in the portal, and does not act. That is the
message to take to the consortium — not seven separate feature requests.

**G-14 and G-15 are a different shape and need a different forum.** Neither is closable by the
consortium alone: one needs Sun Life to decide whether Luminate or the API Platform fronts the
REST estate, the other needs Okta to trust the Luminate issuer. Both are Enterprise Architecture
decisions with a consortium dependency, not feature requests.
