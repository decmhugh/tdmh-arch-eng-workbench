# AWS Harness Integration with Luminate — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **D2 Approved**: TBD
> **Repo**: `EDAEACP/acp-product-specs` · **Board**: Product Team (label `acp-product-team`)

## Overview

Update the AWS Harness SDK to speak Luminate's gateway, catalog, and token APIs, then update
the `acp-agentcore-sample` reference examples to the Luminate-supporting harness version.
Sequenced so the SDK support lands first; example migration follows once it ships.

## Tasks

| Task | Description | Depends |
|------|-------------|---------|
| **T1** | Add a **`LuminateAuthProvider`** (portal `POST /api/v1/iam/auth/token`, Authentik-backed client-credentials → Bearer JWT, refresh/caching) behind the existing auth interface. (DD-3) | — |
| **T2** | Add a **`target=luminate`** config to `ACPSettings` (portal base, catalog prefix, gateway `/llm` URL, token endpoint, `project`, `scope_tokens`, tags). (DD-5) | — |
| **T3** | Repoint **`GatewayClient`** to Luminate's `/llm/v1/chat/completions` with **Bearer JWT** (replace `x-acp-agent-id`). (DD-1) | T1, T2 |
| **T4** | Repoint **`RegistryClient`** to Luminate's **catalog viewsets** (`/api/v1/catalog/{agents,mcp-servers,models}`) with a payload mapper to Luminate schema (project, scope_tokens, mandatory tags, configuration). (DD-2) | T1, T2 |
| **T5** | On the Luminate path, **drop the cross-account assume-role** (gateway invokes Bedrock via its pod role). (DD-4) | T2 |
| **T6** | Add **Luminate contract tests** (httpx MockTransport): `/llm` + Bearer, catalog schema, token endpoint. (DD-7) | T3, T4 |
| **T7** | **Release** the Luminate-supporting harness version to Artifactory. | T3, T4, T5, T6 |
| **T8** | **Update the `acp-agentcore-sample` examples** (agent, ai-ready-data agent, MCP, A2A) to the new harness version: `target=luminate`, register via catalog, route model calls through `GatewayClient` (migrate any boto3 Converse/Nova direct calls). (DD-6) | T7 |
| **T9** | Update `acp-agentcore-sample` README/quickstart + register/deploy/invoke scripts for the Luminate flow (project/scope/tags, portal token). | T8 |

## Definition of Done

- Harness supports the Luminate target (gateway `/llm` + Bearer, catalog viewsets, portal token) with contract tests, released to Artifactory.
- `acp-agentcore-sample` examples run end-to-end against Luminate on the new harness version, governed through the gateway.

## References

- Spec: [D0](d0-discovery.md) · [D1](d1-requirements.md) · [D2](d2-design.md)
- Examples: `Control Plane/acp-agentcore-sample` · SDK: `Control Plane/acp-harness-sdk`
- Cross-ref: `sunlife-deployment` DD-5/DD-6 (gateway-side role/cost).
