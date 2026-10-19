# Small Local Model (SLM) Pipeline — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: EACPP-557

## Problem Statement

ACP needs to run **self-hosted open-weight Small Local Models (SLMs)** inside Sun Life's
network — for data residency, supply-chain control, cost, and latency — but today there is
**no governed path to get model weights from Hugging Face into EKS**:

- `huggingface.co` is **blocked by Netskope** (category "Generative AI" → SLF Block), so model
  weights cannot be pulled at all from the corporate estate.
- Ad-hoc downloads (developer laptops, public mirrors) are uncontrolled, unscreened, and
  unauditable — there is no single vetted source of truth for model artifacts.
- There is **no per-model gate**: nothing forces a license / provenance / safety review before a
  model can be served, and nothing ties that approval to the ACP Model Registry.
- Even where models *are* served (demo Ollama), the set of servable models is not constrained by
  any approval state — an operator can pull and serve an arbitrary model.

The deck **"Hugging Face Model Mirror in Artifactory" (ISRA, June 2026)** proposes the target:
a curated, governed mirror of Hugging Face inside **JFrog Artifactory** as the single pull-through
chokepoint, with per-model **GenAI Risk Triage**, registration into the **ACP Model Registry**, and
serving in EKS brokered by the **AI Gateway**. This spec is the ACP-side delivery plan for that
proposal, phased into an interim dev POC and a generalized pipeline.

## Opportunity

ACP becomes the **governed runtime for self-hosted SLMs**: Artifactory is the only way weights
reach the cluster, the Model Registry is the **authority for which models may be pulled and served**,
and the AI Gateway brokers every inference with policy, guardrails, and full observability.

- **Single vetted supply chain** — one approved pull-through source replaces ad-hoc downloads;
  Sonatype Repository Firewall screens every component at ingestion; checksums and provenance are retained.
- **Registry-gated allowlist** — *only models registered and approved in the ACP Model Registry can
  be mirrored, pulled, and served.* The Model Registry's approved set is the single source of truth
  that constrains Artifactory and EKS — there is no path to serve an un-approved model.
- **Data residency & sovereignty** — prompts and inference data never leave the VPC; EKS has **no
  direct internet path to Hugging Face** (egress is scoped to Artifactory servers only).
- **Governance by design** — per-model GenAI Risk Triage + Legal review + registry approval state +
  gateway policy enforcement, with approval artifacts captured (Archer ID, interim).
- **Cost & latency** — small local models avoid per-token vendor fees and reduce round-trip latency.

This is additive to existing ACP components (model-registry, ai-gateway, deployment-infrastructure,
observability-monitoring, governance-integration). It introduces no new runtime service — it wires
Artifactory, the Model Registry, and EKS serving into one governed flow.

## Phasing

| Phase | Scope | Governance vehicle | Models |
|-------|-------|--------------------|--------|
| **Phase 0 — Interim POC** (this deck, slide 3) | Netskope unblock scoped to Artifactory **dev** only; single restricted HF/ML pull-through repo; serve in `acp-data` dev | **In-flight ISRA** (the deck) | **Gemma 3n E2B**, **Gemma 3n E4B** only |
| **Phase 1 — Generalized pipeline** (deck slide 4) | Self-service per-model onboarding; registry-gated allowlist; promotion to SIT/prod | **Separate ISRA + ATG submission** (follow-up) | Phase 0 models **plus** Qwen 3.6 27B, Gemma 4 12B, Qwen 2.5 Coder 14B, Gemma 2 9B |

> Canonical Hugging Face repo IDs, revisions, and digests for each model are pinned at GenAI Risk
> Triage time and recorded on the Model Registry entry; model-family names above match the program deck.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| InfoSec / Risk | ISRA approver | Netskope unblock scoped to Artifactory only; per-model triage as the publish gate |
| DevOps / Platform | Implementers | Artifactory HF/ML repo config; EKS serving; licensing; no broad egress |
| Legal | Per-model reviewer | Open-weight license terms, acceptable use, provenance |
| ACP Model Registry owners | Authority | Registry approval state is the allowlist; model cards + approval artifacts captured |
| Agent / Application teams | Consumers | OpenAI-compatible inference via the Gateway; clear catalog of approved models |
| GbD / GenAI Risk Triage | Per-model gate | License, provenance, safety, data-flow review before publish |
| Enterprise Architecture (ATG) | Generalized-pipeline approver | Architecture sign-off for the broad self-service pipeline (Phase 1) |
| JFrog / Artifactory admins | Platform | ML repo layout (v7.104.15) licensing; pull-through + Sonatype firewall configuration |

## Scope

### In Scope

1. **Netskope unblock (Artifactory-scoped)** — allow `huggingface.co` egress from the Artifactory
   servers only, not the broad estate; primary ISRA ask (Phase 0).
2. **Artifactory HF/ML pull-through repo** — configure the remote (vetting) repository on
   v7.104.15, with Sonatype Repository Firewall screening and an include-pattern allowlist (Phase 0: Gemma 3n only).
3. **Registry-gated model allowlist** — the ACP Model Registry's approved entries are the single
   source of truth constraining what may be mirrored, pulled, and served.
4. **Per-model approval flow** — GenAI Risk Triage + Legal review → Model Registry registration with
   model card + approval artifacts (Archer ID interim).
5. **EKS self-hosted serving** — model-serving workloads (Ollama/vLLM/TGI) in the `acp-data`
   namespace pulling weights from Artifactory, fronted by the AI Gateway (OpenAI-compatible).
6. **Observability** — Langfuse traces, Prometheus metrics, and audit for SLM inference.
7. **Generalized pipeline (Phase 1)** — self-service per-model onboarding workflow + the **separate
   ISRA + ATG submission package** + onboarding of the expanded shortlist.
8. **Supply-chain hardening** — safetensors-preferred, checksum/provenance retention, no arbitrary
   pickle execution, isolated serving pods.

### Out of Scope

- **Broad internet access to `huggingface.co`** — egress stays scoped to Artifactory servers only.
- **Training / fine-tuning on customer data** — serving inference only.
- **Un-triaged or arbitrary model pulls** — nothing reaches EKS that is not mirrored and approved.
- **Authoring the GenAI Risk Triage or Legal process itself** — ACP consumes their sign-off; the
  processes are owned by GbD / Legal.
- **Building a new runtime service** — this wires existing Artifactory, Model Registry, AI Gateway,
  and EKS together.
- **Hosted/vendor model routing** (Bedrock, OpenAI, etc.) — covered by ai-gateway / inference-economics.

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Scoped egress | Netskope allows `huggingface.co` from Artifactory hosts only | EKS has zero direct HF egress (verified) |
| Single vetted source | All model weights in EKS originate from the Artifactory mirror | 100% — no other pull path |
| Registry-gated allowlist | Models pullable/servable ⊆ Model Registry approved set | 0 un-approved models servable |
| Per-model gate | Triage + Legal + registry approval before publish | 100% of served models have approval artifacts |
| POC serving | Gemma 3n E2B + E4B served via Gateway in dev | OpenAI-compatible inference succeeds end-to-end |
| Supply-chain scanning | Sonatype firewall screening on every mirrored component | 100% screened; criticals block publish |
| Observability | Every SLM inference traced + metered + audited | Langfuse + Prometheus coverage 100% |
| Generalized pipeline | Separate ISRA + ATG package submitted | Submission accepted for review |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
| ISRA approval (Phase 0) | InfoSec / Risk | Hard | High — gates the Netskope unblock; nothing proceeds without it |
| Netskope unblock (Artifactory-scoped) | Network / InfoSec | Hard | High — no weights without it |
| Artifactory HF/ML repo licensing | JFrog / Platform | Hard | Med — v7.104.15 ML repo layout must be license-covered |
| ACP Model Registry approval/allowlist API | model-registry (EACPP-225) | Hard | Med — registry is the allowlist authority |
| AI Gateway model routing | ai-gateway (EACPP-211) | Hard | Med — OpenAI-compatible brokering of SLM endpoints |
| EKS `acp-data` serving + Helm | deployment-infrastructure (EACPP-212) | Hard | Med — serving pods + image/weight pull |
| Observability stack | observability-monitoring (EACPP-223) | Soft | Low — Langfuse + Prometheus already deployed |
| GenAI Risk Triage + Legal sign-off | GbD / Legal | Hard | Med — per-model gate before publish |
| ATG submission (Phase 1) | Enterprise Architecture | Hard | Med — generalized pipeline approval |
| Archer (approval artifacts, interim) | GRC | Soft | Low — interim ID capture on registry entry |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Broad internet exposure via unblock | Med | High | Scope Netskope unblock to Artifactory servers only; EKS never talks to HF directly (verified) |
| Malicious / unvetted model published | Med | High | Mandatory per-model GenAI Risk Triage + Sonatype firewall screening before registry publish; registry-gated allowlist |
| Unsafe model weights / embedded code | Med | High | Prefer safetensors; no arbitrary pickle execution; isolated serving pods; provenance retained |
| Artifactory ML repo licensing gap | Med | Med | Confirm v7.104.15 ML repo layout licensing before repo config (spike) |
| Data leakage at inference | Low | High | Self-hosted in VPC; gateway guardrails, logging, DLP policy; no egress |
| Allowlist drift (Artifactory vs Registry) | Med | Med | Registry is single source of truth; controller reconciles Artifactory include-patterns + EKS pull policy; deny on unknown |
| Serving resource pressure on dev EKS | Med | Med | Right-size pods; `Recreate` strategy for single-replica model pods on CPU-tight nodes |
| Scope creep into broad HF access | Med | Med | D0 boundary: Artifactory-only egress, approved models only, no fine-tuning |

## Open Questions

- [ ] Can the Phase 0 POC ride the in-flight ISRA, and is a **separate ISRA + ATG** confirmed required for the generalized pipeline (Phase 1)?
- [ ] Does the current JFrog license cover the v7.104.15 **ML repo layout** (HF layout), or must licensing be extended?
- [ ] Is **per-model GenAI Risk Triage** accepted by InfoSec as the publish gate, or is a heavier assessment required per model?
- [ ] What is the exact mechanism to project the Model Registry allowlist into Artifactory — include-patterns, a "approved" property + Sonatype firewall policy, or an EKS admission check (or all three)?
- [ ] Which serving runtime is canonical for the POC — Ollama (simplest), vLLM, or TGI — and what are the node/GPU constraints in `acp-data` dev?
- [ ] Is **Archer ID** the interim home for approval artifacts, and what is the target system once GRC integration matures?
- [ ] What pinning policy applies — pin by HF revision tag, by commit SHA, or by content digest — for reproducible, immutable mirrors?
- [ ] Egress verification: how do we prove (and continuously monitor) that EKS has no direct path to `huggingface.co`?

## References

- **Program deck**: `ACP-HuggingFace-Mirror-ISRA.pptx` (ISRA, June 2026) — slides 3 (POC) & 4 (future pipeline)
- **Jira Epic**: EACPP-557 (Small Local Model (SLM) Pipeline)
- **Baking models / daemonless image builds**: workspace memory `baking-models-into-images.md` (crane, Netskope, Ollama model bake, EKS gotchas)
- **Related specs**: [Model Registry](../../model-registry/d0-discovery.md) · [AI Gateway](../../ai-gateway/d0-discovery.md) · [Deployment & Infrastructure](../../deployment-infrastructure/d0-discovery.md) · [Observability & Monitoring](../../observability-monitoring/d0-discovery.md) · [Governance Integration](../../governance-integration/d0-discovery.md)
