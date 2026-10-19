# Draft ACPDIS idea — AWS-native content-safety evaluator

> **SUPERSEDED by [acpdis-idea-content-safety-evaluator.md](acpdis-idea-content-safety-evaluator.md)**
> per [DD-13](../d2-design.md#dd-13-the-ballot-idea-is-reframed-to-the-non-gcp-path-with-two-reference-backends).
> Upstream FR-15 is a single gap and the framework change is identical for a self-hosted and a
> managed backend, so two ballot ideas would split the vote on one problem. The submitted idea
> leads with the self-hostable backend, which serves members on any cloud; Bedrock is carried in it
> as the managed reference.
>
> **Do not submit this version.** It is retained for the Bedrock-specific implementation detail the
> superseding draft does not repeat: the `ApplyGuardrail` field mapping, the cross-account
> credential position, and the `ca-central-1` availability evidence.

> **Status**: draft, **not submitted**. Delivery vehicle for
> [D1 gap G-5](../d1-requirements.md#g-5-no-content-safety-evaluator-outside-google-cloud) and
> [D2 §5.7](../d2-design.md#57-option-c-aws-bedrock-guardrails-managed).
>
> **Check the ballot before submitting.** Verified on 2026-09-11 that no ACPDIS idea covers an AWS or
> non-GCP content-safety evaluator. If one has been raised since, support it rather than duplicating.

---

## Title

**AWS-Native Content Safety Evaluator**

## Summary

Luminate's guardrail framework supports one managed content-safety service: Google Cloud Model
Armor. A member whose AI traffic runs on AWS, and whose data-residency position forbids sending
prompt or completion content to Google Cloud, has no equivalent — they get `banned_words` and
Presidio PII detection, and nothing for prompt injection, jailbreak detection, denied topics or
contextual grounding.

This idea adds a second managed evaluator, backed by **AWS Bedrock Guardrails**, through the same
remote-evaluator framework Model Armor already uses. It is an additional `GuardrailType` and a
sidecar — not a new subsystem.

## Problem

The guardrail framework is deliberately pluggable: FR-2 makes an evaluator type "backed either
in-process or by a remote endpoint", and D-5 settles that managed evaluators are sidecars rather
than in-gateway adapters. The framework is not the constraint. The **catalogue** is.

Today `GuardrailType` has three members, and only one of them reaches a managed content-safety
service:

| Type | Backing | Covers |
|---|---|---|
| `banned_words` | in-process | literal term lists |
| `pii_detection` | Presidio sidecar | PII entities |
| `model_armor` | **Google Cloud** | prompt injection, jailbreak, RAI categories, sensitive data |

For a member on AWS this produces three problems at once:

1. **A capability gap.** Prompt-injection and jailbreak detection are reachable *only* through Model
   Armor. The Guardrails D2 says so directly — FR-15 is out of scope because it is "largely reachable
   today through a `model_armor` template".
2. **A residency conflict.** Model Armor requires sending the content to be inspected to Google
   Cloud. For a regulated member whose AI traffic is already contained within one AWS region, an
   inspection control that exports content to a second cloud can be harder to defend than having no
   control at all.
3. **A second cloud relationship for one control.** GCP project, Workload Identity, template
   management and a vendor assessment, to inspect traffic that never otherwise leaves AWS.

## Proposal

Add `bedrock_guardrails` as an evaluator type, backed by a sidecar calling the Bedrock
`ApplyGuardrail` API.

`ApplyGuardrail` is the right primitive: it is **model-independent**, so the evaluator inspects
arbitrary text without invoking a model, exactly as Model Armor's sanitize call does. Its configured
policies (content filters, denied topics, word filters, sensitive-information filters, contextual
grounding) line up with the categories Model Armor covers.

**The sidecar wire contract needs no change.** The existing shape maps one-to-one:

| Luminate sidecar field | Bedrock `ApplyGuardrail` |
|---|---|
| `action: "block"` | `action == GUARDRAIL_INTERVENED` with a blocking policy |
| `action: "redact"` + `replacement_text` | the masked output text |
| `matched_terms` | assessment policy / filter-type labels — categorical, never content |
| `reason` | `bedrock_guardrails_match` |
| 502 on any failure to obtain a verdict | gateway applies its own fail policy per D-9 |

That last row preserves the single failure matrix: as `services/model-armor/app/main.py` puts it,
`fail_open` "is consumed by the gateway, not here".

Config mirrors Model Armor's: `{guardrail_id, guardrail_version, region, fail_open}`, validated
against the expected shape and optionally restricted to a deployment-configured account allow-list —
the same pattern as `MODEL_ARMOR_ALLOWED_PROJECTS`. A `BEDROCK_GUARDRAILS_ENABLED` deployment flag,
default off, gates creation so a member without AWS cannot author a type they cannot evaluate.

## Why this is a good fit for the framework

- **The seam is already reserved.** Guardrails D2, Out-of-Scope: *"Jailbreak / prompt-injection
  evaluator (FR-15) — largely reachable today through a `model_armor` template. **A non-GCP path is a
  later type.** Future phase? Yes."* This idea is that later type.
- **It proves the abstraction.** A second managed evaluator is the first real test that FR-2's
  registry is provider-neutral rather than Model Armor-shaped. Whatever has to change to accommodate
  it makes the third one cheaper.
- **It meets the standing NFRs without exception.** NFR-15 (no service-account key files, short-lived
  keyless credentials) and NFR-16 (credential-free image, identical across environments) are
  satisfied by IRSA → STS, which is how AWS-hosted gateways already reach Bedrock for inference.
- **It is small.** An enum member, a config validator, a TypedDict, a projector, one portal form
  branch, and a sidecar copied from `services/model-armor/`.

## Why it cannot be solved locally

Three routes were considered and rejected:

- **Reuse `model_armor` pointing at a Bedrock-backed sidecar.** `_validate_model_armor_config`
  enforces `projects/<p>/locations/<l>/templates/<t>` with an optional project allow-list, and the
  portal labels the field Model Armor. Encoding an AWS identity into a GCP resource-name field to get
  past a validator is an audit finding waiting to happen.
- **Add the type in a member fork.** `GuardrailType` is a shared `StrEnum` in `luminate_types`, and
  the enum's own docstring is explicit that a gateway running an older copy **denies the request
  with `portal_invalid_guardrails`** rather than ignoring the spec — org-wide for an org-scoped
  attachment. A forked type breaks every gateway not rebuilt in lockstep. Adding a type is
  necessarily a coordinated, upstream change.
- **Live with Presidio.** Presidio covers PII well and is the right interim answer. It does not cover
  prompt injection, jailbreak, denied topics or contextual grounding, which is the whole argument.

## Offer

Sun Life is well placed to **contribute this rather than request it**. We already run the
cross-account Bedrock path the evaluator would use — gateway IRSA assuming a delegated spoke role in
the workload account — and the Bedrock Guardrails control plane is confirmed available in
`ca-central-1`, so a regional-residency deployment is demonstrable rather than theoretical.

Subject to ranking, Sun Life would contribute the evaluator type, the sidecar service, the portal
form branch, and the tests, following the Model Armor implementation as the reference.

## Scope

**In**: `bedrock_guardrails` evaluator type; config schema + validation + account allow-list;
sidecar service; deployment flag; portal authoring; request and response directions.

**Out**: Bedrock Guardrails *authoring* inside Luminate — the guardrail is managed in AWS and
referenced by id and version, exactly as a Model Armor template is managed in GCP. Automated
Reasoning policies. Any change to the failure matrix (D-9), the merge rule (D-1) or the audit
contract.

## Open questions for the squad

1. Should a deployment be able to enable more than one managed evaluator at once, or is
   one-per-deployment the intended posture?
2. Does the evaluator's own region belong in the guardrail config (per-control) or in deployment
   settings (per-gateway)? Model Armor puts it in the template resource name, which makes it
   per-control by accident rather than by decision.
3. `ApplyGuardrail` returns rich assessment detail. How much may cross the sidecar boundary before it
   stops being a categorical label and starts being content, under NFR-9?

## Related

- Guardrails D1 / D2 / D3 — `luminate-designs` → `docs/projects/luminate/02-architecture-and-design/designs/guardrails/`
- `d2-guardrails-model-armor.md` — superseded, retained for the sidecar deployment shape this copies
- ACPDIS-25 Content Guardrail Enforcement (Delivery) — the framework this extends
- ACPDIS-97 Enterprise DLP Integration (Parking Lot) — adjacent, different shape
- Sun Life: [EACPP-1295](https://sunlife.atlassian.net/browse/EACPP-1295) Guardrails Enablement
