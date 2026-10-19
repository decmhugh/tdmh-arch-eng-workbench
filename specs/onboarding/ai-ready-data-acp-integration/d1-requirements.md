# Onboard the AI-Ready Data Use Case to ACP — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD

## Capability Matrix — internal build vs Luminate target

| Capability | Internal build (EACPP-545, retired) | Luminate target (this spec) |
|---|---|---|
| Tool registration | AI-Ready Data tools in the internal MCP Registry | **MCP server registered in the Luminate catalog** |
| Governed egress | Internal `ai-gateway` clearance guard | **Luminate gateway** — authorize, trace, kill switch |
| Classification enforcement | `DataProduct` read model + clearance intersection in ACP | **Out of scope** — the Data Control Plane enforces at the data tier |
| Snowflake RBAC | `snowflake-adapter` clearance→role mapping | **Out of scope** — Sirius Snowfort owns grants |
| Lifecycle gate | AI-readiness gate in agent/model approval | **Out of scope** — belongs in `governance-intake` as an obligation if it returns |
| Lineage | Collibra publish + reconciliation job | **Out of scope** — future, per `governance-intake` D0 |
| Programmatic access | Internal SDK defaults | **`acp-harness-sdk`** with the Luminate target |
| Documentation | Spec only | **`luminate-user-guides`** + the ACP onboarding guide |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Register the **AI-Ready Data MCP server(s)** in the Luminate catalog with owner, project, scope tokens and the mandatory tag set. | Must |
| FR-2 | Publish the framework's **tools** through the catalog so consumers can discover them with their metadata (name, description, owner, scopes). | Must |
| FR-3 | Route AI-Ready Data **tool traffic through the Luminate gateway**, so every call is authorized, traced and subject to the kill switch. | Must |
| FR-4 | Provide a **repeatable end-to-end test** — register → discover → invoke → retrieve the audit record — runnable by the use-case team without ACP assistance. | Must |
| FR-5 | Record the **onboarding inputs** the use-case team must supply (server endpoint, owner, scopes, classification, environment) and the outputs they receive (catalog entry, gateway route, credentials). | Must |
| FR-6 | Where the use case calls models or tools programmatically, integrate via **`acp-harness-sdk`** against the Luminate target rather than a bespoke client. | Should |
| FR-7 | Contribute the onboarding path to **`luminate-user-guides`** so it is maintained with the platform, not in this spec. | Should |
| FR-8 | Support **staged registration** — a read-only tool batch first, mutating tools second — so the pilot is not blocked on approval of write-capable tooling. | Should |
| FR-9 | Confirm the **audit record shape** returned for a tool call is sufficient for the governance record consumed by `governance-intake`. | Could |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **ACP never re-classifies data.** Classification, contracts, masking and RLS stay with the Data Control Plane; ACP governs the agent's route, not the data. | Must |
| NFR-2 | **No new runtime service.** This is registration and configuration against a deployed Luminate, not a new component. | Must |
| NFR-3 | **No Sun Life fork of Luminate.** Anything the platform lacks is raised as a consortium ask, not patched locally. | Must |
| NFR-4 | **Gateway routing must not materially degrade tool latency** — measured against the direct call in dev before the team switches. | Should |
| NFR-5 | **Documentation lives with the platform** — `luminate-user-guides` and the onboarding guide, not ticket comments. | Should |

## Constraints & Assumptions

- A Luminate dev environment with a working catalog and gateway is available
  ([`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md), EACPP-596).
- The DCP team owns and supplies the MCP server and its metadata; ACP registers and routes it.
- The retired enforcement design (EACPP-545 T1–T9) is **not** revived as part of this work.
- The harness SDK is only required for callers that invoke programmatically; a pure MCP registration
  does not depend on [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md).

## Out of Scope

Restated from D0 because it is the main risk to this spec: runtime classification enforcement,
clearance→Snowflake RBAC mapping, the AI-readiness lifecycle gate, Collibra lineage and
reconciliation, and classification-compliance reporting are **all out of scope**. They were the
internal-build ambition. If any returns, it returns as a consortium capability.

## Open Questions

- [ ] Which tools are in the first registration batch (see D0)?
- [ ] Does the use case route model traffic as well as tool traffic?
- [ ] Who owns the catalog record — DCP or ACP?
- [ ] Do mutating tools need a human-in-the-loop gate at pilot stage?
