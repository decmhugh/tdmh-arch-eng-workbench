# Draft ACPDIS idea — Non-GCP content safety evaluators

> **Status**: draft, **not submitted**. Delivery vehicle for
> [D1 gap G-5](../d1-requirements.md#g-5-no-content-safety-evaluator-outside-google-cloud) and
> [D2 §5](../d2-design.md#5-phase-2-closing-the-content-safety-gap). Submitted by the Sun Life
> consortium representative under [T17](../d3-tasks.md).
>
> **Supersedes** `acpdis-idea-bedrock-guardrails.md` per
> [DD-13](../d2-design.md#dd-13-the-ballot-idea-is-reframed-to-the-non-gcp-path-with-two-reference-backends):
> one gap, one idea, two reference backends — leading with the self-hostable one. The superseded
> draft is retained for its Bedrock-specific implementation detail.
>
> **Check the ballot before submitting.** Verified on 2026-09-11 that no ACPDIS idea covers a
> non-GCP content-safety evaluator. If one has been raised since, support it rather than duplicating.
>
> **Rank ACPDIS-84 alongside this, not instead of it.** `llm_judge` closes a large part of the same
> gap for members who can host a model, and it is already on the ballot in Discovery. The two are
> complementary — see *Relationship to ACPDIS-84* below.

---

## Title

**Non-GCP Content Safety Evaluators**

## Summary

Luminate's guardrail framework supports exactly one managed content-safety service: Google Cloud
Model Armor. Prompt injection, jailbreak detection, denied topics and contextual grounding are
reachable **only** through it. A member without a Google Cloud relationship — or whose
data-residency position forbids sending prompt and completion content to a second cloud — gets
`banned_words` and Presidio PII detection, and nothing else.

This idea adds content-safety evaluation that does not require Google Cloud, through the same
remote-evaluator framework Model Armor already uses. It proposes **two reference backends**:

1. **A self-hostable classifier** running in the member's own cluster — no vendor account, no
   egress, no per-call charge. *The default.*
2. **A managed cloud service** (AWS Bedrock Guardrails as the worked example) for members who prefer
   not to operate a model.

Both are the same framework change. Neither is a new subsystem.

## Problem

The framework is deliberately pluggable — FR-2 makes an evaluator type "backed either in-process or
by a remote endpoint", and D-5 settles that managed evaluators are sidecars rather than in-gateway
adapters. **The framework is not the constraint. The catalogue is.**

Today `GuardrailType` has three members, and only one reaches a managed content-safety service:

| Type | Backing | Covers |
|---|---|---|
| `banned_words` | in-process | literal term lists |
| `pii_detection` | Presidio sidecar | PII entities |
| `model_armor` | **Google Cloud** | prompt injection, jailbreak, RAI categories, sensitive data |

For a member outside GCP this produces three problems at once:

1. **A capability gap.** Prompt-injection and jailbreak detection have no other path. The Guardrails
   D2 says so directly — FR-15 is out of scope because it is "largely reachable today through a
   `model_armor` template".
2. **A residency and custody conflict.** Model Armor requires sending the content to be inspected to
   Google Cloud. For a regulated member whose AI traffic is otherwise contained within one cloud and
   one region, an inspection control that exports content to a second cloud can be harder to defend
   than having no control at all.
3. **A whole cloud relationship for one control.** GCP project, Workload Identity, template
   management and a third-party vendor assessment — to inspect traffic that never otherwise leaves
   the member's own infrastructure.

The third point is the one that decides adoption. A control that requires standing up a new cloud
tenancy will not be adopted by the members who most need it.

## Proposal

Add a content-safety evaluator type whose backend is pluggable, with two reference implementations.

### Reference backend 1 — self-hosted classifier (the default)

A sidecar wrapping a small open-licensed classifier, colocated with the Gateway pod exactly as
`pii-detector` is today. Content never leaves the pod. Latency is tens of milliseconds, comfortably
inside NFR-2's ceiling. No GPU, no vendor account, no per-call cost.

This is the backend that makes the capability available to **every member regardless of cloud**, and
it is the one Sun Life offers to contribute.

### Reference backend 2 — managed cloud service

For members who would rather not operate a model. AWS Bedrock `ApplyGuardrail` is the worked
example: it is **model-independent**, so it inspects arbitrary text without invoking a model —
exactly as Model Armor's sanitize call does — and its configured policies (content filters, denied
topics, word filters, sensitive-information filters, contextual grounding) line up with the
categories Model Armor covers.

### The sidecar wire contract needs no change for either

The existing shape already carries what both backends return:

| Luminate sidecar field | Self-hosted classifier | Bedrock `ApplyGuardrail` |
|---|---|---|
| `action: "block"` | label above threshold | `action == GUARDRAIL_INTERVENED` with a blocking policy |
| `action: "redact"` + `replacement_text` | n/a (classify only) | the masked output text |
| `matched_terms` | class labels | assessment policy / filter-type labels |
| `reason` | `<type>_match` | `<type>_match` |
| 502 on any failure to obtain a verdict | same | same |

In both cases `matched_terms` carries **categorical labels only, never content** — preserving NFR-9.
And in both cases the sidecar never decides the fail posture: as
`services/model-armor/app/main.py` puts it, `fail_open` "is consumed by the gateway, not here". That
is what keeps the single failure matrix in D-9 intact.

Config mirrors Model Armor's pattern — a backend discriminator plus backend-specific fields,
validated per type, with an optional deployment-configured allow-list in the same spirit as
`MODEL_ARMOR_ALLOWED_PROJECTS`. A deployment flag defaulting off gates creation, so a member cannot
author a control their deployment cannot evaluate.

## Relationship to ACPDIS-84 (LLM Judge Guardrails)

These overlap and should both be ranked. They solve the same gap at different points on the
cost/capability curve, and neither subsumes the other:

| | This idea | ACPDIS-84 `llm_judge` |
|---|---|---|
| Compute | CPU classifier, or a managed API | **GPU** model |
| Latency | tens of ms | inference-bound |
| Coverage | fixed taxonomy | operator-authored natural-language rules |
| Can redact | yes (managed backend) | **no** — allow/block only, and rewriting is out of scope with *Future phase? No* |
| Barrier to a member | none | must be able to host or reach a judge-eligible model |

A member with no GPU capacity and a strict residency posture is served by this idea and not by
ACPDIS-84. A member wanting bespoke policy rules is served by ACPDIS-84 and not by this one.

## Why this is a good fit for the framework

- **The seam is already reserved.** Guardrails D2, Out-of-Scope: *"Jailbreak / prompt-injection
  evaluator (FR-15) — largely reachable today through a `model_armor` template. **A non-GCP path is
  a later type.** Future phase? Yes."* This idea is that later type.
- **It proves the abstraction.** A second content-safety evaluator is the first real test that FR-2's
  registry is provider-neutral rather than Model Armor-shaped. Whatever has to change to accommodate
  it makes the third one cheaper.
- **It meets the standing NFRs without exception.** The self-hosted backend meets NFR-15 (no
  service-account key files) and NFR-16 (credential-free image) trivially — there is no credential
  at all. The managed backend meets them with short-lived keyless workload identity.
- **It is small.** An enum member, a config validator, a TypedDict, a projector, one portal form
  branch, and a sidecar following the `services/model-armor/` pattern.

## Why it cannot be solved by a member alone

Four routes were considered and rejected:

- **Reuse `model_armor` pointing at a different sidecar.** `_validate_model_armor_config` enforces
  `projects/<p>/locations/<l>/templates/<t>` with an optional project allow-list, and the portal
  labels the field Model Armor. Encoding another provider's identity into a GCP resource-name field
  to get past a validator is an audit finding waiting to happen.
- **Reuse `pii_detection` for a prompt-injection classifier.** It would work at runtime, but the
  config schema is `entities[]` / `redaction_mode`, the portal would label it PII, and the audit's
  categorical labels would misdescribe what was detected.
- **Add the type in a member fork.** `GuardrailType` is a shared `StrEnum` in `luminate_types`, and
  the enum's own docstring is explicit that a gateway running an older copy **denies the request
  with `portal_invalid_guardrails`** rather than ignoring the spec — org-wide for an org-scoped
  attachment. A forked type breaks every gateway not rebuilt in lockstep. Adding a type is
  necessarily a coordinated, upstream change.
- **Live with Presidio.** Presidio covers PII well and is the right interim answer. It does not cover
  prompt injection, jailbreak or topic policy, which is the whole argument.

## Offer

Sun Life offers to **contribute the self-hosted backend**, and can supply the managed backend as a
second reference if the squad wants both landed together.

We are positioned for it. Our existing model-onboarding pipeline already provides the parts a
self-hosted evaluator needs and which are otherwise the expensive half of this work: a governed
mirror with a default-deny allow-list, digest and revision pinning, an automated licence and CVE
gate on download, safetensors-only weight loading, and fail-closed revocation that makes a withdrawn
model unservable within minutes. We also run a working cross-account managed-inference path, so the
second backend is not theoretical either.

## Scope

**In**: a content-safety evaluator type; pluggable backend with two reference implementations;
config schema, validation and optional allow-list; deployment flag; portal authoring; request and
response directions.

**Out**: authoring the safety policy *inside* Luminate — a managed guardrail is referenced by id and
version, exactly as a Model Armor template is; model hosting and lifecycle, which belong to the
member; any change to the failure matrix (D-9), the merge rule (D-1) or the audit contract (NFR-9).

## Open questions for the squad

1. One type with a backend discriminator, or one type per backend? A discriminator keeps the portal
   simpler; separate types keep each config schema honest.
2. Should a deployment be able to enable more than one content-safety backend at once, or is
   one-per-deployment the intended posture?
3. Does the evaluator's region or endpoint belong in the guardrail config (per-control) or in
   deployment settings (per-gateway)? Model Armor puts it in the template resource name, which makes
   it per-control by accident rather than by decision.
4. Managed backends return rich assessment detail. How much may cross the sidecar boundary before it
   stops being a categorical label and starts being content, under NFR-9?
5. Does the framework want an opinion on *which* self-hostable classifier ships as the reference, or
   should that stay a deployment choice with the sidecar accepting any conforming model?

## Related

- Guardrails D1 / D2 / D3 — `luminate-designs` → `docs/projects/luminate/02-architecture-and-design/designs/guardrails/`
- `d2-guardrails-model-armor.md` — superseded, retained for the sidecar deployment shape this follows
- ACPDIS-25 Content Guardrail Enforcement (Delivery) — the framework this extends
- ACPDIS-84 LLM Judge Guardrails (Discovery) — complementary, rank both
- ACPDIS-97 Enterprise DLP Integration (Parking Lot) — adjacent, different shape
- Sun Life: [EACPP-1295](https://sunlife.atlassian.net/browse/EACPP-1295) Guardrails Enablement
