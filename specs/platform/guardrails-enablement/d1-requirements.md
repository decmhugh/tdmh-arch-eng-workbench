# Guardrails Enablement — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: [EACPP-1295](https://sunlife.atlassian.net/browse/EACPP-1295)
>
> Platform facts carry forward from [D0 §3–§5](d0-discovery.md), verified against `luminate`
> `origin/main` `7b33b6706` and `luminate-sunlife-deploy` `origin/main` `7d5a35b` on 2026-09-11.
> Requirements here are **Sun Life's**, not the platform's. Where a requirement is met by shipping
> Luminate behaviour it says so and the work is configuration; where it is not, it is named as a
> gap in §4.

## 1. Scope of this gate

D1 answers one question: *what must be true before we can say Sun Life enforces content controls
on AI traffic, and which of those things does Luminate already do?*

It deliberately does **not** specify which words or which PII entities. That content is owned by
Privacy and Security (D0 Q-1) and is consumed here as configuration — the same separation the
capability map draws for compliance-regime content in INT-10.

## 2. Functional requirements

| ID | Requirement | Priority | Met by |
|---|---|---|---|
| FR-1 | Every Sun Life gateway resolves at least one enforcing content control on the LLM lane. | Must | Configuration |
| FR-2 | A control that cannot be evaluated on the gateway it is bound to must not read as enforcing. Either the evaluator resolves, or the operator has explicitly chosen to deny. | Must | **Gap G-1** — platform fails open by default |
| FR-3 | `banned_words` controls are authorable and enforce with no additional infrastructure. | Must | Shipping — `LOCAL_EVALUATORS` |
| FR-4 | `pii_detection` controls are authorable and enforce, with the Presidio sidecar deployed alongside every gateway. | Must | Sidecar deploy + `GATEWAY_GUARDRAIL_REMOTE_ENDPOINTS` |
| FR-5 | A control can be bound to the caller (organization, project, agent, MCP server, application) or to the destination (model, MCP server). | Must | Shipping — 8 attachment scopes |
| FR-6 | Caller-side controls resolve for Sun Life's JWT client-credentials callers, not only for `lum_` API keys. | Must | Shipping — `facts.py::_collect_guardrails` source branch. **Contradicts D2 FR-6; see D0 §3.4** |
| FR-7 | A control can run in `warn` before it runs in `enforce`, so impact is observable before it denies. | Must | Shipping — `GuardrailMode.warn` |
| FR-8 | Response-direction controls apply on the LLM lane. | Must | Shipping — model-lane response scanner |
| FR-9 | A caller cannot disable a resolved response control from its own request. | Must | **Gap G-2** — `"stream": true` bypasses it under the default |
| FR-10 | Every evaluation — match, no-match and failure alike — produces a retained record attributable to caller, target, direction and request id. | Must | Shipping — `GuardrailEvaluation`, count-only |
| FR-11 | No matched term, span content, prompt or completion is ever persisted in an evaluation record. | Must | Shipping — D2 NFR-9; `banned_words` matches stay count-only, PII / Model Armor emit category labels only |
| FR-12 | Evaluation records are pruned on a stated retention window, and the window is a deliberate choice rather than a default. | Must | `retention_days` + `GUARDRAIL_RETENTION_DELETE_ENABLED` (currently `false`) |
| FR-13 | An operator can see, per control, what it matched and what action was taken, filtered by outcome and direction. | Must | Shipping — portal activity surface |
| FR-14 | The deployed posture — fail mode, streaming mode, timeouts, endpoint map — is expressed in `luminate-sunlife-deploy` and reproducible from it. | Must | Chart + values work |
| FR-15 | The same posture is applied to all five Sun Life gateways (DEV install `luminate`; PROD install `luminate`, `luminate-gw-dev`, `luminate-gw-sit`, `luminate-gw-stage`), or a difference is recorded with its reason. | Must | Values work |
| FR-16 | A control set can be re-applied idempotently to a rebuilt environment. | Should | `bootstrap-data` YAML seeding — upstream FR-14, **Should Have, not built** → **Gap G-3** |
| FR-17 | Guardrail configuration changes are auditable — who changed a binding's posture, and when. | Should | **Gap G-4** — upstream AIC-699 / AIC-777 / AIC-778 open |
| FR-18 | A content-safety control covering prompt injection, jailbreak and topic policy is authorable, without depending on Google Cloud. | Could — Phase 2 | **Gap G-5** — upstream ships no non-GCP path |
| FR-19 | Where a use case's data must not leave the cluster, a content-safety control exists that inspects it **in-cluster**. | Could — Phase 2 | Options A and B in [D2 §5](d2-design.md#5-phase-2-closing-the-content-safety-gap). Presidio already meets this for PII |
| FR-20 | Any evaluator model Sun Life self-hosts is acquired, licence-screened, digest-pinned and revocable through the existing governed path rather than a bespoke one. | Could — Phase 2 | SLM pipeline controls C1–C10. **No new mechanism required** |

## 3. Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | The request-direction guardrail phase adds no more than the largest resolved evaluation ceiling plus fan-out, and that figure is **measured in DEV before PROD rollout**, not quoted. Upstream withdrew its 200 ms target (D-6) precisely because it was never measured. |
| NFR-2 | Performance | The response-path time-to-first-token delta under `guardrail_response_streaming: enforce` is measured and published before the mode is enabled in PROD. |
| NFR-3 | Availability | A sidecar outage under a fail-closed posture denies traffic. That is intended, and there is a runbook for it with a named rollback lever. |
| NFR-4 | Availability | The rollback lever is documented as *unset the endpoint for that type*, which returns the control to fail-open — **and therefore silently unenforcing**. Any use of it must be announced, not quiet. |
| NFR-5 | Security | The sidecar image is credential-free and identical across environments; only the injected identity differs. Mirrors upstream NFR-16. |
| NFR-6 | Security | No service-account key file exists in any environment. Phase 2's Bedrock path is IRSA → STS only. Mirrors upstream NFR-15. |
| NFR-7 | Security | Evaluated content does not leave the cluster for an in-process or in-cluster evaluator. Any evaluator that sends content to an external service is a data-classification decision before it is a technical one (D0 Q-6). **An in-cluster evaluator dissolves that question rather than answering it**, which is why [DD-11](d2-design.md#dd-11-phase-2s-default-is-in-cluster-and-open-source-bedrock-is-the-fallback-not-the-plan) prefers one. |
| NFR-8 | Scalability | Sidecar resource requests and limits are sized from measurement, one sidecar per gateway pod (upstream NFR-8, generalising NFR-14), and the cost of that fan-out across five gateways is stated. |
| NFR-9 | Observability | Per-evaluator latency, deny rate per control, evaluator availability and audit drop counters are visible in the existing Splunk / Langfuse path before PROD rollout. |
| NFR-10 | Operability | The posture is legible from the cluster — `kubectl get cm luminate-gateway -o yaml` shows every guardrail setting in force, with none inherited silently from a code default. |

## 4. Gaps

Graded with the capability-map convention: a capability is only ✅ when it has a **runtime consumer
on the request path**. Each gap states whether it is *ours to configure* or *a platform behaviour*,
because that decides who fixes it (see
[Capability Gap Escalation](../../../process/capability-gap-escalation.md)).

### G-1 — An unevaluable control reads as enforcing

**Platform behaviour.** `_UnresolvedEvaluator` applies `spec_fail_open(spec, default=True)`, so a
`pii_detection` or `model_armor` guardrail bound to a gateway with no endpoint for that type
forwards the traffic and records `guardrail_evaluator_unresolved`. The portal shows it attached and
enforcing throughout.

The upstream default is defensible in its own terms — it protects the documented rollback lever,
and the alternative would turn a routine endpoint change into an org-wide denial. The gap is not
that the default is wrong; it is that **nothing surfaces the resulting state to the operator**.

*Sun Life mitigation (this spec):* deploy the sidecar before authoring any remote-type control,
and set `fail_open: false` explicitly on every enforcing remote-type control we create. Verify by
the absence of `guardrail_evaluator_unresolved` rows, not by the portal.
*Upstream:* AIC-714 ("Refuse guardrail attachments on flow types that cannot be enforced") is the
closest existing item. It was done on 2026-09-17 and covers flow types only, not unevaluable types.
A narrower ask — *warn at attach time when the bound gateway has
no evaluator for the type* — is worth raising; it is a portal affordance, not a platform capability
change, so it does not need a ballot idea.

### G-2 — A caller can opt out of response controls

**Platform behaviour**, and upstream already agrees it is a defect: D2 NFR-7 states it is "not met
today" and D-11 removes the exemption rather than narrowing the requirement.

*Sun Life mitigation:* `guardrail_response_streaming: enforce` exists today and is what the
upstream local stack runs. Enable it once NFR-2 is measured. Until then, DEV runs `audit` (the
code default since AIC-691). For a streaming caller, every response-direction control is
**detective only**: the response is scanned after delivery and never blocked or redacted. Do not
claim otherwise in any onboarding document.
*Upstream:* AIC-680 (default posture) and AIC-717 (buffered, redaction-capable streaming) were
decided on 2026-09-13, and AIC-691 (2026-09-17) implemented `audit`. ACPDIS-98 is in Discovery on the
ballot. Sun Life should support ACPDIS-98 at the next Product Board round rather than raise a
duplicate.

### G-3 — No declarative seeding of a control set

**Platform behaviour.** Upstream FR-14 (YAML bootstrap seeding) is *Should Have* and explicitly out
of scope for the current phase. `backend/app/ops/bootstrap-data/{dev,demo}/guardrails.yaml` exist
as demo fixtures, not as a supported operator surface.

*Sun Life mitigation:* author the first control set through the API with a recorded, re-runnable
script under `luminate-sunlife-deploy`, and treat that script as the source of truth until seeding
lands. Note this is state in a database that no GitOps pipeline reconciles — a rebuilt environment
loses the controls silently.

### G-4 — Configuration-change audit is incomplete

**Platform behaviour.** Upstream has three open items acknowledging it: AIC-699 (an attachment mode
change leaves no audit record), AIC-777 (a cascaded attachment delete leaves no audit record),
AIC-778 (a binding's posture cannot be changed from the portal at all). All Backlog or In Review.

*Sun Life mitigation:* until those land, every control change goes through the recorded script from
G-3, so the change history lives in git even though it does not live in the platform.

### G-5 — No content-safety evaluator outside Google Cloud

**Platform absence**, and a *deliberate* one: the D2's Out-of-Scope table says a non-GCP path is a
later type. Not a defect — an unbuilt capability with the seam reserved.

Prompt injection, jailbreak and topic policy are reachable today **only** through `model_armor`,
which is Google Cloud. `banned_words` and `pii_detection` do not cover them, and `llm_judge` —
which would — is designed but not built.

*Route:* a new ACPDIS ballot idea (draft at
[references/acpdis-idea-content-safety-evaluator.md](references/acpdis-idea-content-safety-evaluator.md)).
An ask absent from ACPDIS cannot be ranked at a Product Board round, so no AIC story is the right
first move.

*Three routes exist and they are not exclusive* — see [D2 §5](d2-design.md#5-phase-2-closing-the-content-safety-gap).
The recommendation ([DD-11](d2-design.md#dd-11-phase-2s-default-is-in-cluster-and-open-source-bedrock-is-the-fallback-not-the-plan))
is **in-cluster and open-source first**: it removes the data-custody question entirely, needs no
vendor account, and — because it serves members on any cloud — is the stronger argument at a
Product Board round than an AWS-specific one. Sun Life is well placed to contribute either, holding
both a self-hostable serving stack and a working cross-account Bedrock path.

**The cheapest move is not a contribution at all**: ACPDIS-84 (`llm_judge`) is already on the ballot
in Discovery, and a judge routed to a self-hosted safety model closes most of this gap with a vote
rather than code.

### G-6 — No response scanning outside the LLM lane

**Platform behaviour**, honestly audited (`response_scan_unsupported_target`) rather than silently
dropped. Raise upstream only if a Sun Life use case actually needs MCP or A2A response inspection;
do not raise it speculatively.

## 5. Requirement-to-capability trace

| Requirement | CAP | Verdict today |
|---|---|---|
| FR-1, FR-3, FR-5, FR-7, FR-8, FR-10, FR-11, FR-13 | [CAP-10](../../../capability-map.md#cap-10) | ✅ platform-available, **unconfigured at Sun Life** |
| FR-4 | CAP-10 | ✅ platform-available, needs sidecar deployment |
| FR-2, FR-9 | CAP-10 | ⚠️ shipped with a documented hole |
| FR-16, FR-17 | CAP-10 | ⚠️ upstream backlog |
| FR-18, FR-19 | CAP-10 | ❌ absent, seam reserved — three routes, see D2 §5 |
| FR-20 | — (Sun Life-side, [slm-pipeline](../slm-pipeline/d2-design.md)) | ✅ governed acquisition path already designed |
| FR-12 | CAP-10 / [CAP-19](../../../capability-map.md#cap-19) | ✅ mechanism ships; window is our decision |

**Capability-map follow-up.** CAP-10's grading is about Luminate and is correct. This spec's finding
is that the same row is read as a statement about Sun Life, and is then wrong. Recommend the
catalogue gain a deployment-state qualifier for CAP-10 — the same distinction INT-02 already draws
for credential backends that are "built and switched off". Tracked as T16.

## 6. Acceptance criteria

| ID | Criterion | Verifies |
|---|---|---|
| AC-1 | `kubectl get cm luminate-gateway -o yaml` on all five gateways shows an explicit value for `GATEWAY_GUARDRAIL_REMOTE_ENDPOINTS`, `GATEWAY_GUARDRAIL_REMOTE_FAIL_OPEN`, `GATEWAY_GUARDRAIL_REMOTE_TIMEOUT` and `GATEWAY_GUARDRAIL_RESPONSE_STREAMING` | FR-14, FR-15, NFR-10 |
| AC-2 | A crafted request containing a banned term returns HTTP 422 with the structured guardrail error, and the evaluation row reads `outcome=matched, action_taken=block` | FR-1, FR-3 |
| AC-3 | A crafted request containing a Canadian SIN is forwarded with the value replaced, and the upstream receives the redacted body | FR-4 |
| AC-4 | Across the DEV proving run, **zero** evaluation rows carry `failure_reason=guardrail_evaluator_unresolved` | FR-2, G-1 |
| AC-5 | A `warn`-mode control produces `x-luminate-guardrails-warned` and an evaluation row, and does not alter the body | FR-7 |
| AC-6 | A response-direction control on a **non-streamed** completion withholds a violating completion; the same control on a **streamed** completion is shown, with evidence, to behave per the deployed `guardrail_response_streaming` value | FR-8, FR-9, G-2 |
| AC-7 | No evaluation row contains a matched term, prompt or completion; PII rows carry entity labels only | FR-11 |
| AC-8 | Measured p50/p95/p99 for the guardrail phase and the TTFT delta are recorded in D4 | NFR-1, NFR-2 |
| AC-9 | A sidecar is scaled to zero in DEV and the resulting caller-visible behaviour matches the documented fail posture | NFR-3 |
| AC-10 | The control set can be dropped and recreated from the recorded script with identical resulting rows | FR-16, G-3 |

## 7. Related

- [D0 — Discovery](d0-discovery.md) · [D2 — Design](d2-design.md) · [D3 — Tasks](d3-tasks.md)
- [ACP Capability Map — CAP-10](../../../capability-map.md#cap-10)
- [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
