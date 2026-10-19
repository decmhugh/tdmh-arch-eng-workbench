# Anthropic Client Product & ACP Integration — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: EACPP-1319
>
> Everything marked **measured** in this document was observed against the dev
> install on 2026-09-14 by driving Claude Code and the Luminate gateway directly.
> Claims that are **not** measured are labelled as inference or as open.

## 0. What D0 asked, and what changed

D0 left seven open questions. Three are now answered from evidence, and one turns out
to have been framed the wrong way round.

| D0 open question | Status after D1 |
|---|---|
| How will users authenticate and be authorized to use the ACP route? | **Answered** — §2, §3. An AD group is necessary but not sufficient, and it is not the attribution mechanism. |
| What usage data is required to attribute token costs? | **Answered** — §4. The ledger already carries `user_id` and `user_email`; what decides attribution is the *token the client presents*, not the ledger. |
| One shared workload account or multiple? | **Answered** — §5. A per-project provider account binding exists, is deployed in dev, and is **not on the upstream main branch**. |
| Which client products are in the validation set? | **Narrowed** — §1. Only Claude Code is demonstrably configurable against a third-party endpoint. |
| Who owns the vendor relationship and chargeback model? | Open — governance, not technical. |
| What governance activities remain open? | Open — tracked against the October 31 target. |
| Detailed control interpretation of LVT 4 | Open. |

**The framing correction.** D0 treats access control and cost visibility as two
requirements. They are one. The identity the client presents to the gateway determines
*both* whether the call is allowed *and* who the cost lands on. A design that solves
access with a shared machine credential silently forecloses per-user attribution, and
no amount of downstream reporting recovers it. This is the single most consequential
decision in the onboarding and it is taken at §3.

---

## 1. Product scope — what can actually be pointed at ACP

D0 lists Claude Code, Claude Cowork, Claude Chat and Office add-ins as one wave. They do
not share a configuration surface, and only one of them is proven.

| Product | Third-party endpoint | Per-user credential | Evidence |
|---|---|---|---|
| **Claude Code** | Yes — `ANTHROPIC_BASE_URL` | Yes — `apiKeyHelper` runs a command per request | **Measured**: driven end-to-end against the dev gateway |
| Claude Cowork | Unconfirmed | Unconfirmed | Not tested |
| Claude Chat | Unconfirmed | Unconfirmed | Not tested |
| Office add-ins | Unconfirmed | Unconfirmed | Not tested |

**FR-1 — Confine the first wave to Claude Code until the others are evidenced.**
Claude Code has two properties the others are not yet known to have: an arbitrary base
URL, and a credential *helper* — an executable the CLI re-runs, which is what makes a
short-lived per-user token possible at all. A product that accepts only a static pasted
key cannot carry a rotating user identity and therefore cannot be attributed per user.

**FR-2 — Before admitting any further product, evidence both properties.** The
acceptance test is the one used here: point the client at a listener that records
request headers and confirm (a) it reaches a custom base URL, (b) which header carries
the credential, (c) whether the credential is refreshed. Product marketing claims of
"supports third-party inference" are not sufficient — see §2, where exactly that claim
was true and the integration still failed.
That listener is `scripts/header-probe.py` in
[`acp-claude-code-harness`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-claude-code-harness/browse),
which is the sample implementation for this onboarding.
---

## 2. Wire-protocol requirements

**Measured.** The gateway serves the native Anthropic Messages API on its LLM lane.

| Behaviour | Result |
|---|---|
| `POST {gateway}/llm/v1/messages` | 200, well-formed Anthropic Messages body |
| `"stream": true` | 200, real incremental SSE (`message_start` + deltas) |
| `?beta=true` query string the client appends | No effect |
| Access-policy denial | 403, correctly distinguished from authentication failure |

**FR-3 — The client must present its credential in `Authorization: Bearer` only.**

Claude Code with `apiKeyHelper` configured puts the credential in **two** headers:

```
authorization: Bearer eyJhbGciOiJ…
x-api-key:     eyJhbGciOiJSUzI1Ni…
```

The gateway authenticates on `x-api-key` first, tries to verify a JWT as a platform API
key, fails, and does not fall back to the valid bearer token beside it. Isolated by
holding the token constant and varying one header at a time:

| Request | Result |
|---|---|
| `Authorization` only | **200** |
| `Authorization` + `x-api-key` | **401** |
| `Authorization` + **empty** `x-api-key` | passes authentication |

The supported client-side mitigation is to blank the header
(`ANTHROPIC_CUSTOM_HEADERS: "x-api-key: "`), which preserves credential refresh.
`ANTHROPIC_AUTH_TOKEN` also sends only `Authorization`, but it is a *static* value and a
working session outlives a short-lived token.

**FR-4 — Fix the precedence at the gateway rather than in every client.** The mitigation
above is a per-client workaround for a platform defect. The gateway should prefer
`Authorization` when both are present, or fall through to it when API-key verification
fails. This is a consortium contribution, not Sun Life configuration.

**NFR-1 — Credential refresh must be automatic and shorter than the token lifetime.**
Gateway access tokens live **300 seconds** (measured). A coding session runs for hours. The
client must re-mint on a timer strictly below that.

---

## 3. Identity — the decision that determines everything downstream

### 3.1 How the platform derives a principal

**Measured / source-verified.** The gateway takes the JWT `sub` claim and composes
`luminate_principal_id = {entity_type}:{entity_id}`. That value is what flows onward into
telemetry and, ultimately, into the cost ledger.

The gateway accepts three credential shapes and routes them to different validators by
prefix: `lum_` (platform API key), `lud_at_` (user-delegated OAuth token), and otherwise
a JWT.

### 3.2 The consequence

| Credential the client presents | `entity_type:entity_id` becomes | Per-user attribution |
|---|---|---|
| Machine client-credentials JWT (one shared client) | `service_principal:<one uuid>` for **every** user | **Impossible** — one row per day for the whole population |
| User-delegated token (`lud_at_`) or user JWT | `user:<that user's uuid>` | **Works** — see §4 |

**FR-5 — Claude Code must present a per-user identity, not a shared machine credential.**
A shared credential satisfies the access-control requirement and destroys the cost
requirement in the same stroke. It is not recoverable downstream: the ledger records the
principal it was given.

### 3.3 Does an AD group need to happen?

**Yes, but for entitlement — not for attribution, and not for per-call authorization.**
Three separate things get conflated here and D0 merges them.

| Concern | Does an AD group solve it? |
|---|---|
| **Entitlement** — who may install the client and obtain a credential at all | **Yes.** This is the right instrument, and it lives in the desktop/identity estate, outside ACP. |
| **Attribution** — whose cost is this call | **No.** Attribution comes from the token presented on the call. A group gates who gets a token; it does not travel on the request. |
| **Per-call authorization** — may this caller use this model | **Not today.** See below. |

**Measured: a user group *can* be an authorization source, but nothing populates it from
an IdP.**

- `AccessPolicy.source_user_group` exists and is **read at runtime** — the reach
  calculation and quota matching both filter on `source_user_group_id`, and the rego
  iterates `input.principal.group_ids`. This is a genuine enforcement path, not a dormant
  field.
- `UserGroupSource` offers `local` and `idp_sync`, but `idp_sync` appears only as a
  *guard* that refuses manual user additions to a group marked as synced. There is no
  writer that populates membership from an identity provider.
- **There is no SCIM endpoint** (repo-wide search for `scim`: zero matches).

**FR-6 — Treat the AD group as the entitlement gate and mirror it explicitly.** Until
IdP-driven group sync exists, an AD group cannot drive Luminate authorization without a
manual mirror, which will drift silently and become a stale-access finding. Either:

- **(a)** use the AD group to gate credential *issuance* and keep Luminate authorization
  keyed on the user/project — recommended; or
- **(b)** sponsor group sync as a consortium contribution and depend on it — this is a
  platform change with its own lead time and should not sit on the October 31 path.

**FR-7 — A user must exist in Luminate for their calls to be attributable.** Per-user
attribution requires a `User` row to resolve `user_email` on the ledger. The provisioning
path for first-wave users is an open item (§7, G-3).

### 3.4 How Claude Code obtains a per-user token

**Measured.** `apiKeyHelper` is an arbitrary executable the CLI re-runs on a TTL and whose
stdout becomes the credential. It is the correct seam for a rotating per-user token.

**Source-verified constraint: there is no device-authorization grant.** The delegated
OAuth implementation supports `authorization_code` (PKCE S256 mandatory), `refresh_token`
and RFC 8693 token exchange. A repo-wide search for `device_code`, `device_authorization`
and `8628` returns **zero matches**.

That leaves two viable shapes, and rules out a third:

| Shape | Viable | Note |
|---|---|---|
| RFC 8693 token exchange — swap the user's existing desktop SSO token for a delegated token | Optimisation *(was Preferred; see DD-3, reversed 2026-09-16)* | No new login prompt, but depends on issuer trust (§6) — which brokering resolved without it |
| Authorization code + PKCE with a loopback redirect | **Viable** | The laptop has a browser; costs an interactive login per refresh window |
| RFC 8628 device flow | **Not available** | Does not exist; do not design against it |

---

## 4. Cost attribution requirements

**Measured / source-verified.** The chain is complete and already carries a user
dimension — this is better than D0 assumes.

```
gateway: JWT sub ──▶ luminate_principal_id = {entity_type}:{entity_id}
                          │
                     Langfuse trace user_id
                          │
                     ClickHouse traces.user_id
                          │
          dbos-worker rollup, grouped by user_id
                          │
   ProjectUsageDaily.user_id + .user_email + .cost_centre
                          │
            chargeback API, filterable by user_ids
```

- The ledger carries `user_id`, `user_email`, `cost_centre`, `project_id`, `entity_type`,
  `entity_id`, token counts and cost — `user_id` is part of the rollup's grouping key.
- The chargeback API exposes a `user_ids` filter, and **non-admin callers are restricted
  to their own usage**, which is the right default for a tool whose usage is personal.
- `cost_centre` is snapshotted onto the ledger row at rollup time from the project, so a
  later cost-centre change does not silently re-attribute historical spend.

**FR-8 — No new attribution plumbing is required.** The requirement is to feed the
existing chain a user identity (FR-5). Reporting work should not be commissioned before
the identity decision is taken; it would build on a principal that is a single shared
machine.

**FR-9 — State the granularity honestly.** The ledger aggregates by **calendar day**.
There is no run or session dimension on the finance-facing surface, so "what did this
session cost" is not answerable from chargeback — only from the trace store. If
per-session recovery is a requirement it is a gap, not a configuration.

**NFR-2 — Attribution must survive streaming.** Claude Code streams by default. Usage
accounting is retained across streamed responses (source-verified), so this is satisfied —
but any change to the streaming path must re-verify it.

---

## 5. Model access requirements — two gates, currently disjoint

**Measured. This is what blocks the end-to-end run today.**

Reaching a model through the gateway requires clearing *four* independent gates. Three
were passed; the fourth is an approval boundary.

| # | Gate | Where it lives | State |
|---|---|---|---|
| 1 | Luminate access policy, caller → model | ACP catalogue | **Granted** for the test workload |
| 2 | Provider account binding — which AWS account the call is signed into | ACP catalogue (`OfferingAccountBinding`) | **Created**; verified working |
| 3 | Spoke role IAM allow-list `InvokeApprovedBedrockModels` | Model AWS account | Model-specific |
| 4 | Bedrock Marketplace subscription | Model AWS account | Model-specific |

Gates 3 and 4 are maintained separately and **have drifted apart**:

| Model | IAM-approved (gate 3) | Invocable (gate 4) | Usable |
|---|---|---|---|
| `anthropic.claude-3-haiku-20240307-v1:0` | yes | yes | **yes** |
| `us.anthropic.claude-sonnet-4-6` | yes | **not subscribed** | no |
| `us.anthropic.claude-haiku-4-5-…` | yes | **not subscribed** | no |
| `us.anthropic.claude-3-sonnet-…` | yes | **retired id** | no |
| `us.anthropic.claude-sonnet-4-5-…` | **not in allow-list** | yes | no |

The intersection is exactly one model — Claude 3 Haiku — which **does not support prompt
caching**.

**FR-10 — The model must support prompt caching.** Claude Code sends
`cache_control: {"type": "ephemeral"}` blocks on the system prompt and tool definitions. A
model that does not support them refuses the request upstream:

```
403 "You invoked an unsupported model or your request did not allow prompt caching."
```

Isolated by varying one thing at a time: the `anthropic-beta: prompt-caching-…` **header
alone is harmless**; it is the `cache_control` block in the **body** that is refused. An
earlier reading blamed the header and was wrong.

**FR-11 — Reconcile the IAM allow-list with the subscription state, and keep them
reconciled.** A catalogue entry whose model is not invocable is worse than an absent one:
it is discoverable, it passes policy, and it fails at the last hop with a message the
gateway sanitises to `{"error":"forbidden"}` — indistinguishable from a governance
denial without gateway log access.

**FR-12 — Onboarding must include a model-reachability check.** Registering a model in
the catalogue does not make it invocable. The check is a real inference call through the
gateway as the intended caller, not a listing API — a model reports as `ACTIVE` in
`list-inference-profiles` whether or not the account may call it.

---

## 6. Tooling requirements

D0 puts MCP out of scope for the first wave, which is right for delivery. These
requirements exist so the *second* wave is not designed around something that does not run.

**FR-13 — Governed tools come from the ACP MCP registry, not the workstation.** A tool
that reaches tenant data must be a registered MCP server reached through the gateway, so the
call is authorized and attributable. A **stdio** MCP server is a local process launched with
the user's ambient credentials — it acts as *them*, unmediated, and is a software-approval
decision rather than a configuration one.

**Measured**: the gateway serves each registered MCP server on its own path and the client
connects and enumerates tools through it; requests are `403 policy_denied` until the caller
holds an access policy for that server.

**FR-14 — Separate read from write by registering separate servers.** The unit of
enforcement is the **server**, not the tool. A policy scoped `read_only` still exposed every
tool on the server. The scope never reaches the gateway's authorization rego, and
`allowed_tool_ids` has no runtime consumer anywhere. Any requirement for tool-level
separation must be met by splitting servers, not by setting a scope.

**FR-15 — Do not make the first wave depend on a skills registry.** See §8 G-12.

---

## 7. Constraints (measured unless stated)
| # | Constraint | Consequence |
|---|---|---|
| C-1 | Gateway access tokens live 300 s | Refresh must be automated (NFR-1) |
| C-2 | The token's `aud` must name the gateway — **only when audience checking is switched on**. Measured 2026-09-16: `GATEWAY_JWT_AUDIENCE` is unset in dev, so the validator sets `verify_aud: False` and any audience is accepted | A client created without the audience mapping authenticates fine in dev and breaks the moment an environment sets that variable. Set the mapper regardless; do not read a working dev call as evidence the audience is right |
| C-3 | Client id + secret cannot be sent to the gateway in any form | Must be exchanged at the portal token endpoint first |
| C-4 | Trusted issuer is a **single** configured value (dev: Keycloak) | An Okta- or Entra-signed desktop token cannot be presented directly. **Addressed 2026-09-16 by brokering rather than exchange**: Entra is federated *into* the Keycloak realm, so the human authenticates at Microsoft and Keycloak mints the token. The issuer stays single and trusted, and the gateway needs no federation change |
| C-5 | The gateway's own connection limiter returns `503 "Too many connections"` under modest concurrency | Claude Code is far more concurrent than a shell loop; must be load-tested before rollout |
| C-6 | Errors are sanitised — `403` covers both policy denial and upstream refusal | Operators need gateway log access to triage; the response body is not diagnostic |
| C-7 | Credentials attach to a *deployment*, not a catalogue entry, and the secret is shown once | Provisioning runbook must account for this |
| C-8 | Service-principal bearer auth is disabled in all deployed environments (inference from configuration) | Do not design against it without a change request |

---

## 8. Capability gaps

| ID | Gap | Severity | Owner |
|---|---|---|---|
| **G-1** | Gateway rejects a valid bearer token when `x-api-key` is also present (FR-4) | High — blocks every client that sends both | Consortium |
| **G-2** | No IdP-driven user-group sync; no SCIM | High for an AD-group-based control | Consortium |
| **G-3** | No defined provisioning path for first-wave users into Luminate `User` rows. **Confirmed in source 2026-09-16**: there is no just-in-time user creation anywhere on the request path, so the row must pre-exist before a human can be authorized | High — blocks `user_email` on the ledger | ACP Product |
| **G-4** | IAM model allow-list and Bedrock subscription state drift (FR-11) | High — currently blocks all capable models | Cloud / ACP Platform |
| **G-5** | No device-authorization grant for CLI login | Medium — constrains §3.4 to two shapes | Consortium |
| **G-6** | Chargeback has no run/session dimension (FR-9) | Medium — only if per-session recovery is required | Consortium |
| **G-7** | Per-project provider account binding is deployed in dev but **not on upstream main** | Medium — Sun Life depends on an unmerged change | Consortium |
| **G-8** | Connection limiter untested at client concurrency (C-5) | Medium | ACP Platform |
| **G-9** | Only Claude Code is evidenced; the rest of the wave is unproven (FR-1) | Medium — scope risk against Oct 31 | ACP Product |
| **G-10** | No credential refresh for an MCP tool connection — the header is static and gateway tokens are short-lived. The client supports OAuth; the gateway does not advertise the metadata for it | Medium — blocks MCP as a deployment pattern | Consortium |
| **G-11** | No Sun Life standard for agent-plugin marketplaces, and the existing index is a demonstration (`sample-marketplace`) | Medium — a gap to raise, not a control to satisfy | EA / ACP Product |
| **G-12** | Luminate has **zero** skills implementation; the Skills Registry is a draft design (PR #106, still draft since 2026-07-14) whose runtime is the platform, **not a laptop** | Low for this wave — record as direction of travel | Consortium |
| **G-13** | Registry boundary with Nova unsettled — Nova already owns approved `agent` / `ai-skills` / `plugin` entity types and runs its own agent gateway | Medium — owned by `nova-acp-integration` (EACPP-895) | ACP Product |
| **G-14** | The **interim** posture is undesigned. D0 says the immediate path remains Bedrock direct, and that is what runs today — but it provides **none** of the per-user attribution in FR-5/FR-8, because the identity on the call is an AWS role | High — decides whether Oct 31 is met by a path that answers the cost question or one that does not | ACP Product |
| **G-15** | The **per-user** token path is unexercised. Every measured call used a Keycloak `client_credentials` service-account token — the shape DD-1 rejects. **Progress 2026-09-16**: the loopback-PKCE half of DD-3 is built — Entra federated into the `luminate` realm, an RFC 8252 public client (`luminate-desktop`) deployed. A real login was then attempted and **failed at Entra with `AADSTS50011`**: the broker redirect URI is *not* registered on the app. See G-18. No human identity has reached `ProjectUsageDaily` | High — FR-5/FR-8 and the whole attribution case rest on a chain traced through code, not demonstrated | ACP Product / Consortium |
| **G-16** | ~~Cost rollup fails silently.~~ **Resolved 2026-09-16.** Traces reached the store correctly attributed (`{entity_type}:{entity_id}`, real cost), but the portal usage/cost tables stayed empty because the rollup read an **unconfigured ClickHouse** — no-opping every minute while, by its own warning, reporting usage as **ageing rather than an outage**, so spend looked plausible and stale rather than absent. ClickHouse is now configured and the same job reports `observations=1 traces=1 rows=10`. The **rendered dashboard remains unverified** | Was High — kept on the register because the failure *mode* recurs (see G-17): a view that silently under-reports is worse than one that errors | ACP Platform |
| **G-17** | **A human token authenticates but does not attribute.** The gateway classifies any token carrying `email` / `oid` / `preferred_username` as `owner_type="user"` and admits it — but attribution keys off a *separate* `luminate_sub` claim carrying the portal `User.id`. Without it the gateway falls back to the IdP subject, which matches no portal user, logs that attribution and chargeback are **"degraded"**, and serves the request anyway. `luminate-desktop` currently emits only the audience mapper | High — G-16's silent-underreporting failure one layer up: a governed call that bills to nobody | Consortium / ACP Platform |
| **G-18** | **The Entra app registration does not carry the Keycloak broker redirect URI.** `OIDC-LuminatePortal-DEV` (`ea8bed79-…`) holds exactly one URI, the portal's Django callback, so a brokered login dies at `AADSTS50011` *after* the user has authenticated. **Raised 2026-09-16 as RITM2628871.** The boundary question — whether one registration should serve both the portal and Keycloak federation, or the broker should get its own — was **decided in favour of extending the existing portal registration**; revisit if the broker's lifecycle or secret rotation diverges from the portal's | High — hard-blocks every human login, and fails *first* of the three identity gaps. The only one outside ACP's control | Identity / EA |

---

## 9. Traceability

| Requirement | D0 driver | Verified by |
|---|---|---|
| FR-1, FR-2 | "Which products are in the initial validation set?" | Header-probe acceptance test |
| FR-3, FR-4, NFR-1 | "Centralize inference" | Measured header isolation, §2 |
| FR-5, FR-6, FR-7 | "How will users authenticate and be authorized?" | Source-verified principal derivation, §3 |
| FR-8, FR-9, NFR-2 | "What usage data is required to attribute token costs?" | Source-verified ledger chain, §4 |
| FR-10, FR-11, FR-12 | "Centralized inference is demonstrated" | Measured four-gate matrix, §5 |
| FR-13, FR-14, FR-15 | "No MCP integration in the first wave" — scoping the *next* one | Measured MCP lane probe, §6 |

## References

- [D0 — Discovery](d0-discovery.md)
- [D2 — Design](d2-design.md)
- **Sample implementation**: [`EDAEACP/acp-claude-code-harness`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-claude-code-harness/browse)
  — the client configuration, preflight checks and probes behind every *measured* claim here
- [ACP Capability Map](../../../capability-map.md)
- [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
- Related inference work: the `model-inference-patterns` spec (EACPP-1320), which records
  why centralizing inference makes ACP the attribution authority.
