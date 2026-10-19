# Small Local Model (SLM) Pipeline — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: EACPP-557

## Scope & Responsibility Boundary

This spec defines a **governed supply-and-serve pipeline** for self-hosted open-weight SLMs. ACP
**owns** the chokepoint wiring (Artifactory mirror config, registry-gated allowlist, EKS serving,
gateway brokering, observability) and **consumes** the per-model approvals produced by GenAI Risk
Triage and Legal. ACP never authors those approval processes and never opens broad internet access.

Work spans existing components; this spec is the cross-cutting contract:

| Capability | Owning component / team | This spec adds |
|-----------|-------------------------|----------------|
| Netskope unblock (Artifactory-scoped) | Network / InfoSec (via ISRA) | The request + verification that EKS has no HF egress |
| HF/ML pull-through mirror + Sonatype firewall | deployment-infrastructure / JFrog | Repo config, include-pattern allowlist, firewall gate |
| Registry-gated allowlist | model-registry | Approved set = source of truth for pullable/servable models |
| Per-model approval capture | model-registry / governance-integration | Model card + triage/Legal artifacts (Archer ID interim) |
| EKS serving (`acp-data`) | deployment-infrastructure | Serving pods (Ollama/vLLM/TGI) pulling from Artifactory |
| OpenAI-compatible brokering | ai-gateway | Route SLM endpoints with policy/guardrails |
| Observability | observability-monitoring | Langfuse traces + Prometheus metrics + audit |
| Generalized pipeline governance | EA (ATG) / InfoSec (ISRA) | Phase 1 ISRA + ATG submission package |

## User Stories

### US-1: Scope Netskope egress to Artifactory only (Phase 0)

**As an** InfoSec risk approver,
**I want** the `huggingface.co` unblock limited to the Artifactory servers,
**So that** the broad estate and EKS keep no direct path to Hugging Face.

**Acceptance Criteria**:
- [ ] **Given** the ISRA is approved, **When** the Netskope rule is applied, **Then** only Artifactory source IPs/egress can reach `huggingface.co`.
- [ ] **Given** an EKS pod in `acp-data`, **When** it attempts to reach `huggingface.co` directly, **Then** the request is blocked.
- [ ] **Given** the unblock is live, **When** egress is reviewed, **Then** a verification record shows Artifactory-only scope and EKS containment.

### US-2: Mirror approved models through Artifactory (Phase 0)

**As a** platform engineer,
**I want** a HF/ML pull-through repository in Artifactory (dev) restricted to approved model paths and scanned by Sonatype firewall,
**So that** weights enter the network through one vetted, scanned chokepoint.

**Acceptance Criteria**:
- [ ] **Given** Artifactory v7.104.15, **When** the HF/ML remote repo is configured, **Then** it pull-through caches only the allowlisted HF repo IDs (Phase 0: Gemma 3n E2B/E4B).
- [ ] **Given** a model artifact is cached, **When** the Sonatype firewall screens it, **Then** critical findings block publish to the Registry.
- [ ] **Given** a non-allowlisted HF repo ID, **When** a pull is attempted, **Then** Artifactory does not cache or serve it.
- [ ] **Given** a cached artifact, **When** stored, **Then** checksum and provenance metadata are retained.

### US-3: Registry-gated model allowlist

**As a** Model Registry owner,
**I want** the set of pullable/servable models to be exactly the set approved in the ACP Model Registry,
**So that** no model can be mirrored, pulled, or served without registry approval.

**Acceptance Criteria**:
- [ ] **Given** a model is **approved** in the Registry with a pinned HF repo ID/revision/digest, **When** the allowlist reconciles, **Then** Artifactory include-patterns and the EKS pull policy permit exactly that artifact.
- [ ] **Given** a model is **not approved** (or revoked), **When** a pull or serve is attempted, **Then** it is denied (fail-closed) and the attempt is audited.
- [ ] **Given** the Registry approved set changes, **When** reconciliation runs, **Then** Artifactory and EKS policies converge to the new set within the freshness target.
- [ ] **Given** drift between Artifactory and the Registry, **When** detected, **Then** a governance finding is raised and the Registry wins.

### US-4: Capture per-model approval (triage + Legal)

**As a** governance approver,
**I want** each model's GenAI Risk Triage and Legal review recorded as the registry approval state with artifacts,
**So that** no model is servable without sign-off and the evidence is auditable.

**Acceptance Criteria**:
- [ ] **Given** a model request, **When** GenAI Risk Triage and Legal review complete, **Then** the Registry entry records reviewer, decision, date, and an Archer ID (interim).
- [ ] **Given** a model lacks triage or Legal sign-off, **When** approval is attempted, **Then** it is blocked.
- [ ] **Given** an approved model, **When** viewed, **Then** the model card shows license, provenance, source HF repo ID/digest, and approval artifacts.

### US-5: Self-host SLM serving in EKS (Phase 0)

**As an** application team,
**I want** approved SLMs served from `acp-data` pulling weights from Artifactory and fronted by the AI Gateway,
**So that** I can call them OpenAI-compatibly without data leaving the VPC.

**Acceptance Criteria**:
- [ ] **Given** an approved model, **When** the serving pod starts, **Then** it pulls image + weights from Artifactory (not the internet).
- [ ] **Given** a deployed SLM, **When** a client calls it via the Gateway, **Then** an OpenAI-compatible response is returned with policy/guardrails applied.
- [ ] **Given** a single-replica model pod on CPU-tight nodes, **When** it is updated, **Then** the `Recreate` strategy avoids a second Pending pod.
- [ ] **Given** Gemma 3n E2B and E4B, **When** the POC runs, **Then** both serve end-to-end in dev.

### US-6: Observability for SLM inference

**As an** operator,
**I want** every SLM inference traced, metered, and audited,
**So that** usage, cost, latency, and policy decisions are visible.

**Acceptance Criteria**:
- [ ] **Given** an SLM inference, **When** it completes, **Then** a Langfuse trace and Prometheus metrics (tokens, latency, errors) are emitted.
- [ ] **Given** a gateway policy/guardrail decision, **When** it occurs, **Then** it is audited with model id and outcome.
- [ ] **Given** a Grafana view, **When** opened, **Then** SLM inference metrics are visible per model.

### US-7: Generalized self-service onboarding pipeline (Phase 1)

**As a** model requester,
**I want** a repeatable workflow Request → GenAI Risk Triage → Legal → Mirror → Registry Approval → Serve,
**So that** new approved SLMs can be onboarded without bespoke wiring.

**Acceptance Criteria**:
- [ ] **Given** a new model request, **When** it passes triage + Legal + registry approval, **Then** mirror + serve are enabled automatically by the registry-gated allowlist.
- [ ] **Given** any stage fails, **When** the workflow halts, **Then** the model is not mirrored or served and the reason is recorded.
- [ ] **Given** the expanded shortlist (Qwen 3.6 27B, Gemma 4 12B, Qwen 2.5 Coder 14B, Gemma 2 9B), **When** onboarded, **Then** each follows the same workflow.

### US-8: Generalized-pipeline ISRA + ATG submission (Phase 1)

**As a** program lead,
**I want** a separate ISRA and ATG submission for the generalized pipeline,
**So that** the broad self-service pipeline and expanded models are formally risk-assessed and architecture-approved.

**Acceptance Criteria**:
- [ ] **Given** Phase 0 controls are proven, **When** the Phase 1 package is prepared, **Then** it documents the generalized pipeline, the registry-gated allowlist, and the expanded model shortlist.
- [ ] **Given** the package, **When** submitted, **Then** ISRA (InfoSec) and ATG (EA) reviews are requested and tracked.

## Functional Requirements

### FR-1: Artifactory HF/ML pull-through mirror

A remote (pull-through) HF/ML repository on Artifactory v7.104.15 with an **include-pattern
allowlist** and Sonatype Repository Firewall screening. Pull-through is restricted to allowlisted HF repo IDs; Sonatype firewall
criticals block registry publish; checksum + provenance retained.

### FR-2: Registry-gated allowlist projection

A reconciliation controller reads the Model Registry **approved** set (each with HF repo ID +
pinned revision/digest) and projects it into (a) Artifactory include-patterns / "approved" property
and (b) the EKS pull/admission policy. The Registry is the single source of truth; unknown ⇒ deny.

```
allowed_artifacts = { (m.hf_repo_id, m.pinned_digest)
                      for m in model_registry if m.status == "approved" }
artifactory.include_patterns ← allowed_artifacts
eks.pull_policy.allow        ← allowed_artifacts
# anything not in allowed_artifacts is fail-closed denied
```

### FR-3: Per-model approval + artifacts

The Model Registry entry carries approval state (`triaged`, `legal_reviewed`, `approved`/`revoked`),
reviewer, date, Archer ID (interim), license, provenance, source HF repo ID/digest, and a model
card. No serving without `approved`.

### FR-4: EKS serving

Serving workloads (Ollama/vLLM/TGI) run in `acp-data`, pull image + weights from Artifactory, expose
OpenAI-compatible endpoints, and register with the AI Gateway. Single-replica model pods use the
`Recreate` strategy on CPU-tight nodes.

### FR-5: Gateway brokering

The AI Gateway routes to SLM endpoints with policy, guardrails, and rate limits; consumers call
OpenAI-compatible APIs through the Gateway only (no direct pod access).

### FR-6: Observability

Langfuse traces and Prometheus metrics for every SLM inference; gateway decisions audited; Grafana
dashboards per model.

### FR-7: Netskope egress scope + verification

`huggingface.co` egress allowed from Artifactory hosts only; an explicit verification confirms EKS
has no direct path and continuously monitors it.

### FR-8: Generalized onboarding workflow + governance submission

A documented self-service workflow (Request → Triage → Legal → Mirror → Registry Approval → Serve)
and a Phase 1 ISRA + ATG submission package.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Security | EKS has no direct egress to `huggingface.co` | 0 direct connections (verified + monitored) |
| NFR-2 | Security | Every mirrored artifact scanned by Sonatype firewall | 100%; criticals block publish |
| NFR-3 | Governance | Servable models ⊆ Registry approved set | 0 un-approved servable models (fail-closed) |
| NFR-4 | Freshness | Allowlist reconciliation after Registry change | < 15 min to converge Artifactory + EKS |
| NFR-5 | Integrity | Model artifacts pinned + immutable | Pin by revision/digest; checksum verified on pull |
| NFR-6 | Safety | Weight format | Prefer safetensors; no arbitrary pickle execution |
| NFR-7 | Observability | SLM inferences traced + metered | 100% Langfuse + Prometheus coverage |
| NFR-8 | Availability | Serving survives single-pod restart on tight nodes | `Recreate` strategy; no stuck Pending |
| NFR-9 | Auditability | Pull/serve denials + approvals audited | 100% of decisions recorded |

## Data Model Requirements

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| ApprovedModel (Registry) | model_id (PK), hf_repo_id, pinned_revision, pinned_digest, status, license, provenance, archer_id, model_card_url | drives Allowlist |
| AllowlistEntry | hf_repo_id, pinned_digest, approved (bool), last_reconciled_at | derived from ApprovedModel |
| MirrorArtifact (Artifactory) | repo_path, checksum, firewall_status, source_url, cached_at | matches AllowlistEntry |
| ServingDeployment | model_id, runtime (ollama/vllm/tgi), namespace, endpoint, replicas, strategy | belongs_to ApprovedModel |
| InferenceEvent | id, model_id, tokens, latency_ms, decision, timestamp | belongs_to ServingDeployment |

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Model approved in Registry but the Sonatype firewall flags a critical/malicious component | Block publish; mark `quarantined`; do not allowlist |
| Model revoked in Registry while serving | Reconcile removes allowlist; serving scaled down; pulls denied |
| HF repo ID requested but not approved | Artifactory does not cache; EKS pull denied; audited |
| Pinned digest mismatch on pull | Fail-closed; checksum mismatch alert; do not serve |
| Netskope unblock accidentally broadened | Verification monitor alerts; revert to Artifactory-only scope |
| ML repo layout not licensed | Block Phase 0 repo config until licensing confirmed (spike output) |
| Single-replica pod update on full node | `Recreate` strategy used; no second Pending pod |
| Two models share a base but differ by digest | Treated as distinct allowlist entries (digest-keyed) |

## Constraints

- **Egress**: only Artifactory may reach `huggingface.co`; EKS never does (fail-closed, verified).
- **Authority**: the ACP Model Registry approved set is the single source of truth for the allowlist.
- **Approval**: no model servable without GenAI Risk Triage + Legal + registry approval.
- **Phasing**: Phase 0 rides the in-flight ISRA (dev, Gemma 3n only); Phase 1 requires a **separate ISRA + ATG**.
- **Platform**: EKS `slf-eks-t1k-ca-dev`, `acp-data` namespace; Artifactory v7.104.15; AI Gateway already deployed.
- **Safety**: safetensors preferred; no pickle execution; isolated serving pods; provenance retained.
- **No fine-tuning / no training on customer data** — inference serving only.

## Traceability

| Requirement | D0 Success Criteria | Jira Task |
|-------------|--------------------|-----------|
| US-1 / FR-7 | Scoped egress; EKS containment | T2 |
| US-2 / FR-1 | Single vetted source; Sonatype Repository Firewall screening | T3 |
| US-3 / FR-2 | Registry-gated allowlist | T9 |
| US-4 / FR-3 | Per-model gate; approval artifacts | T4, T5 |
| US-5 / FR-4, FR-5 | POC serving; OpenAI-compatible | T6 |
| US-6 / FR-6 | Observability coverage | T7 |
| US-7 / FR-8 | Generalized onboarding | T10, T12 |
| US-8 / FR-8 | Separate ISRA + ATG | T11 |
| NFR-2 (licensing) | Single vetted source | T1 (spike) |
| NFR-5/6 (integrity/safety) | Supply-chain scanning | T13 |
