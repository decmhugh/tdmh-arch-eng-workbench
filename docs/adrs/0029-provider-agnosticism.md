---
parent: Decisions
nav_order: 29
title: ADR-0029 LLM and Cloud Provider Agnosticism
status: draft
date: 2025-07-14
decision-makers: [TBD]
---

# ADR-0029: LLM and Cloud Provider Agnosticism

## Status

**Draft**

## Context and Problem Statement

ACP governs AI agents that may use any LLM provider (Amazon Bedrock, Azure OpenAI, Snowflake Cortex, Google Vertex AI, self-hosted models, etc.) and may run on different cloud or on-premise platforms. If ACP's architecture is tightly coupled to a specific provider, it limits adoption, creates vendor lock-in for consuming teams, and reduces the platform's value as a universal governance layer.

The question: should ACP be designed as a provider-agnostic control plane, or should it optimize for a primary provider (e.g., AWS Bedrock) with secondary provider support?

## Decision Drivers

* ACP's core value proposition is universal AI agent governance — not tied to a specific LLM provider
* Consuming teams within the enterprise use multiple LLM providers today (Bedrock, Azure OpenAI, Snowflake Cortex)
* Future providers and models are unpredictable — the platform must accommodate them without core changes
* Adapter pattern already exists in the codebase (acp-adapter-aws, acp-adapter-k8s, acp-adapter-snowflake)
* Observability and cost tracking must normalize data across providers into a common schema
* Multi-region deployments may use different cloud providers per region

## Considered Options

1. **Provider-agnostic with adapter pattern** — All provider-specific logic isolated behind adapter interfaces
2. **Primary provider with extensions** — Optimize for Bedrock, bolt on other providers
3. **Fully abstracted** — No provider-specific code at all, everything generic

## Decision Outcome

**Chosen option: Provider-agnostic with adapter pattern**

All provider-specific functionality is isolated behind well-defined adapter interfaces. ACP's core (governance policies, agent registry, model registry, observability, cost tracking) operates on provider-neutral abstractions.

### Principles

1. **Core is provider-neutral** — ACP core, management plane, and governance engine must not import or reference any specific LLM provider SDK
2. **Adapters encapsulate providers** — Each LLM/cloud provider gets a dedicated adapter that implements the common interface (e.g., `acp-adapter-aws`, `acp-adapter-snowflake`)
3. **Common telemetry schema** — Observability, cost tracking, and usage reporting use a provider-agnostic data model. Adapters normalize provider-specific metrics into this common schema
4. **Policies are provider-agnostic** — Governance policies (CEL rules, OPA policies) reference abstract resource types, not provider-specific identifiers
5. **New providers = new adapter** — Adding support for a new LLM provider requires only a new adapter module, not changes to ACP core

### Applies To

| Component | Implication |
| - | - |
| acp-core | Domain models and interfaces must be provider-neutral |
| acp-management-plane | Policy evaluation uses abstract resource types |
| acp-agent-registry | Agent records reference model capabilities, not provider-specific model IDs |
| acp-model-registry | Model cards include provider metadata but core schema is provider-neutral |
| acp-gateway / acp-agentgateway | Routes and governs requests regardless of downstream LLM provider |
| acp-adapter-* | Each adapter encapsulates provider-specific SDK calls, IAM, and telemetry normalization |
| Observability (EACPP-223) | Telemetry ingestion accepts usage data from any provider; cost normalization in adapters |
| Cost tracking | Common token/cost schema; adapters translate provider-specific billing |

### Consequences

* Good, because ACP can govern agents using any LLM provider without core changes
* Good, because consuming teams are not forced onto a specific provider
* Good, because new providers can be onboarded by adding an adapter module
* Good, because observability and cost data are comparable across providers
* Bad, because the adapter abstraction adds a layer of indirection
* Bad, because provider-specific optimizations may be harder to implement behind generic interfaces
* Bad, because each new provider requires adapter development and testing effort

### Confirmation

* No provider-specific imports in `acp-core`, `acp-management-plane`, or `acp-gateway` (enforced via linting)
* All provider-specific code lives in `acp-adapter-*` repos
* Integration tests verify governance flows work with at least two different provider adapters
* Observability telemetry schema validation confirms provider-neutral structure

## References

* Existing adapters: `acp-adapter-aws`, `acp-adapter-k8s`, `acp-adapter-snowflake`
* Related: [ADR-0025 Polyrepo Architecture](0025-polyrepo-architecture.md) (adapters as separate repos)
* Related: EACPP-223 Observability spec (provider-agnostic telemetry ingestion)
