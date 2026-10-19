# Onboard the AI-Ready Data Use Case to ACP — D0 Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Supersedes**: `T1KACP/acp-specs/specs/ai-ready-data` (EACPP-545), written against the internal
> MVP build. That spec is retired — see [Scope change](#scope-change-from-the-internal-build).

## Scope change from the internal build

The original `ai-ready-data` spec proposed that ACP become the **runtime enforcement layer** for the
Data Control Plane's AI-Ready Data Framework: a `DataProduct` read model in `acp-core`, clearance
intersection enforced in the internal `ai-gateway`, clearance→Snowflake RBAC mapping in
`snowflake-adapter`, an AI-readiness lifecycle gate, Collibra lineage publishing and
classification-compliance reporting — ten tasks across three sprints, all against components of the
internal build.

**That is no longer the scope.** Two things changed:

1. **The runtime is Luminate**, not the internal MVP. `ai-gateway`, `management-plane`,
   `governance-integration` and `snowflake-adapter` are internal-build components; the go-forward
   platform is the consortium build described in
   [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md).
2. **ACP's role narrowed.** ACP is **assisting the AI-Ready Data use case with MCP server
   registration and testing** — not owning data classification enforcement. Classification,
   contracts, masking and RBAC remain with the Data Control Plane (DPEP / Sirius), which already
   enforces them at the data tier.

What survives is the useful half: getting the AI-Ready Data tooling registered as **governed MCP
servers** on Luminate, routed through the gateway, and tested. The enforcement ambition is recorded
here as out of scope so it is not silently lost — if it returns, it returns as a consortium
capability, not a Sun Life fork.

## Problem Statement

- **The AI-Ready Data tooling is not registered anywhere governed.** The framework's tools
  (classify, contract author/lint/test, provision, tag, register) are exposed as MCP tools today
  but are not in the Luminate catalog, so their use is neither discoverable, scoped nor audited.
- **No governed egress path.** Agents calling AI-Ready Data tooling do so directly; there is no
  gateway in the path, so no audit ledger entry, no policy check and no kill switch.
- **No test path.** There is no repeatable way for the use-case team to prove their MCP server
  works end to end against Luminate — registration, discovery, invocation, audit.
- **Onboarding requirements are undocumented for this use case.** What the team must provide
  (server metadata, owner, classification, scopes) and what they get back has not been written
  down, so each conversation restarts.
- **Two planes, no seam.** The Data Control Plane governs the *data*; ACP governs the *agent*. The
  seam between them — an agent reaching certified data through a governed tool — is exactly the MCP
  registration this spec covers, and it is currently missing.

## Opportunity

- **The AI-Ready Data toolset becomes a first-class governed capability** — registered in the
  Luminate catalog, scoped, audited and discoverable, with no new runtime service.
- **A worked example of the two-plane model** — the DCP certifies the data, ACP governs the agent's
  route to it. This use case is the cleanest demonstration of that seam.
- **A reusable MCP onboarding path** — the registration + testing loop proven here is the same one
  `aims`, `orcc` and `waldo` need; documenting it once serves all of them.
- **Low cost, near-term** — registration and testing against an already-deployed Luminate dev
  environment, with no dependency on the retired enforcement design.

## Stakeholders

| Stakeholder | Role | Interests |
|---|---|---|
| **Data Control Plane (DPEP / Sirius) Engineering** | Use-case owner | Their MCP server registered and testable without forking their tooling or vocabulary |
| **Data Product Stewards** | Data owners | Agent access to certified products is visible and audited |
| **ACP Product (Seth)** | Platform | Registration path, gateway routing, test harness, documentation |
| **AI4Ops / consumer agent teams** | Consumers | Discover and call AI-Ready Data tools through one governed URL |
| **Governance-by-Design** | Governance | Tool usage is auditable; ties into the governance record |
| **Enterprise Architecture** | Reviewers | Integration pattern conformance |

## Scope (MVP)

**In Scope:**

- **MCP server registration** — register the AI-Ready Data MCP server(s) in the Luminate catalog
  with owner, project, scopes and mandatory tags.
- **Tool catalog** — the framework's tools discoverable through the catalog with their metadata.
- **Governed routing** — tool traffic routed through the Luminate gateway so calls are authorized,
  traced and killable.
- **Test path** — a repeatable end-to-end test: register → discover → invoke → confirm the audit
  trail, runnable by the use-case team.
- **Onboarding documentation** — what the team provides and what they get back, contributed to
  [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse)
  rather than written once in a ticket.
- **Harness SDK usage** — where the use case calls models or tools programmatically, via
  [`acp-harness-sdk`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-harness-sdk/browse).

**Out of Scope (Backlog):**

- **Runtime classification enforcement in ACP** — clearance intersection, field-level
  allow/redact/deny, the `DataProduct` read model. Retired with the internal build; the DCP enforces
  at the data tier.
- **Clearance → Snowflake RBAC mapping** — Sirius Snowfort owns grants.
- **AI-readiness lifecycle gate** — if it returns, it belongs in
  [`governance-intake`](../../governance/governance-intake/d0-discovery.md) as a per-band obligation, not here.
- **Collibra lineage publishing and classification reconciliation** — explicitly future in
  `governance-intake` D0.
- **Classification-compliance and masking-effectiveness reporting.**
- **Authoring or running the framework workflow** — owned by the DCP and the `ai-ready-data` skill.
- **Defining the Sun Life classification taxonomy** — consumed as-is, never re-authored.

## Success Criteria

- ✅ **AI-Ready Data MCP server registered** in the Luminate catalog and visible to the use-case team.
- ✅ **Tools discoverable** through the catalog with owner, scopes and tags populated.
- ✅ **Traffic routed through the gateway** — no direct, unaudited tool calls from onboarded agents.
- ✅ **Audit trail confirmed** — an invocation is retrievable end to end after the fact.
- ✅ **Test path repeatable by the use-case team** without ACP hand-holding.
- ✅ **Onboarding documented** in `luminate-user-guides`, not in a ticket comment.

## Dependencies

| Dependency | Owner | Type | Risk |
|---|---|---|---|
| Luminate dev environment with catalog + gateway available | [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md) (EACPP-596) | Hard | Med — registration needs a live catalog |
| MCP server metadata (owner, scopes, classification, endpoint) | DCP / DPEP team | Hard | Med — cannot register without it |
| MCP registration path on Luminate | Consortium `mcp-registry` (EACPP-651) | Hard | Med |
| Harness SDK Luminate target, if the use case calls programmatically | [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md) (EACPP-707) | Soft | Low — only for SDK-based callers |
| Luminate user guides as the documentation home | `EDAEACP/luminate-user-guides` | Soft | Low |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scope creeps back toward the retired enforcement design | Med | High | The out-of-scope list above is explicit; enforcement returns as a consortium capability or not at all |
| MCP server metadata incomplete | Med | Med | Register one server first; treat the metadata template as a deliverable |
| Gateway routing changes the use case's call pattern | Med | Med | Test in dev against the real gateway before asking the team to switch |
| Two planes disagree on who denies a request | Low-Med | Med | ACP governs the agent's route; the DCP governs the data. ACP does not re-classify — restated in D1 as a constraint |
| Documentation lands in a ticket and rots | Med | Low | Documentation contributed to `luminate-user-guides` is a success criterion, not a nicety |

## Open Questions

- [ ] Which AI-Ready Data tools are in the first registration batch — the full set, or read-only
      (classify, lint, test) first with mutating tools (provision, tag, register) second?
- [ ] Does the use case call models through the gateway as well, or only tools? That decides whether
      the harness SDK is in scope for the pilot.
- [ ] Who owns the MCP server record in the Luminate catalog — the DCP team or ACP?
- [ ] Are the framework's mutating tools subject to a human-in-the-loop gate at this stage?
- [ ] Which environments does the use case need — dev only for the pilot, or dev + test?

## References

- Retired predecessor: `T1KACP/acp-specs/specs/ai-ready-data` (EACPP-545) — internal-build scope
- Luminate user guides: [`EDAEACP/luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse)
- Harness SDK: [repo](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-harness-sdk/browse) ·
  [user guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-harness-sdk/bb-pages/browse/user-guide/)
- Onboarding guide: [ACP Onboarding Guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-onboarding-guide/bb-pages/browse/)
- AI-Ready Data skill: `agent-skills-python/.github/skills/ai-ready-data/SKILL.md`
- Classification taxonomy: `agent-skills-python/.github/instructions/data-classification.instructions.md`
- Related specs: [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md) ·
  [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md) ·
  [`governance-intake`](../../governance/governance-intake/d0-discovery.md)
