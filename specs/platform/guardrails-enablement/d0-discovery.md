# Guardrails Enablement — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: [EACPP-1295](https://sunlife.atlassian.net/browse/EACPP-1295)
>
> **Verification basis.** Every platform claim below was read out of `luminate` at `origin/main`
> `7b33b6706`, `luminate-designs` at `origin/main` `c8c16d7`, and `luminate-sunlife-deploy` at
> `origin/main` `7d5a35b`, on 2026-09-11. Deployment claims were measured against the running
> clusters on the same day, not inferred from the values files. Each claim carries the file or the
> command it came from.

!!! note "Update — 2026-10-05"
    The body below is the 2026-09-11 baseline and is kept as measured. Three things have moved since:

    - **G-1 happened for real.** AIMS attached a `pii_detection` guardrail (`no-customer-pii`,
      project scope, enforce/block, request + response) in the DEV install. **18 of 18** evaluations
      recorded `guardrail_evaluator_unresolved`, so the traffic passed unscanned while the portal
      read "enforcing" (EACPP-1248).
    - **The streaming default moved.** AIC-680 and AIC-717 were decided on 2026-09-13, and AIC-691
      (2026-09-17) made `audit` a real mode and the code default. §4.3's `exempt` default no longer
      holds on any image at or after that commit; D2 DD-4 is revised to match.
    - **The DEV install now has the evaluator.** T3–T8 shipped in `luminate-sunlife-deploy` PR #28,
      on both DEV-install gateways. The PROD install is unchanged.
## 1. Problem statement

Luminate ships a complete guardrails subsystem. Sun Life runs it switched off.

The [ACP Capability Map](../../../capability-map.md#cap-10) grades **CAP-10 Guardrails** as
**✅ Available** and **Mandatory** — "banned-word, PII (Presidio) and Model Armor scanning on
*both* the request and the response, with block / redact / warn outcomes, and each evaluation
persisted." That grading is correct about the platform. It is not correct about our deployment,
and the map does not distinguish the two.

Measured on 2026-09-11:

| Where | What was measured | Result |
|---|---|---|
| DEV install `360967146904` | `Guardrail.objects.count()` / `GuardrailAttachment` / `GuardrailEvaluation` | `0` / `0` / `0` |
| DEV install | `settings.MODEL_ARMOR_ENABLED` | `False` |
| DEV gateway pod | `printenv \| grep GATEWAY_GUARDRAIL` | no matches |
| PROD install `035722575935` | `cm/luminate-gateway` in `luminate`, `luminate-gw-dev`, `luminate-gw-sit`, `luminate-gw-stage` | 6 keys each, **zero** guardrail keys |
| `luminate-sunlife-deploy` | `grep -ri "guardrail\|pii.detect\|model.armor"` across every values file and template | **zero hits** |

The deployed images are not the constraint. DEV runs gateway `sha-3857f0c` (2026-09-10) and PROD
runs `sha-89356d7`; both contain `gateway/app/middleware/guardrails.py`,
`gateway/app/guardrails/response_scanner.py`, and both sidecar services. The capability is
present in the running binaries and has simply never been configured.

This matters beyond the missing control itself. Guardrails is a **Mandatory** overlay on the
capability map. Any use case onboarded on the strength of that grading — and several have been —
is relying on an inspection layer that does not exist in either install.

## 2. Why now

Three things converge.

**The claim is now load-bearing.** The capability map is the menu for use-case discovery and feeds
Product Board ranking. Governance Mode has shipped and denies on `governance_state`; obligations
resolve controls from a risk band. A Mandatory content control that is graded Available and is in
fact absent is the one kind of error that survives review, because nobody re-checks a ✅.

**The silent-pass failure mode is live.** This is not "nothing happens until we configure it". As
§4.2 shows, the *first* thing an operator is likely to do — create a `pii_detection` guardrail in
the portal and attach it — produces a portal that reads "attached", an activity feed that fills
with rows, and traffic that is never scanned. The control is not merely absent; it is absent in a
way that reads as present.

**Upstream is moving.** ACPDIS-25 *Content Guardrail Enforcement* is in **Delivery** and the
guardrails area is among the most actively worked upstream — 60+ open AIC items reference it. Two
decisions in flight (AIC-680 on the streaming default, AIC-717 on buffered streaming) change the
posture we would deploy. Enabling now, against a documented baseline, is what lets us track those
rather than discover them.

## 3. What upstream actually built

### 3.1 Shape

A `Guardrail` is a named content rule with a type and a typed config. A `GuardrailAttachment`
binds it to exactly one scope and carries the *enforcement intent* — `mode` (`enforce` / `warn`),
`action` (`block` / `redact`), and `applies_to_directions`. The two are deliberately separate, so
the same control can warn broadly and block narrowly.

| Layer | File | Size |
|---|---|---|
| Catalogue + attachment model | `backend/app/guardrails/models.py` | 851 lines |
| Config validation per type | `backend/app/guardrails/models.py` `_CONFIG_VALIDATORS` | — |
| Resolution / merge | `backend/app/policy_engine/guardrail_resolution.py` | 240 lines |
| Fact collection | `backend/app/policy_engine/facts.py` `_collect_guardrails`, `_collect_target_guardrails` | — |
| Decision | `backend/app/policy_engine/rego/authz.rego` `matched_guardrails` | — |
| Enforcement | `gateway/app/middleware/guardrails.py` | 547 lines |
| Evaluators + scanning | `gateway/app/guardrails/` (12 modules) | 2,242 lines |
| Sidecars | `services/pii-detector/`, `services/model-armor/` | — |

Eight attachment scopes, exactly one FK set per row
(`backend/app/guardrails/models.py:ATTACHMENT_SCOPE_FIELDS`):

- **Source** (fires on who is calling) — `organization`, `project`, `api_key`, `agent`,
  `mcp_server`, `application`
- **Target** (fires on what is being called) — `target_model`, `target_mcp_server`

Repeated bindings of one guardrail **merge**, they do not compete (design decision D-1). The
strictest `(mode, action)` wins per direction and directions union across bindings. An
unrecognised pair sorts strictest, so a value added later can never silently weaken enforcement.

### 3.2 Evaluator types — and which ones need infrastructure

`GuardrailType` (`packages/types/src/luminate_types/guardrails.py`) has exactly three members:

| Type | Runtime | Config | Needs a sidecar? |
|---|---|---|---|
| `banned_words` | **in-process** | `words[]`, `case_sensitive` | **No** |
| `pii_detection` | remote | `entities[]`, `language`, `score_threshold`, `entity_thresholds{}`, `redaction_mode` | **Yes** — Presidio |
| `model_armor` | remote | `template` (GCP resource name), `fail_open` | **Yes** — GCP |

`llm_judge` is specified at length in the D2 (FR-17 through FR-20, its own decision set and user
flows) and **is not built** — it is absent from the enum, so a `llm_judge` guardrail cannot be
created. ACPDIS-84 *LLM Judge Guardrails* sits in **Discovery** on the ballot.

`gateway/app/guardrails/registry.py` is explicit that `LOCAL_EVALUATORS` contains one entry,
`banned_words`, and that a remote endpoint always wins over a same-named local one. So
`banned_words` is the only control that works on the images we run today with no new
infrastructure at all.

### 3.3 Where enforcement can and cannot reach

| Lane | `target_type` | Request scanning | Response scanning | Target-scoped attachment |
|---|---|---|---|---|
| LLM `/llm/v1/…` | `model` | Yes | **Yes** | Yes (`target_model`) |
| MCP `/mcp/{endpoint}` | `mcp_server` | Yes | **No** | Yes (`target_mcp_server`) |
| A2A `/a2a/{endpoint}` | `agent` | Yes | **No** | **No** |

Response scanning is model-lane only. `gateway/app/middleware/guardrails.py` refuses it on any
other flow and audits the drop as `response_scan_unsupported_target` rather than letting it read
as a clean pass — but it is still a guardrail an operator configured that is not running.

On the target side, `backend/app/policy_engine/facts.py` sets
`_TARGET_SCOPED_FLOWS = frozenset({"model", "mcp_server"})` because "`authz.rego` has a model
branch and an mcp_server branch and no agent branch". `GuardrailTargetType.AGENT` exists as a
*flow-type filter* on a caller-scoped attachment; it is not a target you can protect.

Scan text extraction (`gateway/app/guardrails/input_extractor.py`) pulls the last chat message for
a chat-shaped body and otherwise falls back to decoding the whole body. On the MCP lane that means
the guardrail scans the raw JSON-RPC envelope, not a tool argument — workable for banned terms and
PII, crude for anything structural.

### 3.4 Two correctness notes about the upstream design docs

The design corpus is authoritative but, in two places, **behind the code**. Both are recorded here
so a reader who checks the D2 and finds a contradiction knows which way it falls.

- **D2 FR-6** says caller-side resolution "needs a caller identity that carries the scope chain.
  Today that is the API key and only the API key, so this is not met for a caller that
  authenticates any other way." **The code does not agree.** `facts.py::_collect_guardrails`
  branches: with no API key presented it resolves `_source_scope_keys(source_id, ownership)` and
  exports `source_guardrails[input.jwt.sub]`, which `authz.rego` reads. JWT callers resolve
  caller-side guardrails. This matters directly — Sun Life runs JWT client-credentials callers
  with `APP_AGENT_API_KEYS_ENABLED=false`, so under the D2's reading no caller-side control would
  ever fire here. Under the code's behaviour they do.
- **`d2-guardrails-model-armor.md`** is marked **Superseded** and warns that its own contract
  names predate the umbrella (`directions` is really `applies_to_directions`). Take data-model and
  API names from `d2-guardrails.md` only. It is retained for the GCP template model and the
  sidecar deployment shape, which is exactly the part Phase 2 reuses.

## 4. The three findings that shape the work

### 4.1 The fail-open default is the wrong way round for us

`gateway/app/settings.py` defaults (env prefix `GATEWAY_`):

| Setting | Default | Consequence |
|---|---|---|
| `guardrail_remote_endpoints` | `{}` | no remote evaluator is reachable |
| `guardrail_remote_fail_open` | `False` | a sidecar *outage* fails closed |
| `guardrail_remote_timeout` | `1.5` s | tuned for a warm sidecar with its model preloaded |
| `guardrail_remote_max_text_bytes` | `256,000` | over-length text is a scan *failure*, not a pass |
| `guardrail_response_streaming` | **`"exempt"`** | streamed responses pass unscanned |
| `guardrail_response_max_buffer_bytes` | `8,000,000` | overflow applies the fail policy |

Note the asymmetry. A sidecar that is *configured and down* fails **closed**. A sidecar that was
**never configured** fails **open**.

### 4.2 A guardrail with no evaluator passes traffic, while reading as enforcing

This is the single most important operational fact in this document.

Be precise about what "silent" means here, because it decides where the fix goes. The
non-evaluation **is** recorded — a `WARNING` in the gateway log and an evaluation row carrying
`failure_reason=guardrail_evaluator_unresolved`. It is not invisible to an operator who knows to
look for it. What is silent is the **portal**, which shows the control attached and enforcing
throughout, and the **caller**, who sees a normal response. So this is not an observability gap to
fix with a dashboard; it is a state that reads as success everywhere a human actually looks.

When `registry.get_evaluator()` returns `None` — which happens for *any known type* with no
in-process evaluator and no configured endpoint, i.e. **every `pii_detection` and `model_armor`
guardrail on a gateway whose endpoint map is empty** — the middleware substitutes
`_UnresolvedEvaluator`, whose `evaluate()` resolves `spec_fail_open(spec, default=True)`.

The `default=True` is deliberate and documented: inheriting the deployment knob "would flip every
guardrail that expressed no preference to fail-closed and destroy the rollback lever" — unsetting
a sidecar endpoint is the documented way to roll a control back without editing every attachment.

The consequence for a deployment in our state is that the obvious first action produces a
convincing illusion:

1. An operator creates a `pii_detection` guardrail in the portal. It saves.
2. They attach it to an organization scope. It saves.
3. The portal shows it attached and enforcing.
4. Every request resolves it, finds no evaluator, records `guardrail_evaluator_unresolved`, and
   **forwards the traffic unscanned**.
5. The activity feed fills with rows, so "there is audit" is also true.

Only an explicit per-guardrail `fail_open: false` denies in that state. Nothing in the portal
warns that the type has no evaluator on the gateway it is bound to. Upstream AIC-714 ("Refuse
guardrail attachments on flow types that cannot be enforced") is the nearest fix and sits in
**Backlog**.

**This is why the deployment order in this spec is sidecar-first, control-second, and why the
first control we author is `banned_words`.** It is also why T8's definition of done is the
*absence* of `guardrail_evaluator_unresolved` rows rather than the presence of evaluation rows —
rows appear either way.

### 4.3 Streaming is exempt by default, and upstream says so

`guardrail_response_streaming` defaults to `"exempt"`: a streamed (SSE) response passes through
with no response-direction scanning and no evaluation record. The `"audit"` value is reserved and
treated as `exempt`; only `"enforce"` scans.

The upstream D2 does not present this as a design choice. **NFR-7**: "Evaluation cannot be skipped
from the client side. No client-supplied header, body field or query parameter can disable a
resolved guardrail. **This is not met today**: under the default streaming setting a
client-supplied `"stream": true` causes a response-direction guardrail to pass unscanned and
unrecorded. The requirement is not narrowed to accommodate that. The exemption is removed
instead, see D-11."

So a caller opts out of our response controls by setting one boolean in their own request body.
For a chat-shaped Sun Life use case that is the *normal* request. Two upstream decisions are open
on it — AIC-680 (default posture, **In Review**) and AIC-717 (buffered redaction-capable
streaming, **In Review**) — plus ACPDIS-98 *Streaming Response Guardrails* in **Discovery**.

We do not have to wait for either. `enforce` exists today and the upstream local stack runs with
it on. What we owe is a measurement of what it costs on time-to-first-token before we turn it on
in PROD (upstream AIC-693 is the matching task, in **To Do**).

## 5. Closing the content-safety gap — the Phase 2 question

Phase 1 gives us banned terms and PII. Neither covers prompt injection, jailbreak or topic policy.
Upstream's only answer to those is `model_armor`, which is Google Cloud — and Sun Life has no GCP
path for this traffic.

The question was first framed as "can we use AWS Bedrock Guardrails?". That framing is too narrow,
and §5.6 explains why. The honest question is **who inspects the content, and where does it go** —
which has an in-cluster open-source answer as well as a managed-cloud one.

### 5.1 There is no Bedrock support, and the field cannot be borrowed

`ApplyGuardrail`, `guardrailIdentifier` and "bedrock guardrail" return **zero hits** across every
`.py`, `.ts`, `.vue` and `.md` file in `luminate`. There is no partial implementation to finish.

The `model_armor` type cannot be quietly repurposed to point at Bedrock.
`_validate_model_armor_config` requires `template` to match
`projects/<project>/locations/<location>/templates/<template>` and optionally restricts the
project segment to `MODEL_ARMOR_ALLOWED_PROJECTS`. A Bedrock guardrail identifier and version do
not have that shape, the portal labels the field Model Armor, and encoding an AWS identity into a
GCP resource-name field to get past a validator is the kind of thing that is discovered during an
audit rather than explained during one.

### 5.2 But the seam is explicitly reserved

The D2's Out-of-Scope table, FR-15:

> **Jailbreak / prompt-injection evaluator (FR-15)** | Largely reachable today through a
> `model_armor` template. **A non-GCP path is a later type** | Future phase? **Yes**

And FR-2 makes a new type a registry entry plus a typed config schema rather than a schema change,
while D-5 settles that evaluators are **sidecars, not in-gateway adapters**. A `bedrock_guardrails`
type is therefore the shape the design already anticipates, not a deviation from it.

The work is genuinely bounded: an enum member, a config validator, a TypedDict, a projector, a
portal form, and a FastAPI sidecar that mirrors `services/model-armor/` — whose wire contract is
already exactly what a Bedrock `ApplyGuardrail` response maps onto (`action`, `matched_terms` as
categorical labels, `replacement_text` for the masked output).

### 5.3 The credential path already exists

| Element | Value | Source |
|---|---|---|
| Gateway hub role | `arn:aws:iam::360967146904:role/delegated/luminate-gateway-irsa` (DEV) | `values/values-dev.yaml` |
| Bedrock spoke role | `arn:aws:iam::131935619052:role/delegated/acp-gateway-xaccount` | `values/values-{dev,prod}.yaml` |
| Region | `ca-central-1` | same |
| Mechanism | pod-level `~/.aws/config`, `[profile base]` web identity → hub, `[profile chain]` → spoke | `helm/luminate-portal/templates/gateway/aws-config-configmap.yaml` |

This satisfies the D2's own hard constraints for a cloud-backed evaluator: **NFR-15** "No
service-account key file exists anywhere in the system. Production credentials are short-lived and
keyless" and **NFR-16** "A sidecar image is credential-free and identical across environments.
Only the runtime-injected identity differs." Our Bedrock path is already IRSA → STS.

Two gaps, both real and both small:

- **The permission is not granted.** The spoke role's inline policy is
  `bedrock:InvokeModel` + `bedrock:InvokeModelWithResponseStream` only
  (`acp-deploy/docs/cross-account-irsa-cloud-request.md`). The permission boundary caps the role
  at `bedrock:*`, so `bedrock:ApplyGuardrail` is *inside* the boundary but *not* granted. That is
  a cross-account cloud request of the same shape as the one already raised, not a new pattern.
- **The resources in that policy are written `us-east-1`** while `gateway.aws.region` is
  `ca-central-1`. Worth reconciling before anyone reasons about data residency for inspected
  content.

### 5.4 Availability — measured, and it corrects a standing assumption

```
$ AWS_PROFILE=t1k-agent-control-plane-dev-ca aws bedrock list-guardrails --region ca-central-1
{ "guardrails": [] }                                    # HTTP 200

$ AWS_PROFILE=t1k-agent-control-plane-dev-ca aws bedrock list-foundation-models --region ca-central-1
An error occurred (AccessDeniedException) ...
```

The Bedrock **Guardrails control plane responds in `ca-central-1`** from the ACP DEV account. That
is the residency answer for inspected content, and it is measured rather than read off a docs
page.

It also corrects a standing assumption carried in ACP notes that account `360967146904` has a
blanket SCP deny on `bedrock:*`. It does not — `ListGuardrails` succeeds while
`ListFoundationModels` is denied, so the deny is **action-scoped**. Anyone planning Bedrock work in
this account should re-probe the specific action rather than assume the whole namespace is closed.

### 5.5 Nothing on the ballot covers it

Ranked against the consortium ballot on 2026-09-11:

| Idea | Status | Relevance |
|---|---|---|
| ACPDIS-25 Content Guardrail Enforcement | **Delivery** | the feature itself — taken |
| ACPDIS-84 LLM Judge Guardrails | Discovery | **rankable, and §5.6 makes it the cheapest lever we have** |
| ACPDIS-98 Streaming Response Guardrails | Discovery | rankable, §4.3 |
| ACPDIS-97 Enterprise DLP Integration | Parking Lot | adjacent, not AWS |
| ACPDIS-95 Reversible PII Tokenization | Parking Lot | adjacent |
| ACPDIS-82 Reusable Guardrail Control Profiles | Parking Lot | adjacent |
| ACPDIS-99 Safety Control Effectiveness | Parking Lot | adjacent |
| **A non-GCP content-safety evaluator** | **absent** | — |

Per the ballot rules, an ask not in ACPDIS cannot be ranked at a Product Board round. So the
delivery vehicle for a new evaluator type is **a new ACPDIS idea**, not an AIC story. The draft is
carried at
[references/acpdis-idea-content-safety-evaluator.md](references/acpdis-idea-content-safety-evaluator.md)
for submission by the Sun Life representative.

### 5.6 The reframe: open source, in-cluster, is the stronger answer

Bedrock is a legitimate option, but it is **one of three**, and it is weakest on the axis that
raised the question. The full analysis is in [D2 §5](d2-design.md#5-phase-2-closing-the-content-safety-gap);
the discovery-level findings are:

- **Phase 1 already ships an open-source in-cluster evaluator.** Presidio is MIT and runs as a CPU
  sidecar inside the gateway pod. The gap is *category coverage*, not open-source-ness.
- **The integration seam is identical either way.** `guardrail_remote_endpoints` is keyed by
  `GuardrailType`, so a Bedrock evaluator and a self-hosted one are the same upstream change. The
  choice is about content custody, licence and operations — not integration.
- **Sun Life already owns the hard part of hosting one.** The SLM pipeline has GPU capacity via a
  Karpenter NodePool, a governed model-acquisition path (Artifactory mirror, digest pinning,
  **Sonatype licence gate**, fail-closed revocation) and measured serving economics.
- **Upstream's `llm_judge` routes through the gateway to a registered model deployment.** So a
  self-hosted safety model needs **no new evaluator type at all** — it needs ACPDIS-84 to rank,
  which is a vote rather than a contribution.
- **Licences were verified, not recalled**, and two well-known OSS guardrail libraries turned out to
  be archived. Only Granite Guardian among the frontier safety models carries a plain OSI licence;
  Llama Guard and ShieldGemma ship under bespoke community terms that Sun Life's existing gate
  would have to pass.

That last point has a measurable consequence for this discovery: from a Sun Life laptop,
`https://huggingface.co/api/models/...` returns **HTTP 403 with a Netskope block page**. That is not
a blocker to solve later — it is control C10 of the SLM pipeline working as designed ("Netskope
allows the HF domains only from Artifactory egress; EKS/users have no direct path"), and the
governed path around it already exists.

## 6. Scope

### 6.1 In scope

| Phase | Area | What |
|---|---|---|
| 1 | Deployment | Package the `pii-detector` sidecar into `helm/luminate-portal`, promote the image to SLF ECR, wire `GATEWAY_GUARDRAIL_*` through `gateway.config` |
| 1 | Posture | Set the fail-mode, streaming and timeout posture deliberately and record the reasoning |
| 1 | Controls | Author a first Sun Life control set — `banned_words` first, `pii_detection` second |
| 1 | Proof | Prove block, redact and warn end to end in DEV; measure the latency and TTFT cost |
| 1 | Evidence | Retention posture, and the activity surface as the evidence trail |
| 1 | Rollout | DEV → the four PROD-install gateways, warn-first then promote |
| 1 | Runbook | Incident, rollback and fail-closed-outage procedure (mirrors upstream AIC-713) |
| 2 | Content safety | Ballot idea for a non-GCP evaluator; evaluator bake-off; judge-latency measurement; Bedrock IAM spike |
| 2 | Contribution | If ranked, the upstream `content_safety` / `prompt_injection` evaluator type |

### 6.2 Out of scope

| Item | Reason |
|---|---|
| `llm_judge` **implementation** | Not built upstream. ACPDIS-84 is in Discovery — Sun Life's action is to **rank it**, not to build it |
| GCP Model Armor | Sun Life has no GCP path; `MODEL_ARMOR_ENABLED` stays `false` |
| Serving a safety model in production | Depends on the SLM pipeline ([EACPP-1069 et al.](../slm-pipeline/d3-tasks.md)). This spec consumes that capability, it does not rebuild it |
| Response scanning on MCP / A2A | Model-lane only upstream. Raise upstream if a use case needs it |
| Per-tool guardrail targeting | `AccessPolicyTargetType` has no tool member; the whole platform lacks per-tool authz |
| Removing the streaming exemption upstream | AIC-680 / AIC-717 are consortium decisions in flight |
| Sun Life control *content* (which words, which PII entities) | Owned by Privacy and Security, consumed here as configuration |

## 7. Constraints and assumptions

| # | Constraint | Evidence |
|---|---|---|
| C-1 | The gateway pod has no `extraContainers` hook in the SLF chart | `helm/luminate-portal/templates/gateway/deployment.yaml` — three containers, all hard-coded |
| C-2 | Gateway env is free-form | `templates/gateway/configmap.yaml` is `range .Values.gateway.config`, so settings are values-only |
| C-3 | Gatekeeper requires requests+limits on every container, including init | Previously observed to fail a ReplicaSet silently with only a `FailedCreate` event |
| C-4 | The PII sidecar carries a spaCy `en_core_web_lg` wheel | `services/pii-detector/Dockerfile` pins the URL and SHA256 — real memory footprint, and a Netskope-visible fetch at build time |
| C-5 | One sidecar per gateway pod, no cross-pod traffic | D2 NFR-8, generalising NFR-14. Cost scales with gateway replicas, not with traffic |
| C-6 | Sidecars are published to GHCR and need promoting to SLF ECR | `.github/workflows/docker-publish.yml` matrix includes `pii-detector` and `model-armor` |
| C-7 | Adding a guardrail *type* is a coordinated deploy | `GuardrailType` docstring: a gateway on an older `luminate_types` denies the request with `portal_invalid_guardrails` rather than ignoring the spec |
| C-8 | GPU capacity is a Karpenter NodePool **tainted `nvidia.com/gpu`**, which "cannot absorb CPU workloads" | [slm-pipeline D2](../slm-pipeline/d2-design.md). A GPU evaluator is therefore a poor gateway-pod sidecar — it would pin every gateway replica to a GPU node — so it belongs as a registry-managed model reached via `llm_judge` |
| C-9 | CPU generative inference is not viable | Measured by the SLM pipeline: **1.5 tok/s, ~11 min for a 1,508-token prompt**; the same prompt is 1.2 s on GPU |
| C-10 | HuggingFace is reachable only through Artifactory egress | SLM pipeline control C10, confirmed from a laptop: `huggingface.co` returns HTTP 403 with a Netskope block page |
| C-11 | Model licences are enforced, not advisory | SLM pipeline control C4 — the Sonatype firewall gate blocks download on "critical CVE, malware, or disallowed license"; approval needs `triaged` + `legal_reviewed` |
| A-1 | Sun Life stays on Keycloak JWT callers, not `lum_` API keys | `APP_AGENT_API_KEYS_ENABLED=false`; §3.4 confirms caller-side resolution still works |

## 8. Open questions

| # | Question | Owner | Blocks |
|---|---|---|---|
| Q-1 | Who owns the Sun Life control content — which terms, which PII entities, which thresholds? | Privacy / Security | D1 sign-off |
| Q-2 | Is `enforce` streaming acceptable in PROD, given the measured TTFT cost? | ACP Product + consuming teams | T12, PROD rollout |
| Q-3 | Should `guardrail_remote_fail_open` be `false` (deny on sidecar outage) for every environment, or `true` in DEV? | ACP Product | T6 |
| Q-4 | What retention window satisfies Sun Life record-keeping for evaluation rows? Upstream AIC-747 is the matching open decision | Privacy / Records | T14 |
| Q-5 | Do we contribute a self-hostable content-safety evaluator, rank ACPDIS-84 (`llm_judge`), or both? | Sun Life consortium rep | Phase 2 |
| Q-6 | Does inspected content leaving the gateway for Bedrock change the data classification of the traffic? (Options A and B make this question go away) | Security / Data Governance | Phase 2 route choice |
| Q-7 | Can a generative safety judge meet the 1.5 s evaluation ceiling on real Sun Life prompts? | ACP Platform | Option B viability |
| Q-8 | Is a safety model an ordinary Model Registry entry, or does an evaluator model need its own approval track? | Model Risk / Governance | T20 |
| Q-9 | Who operates and re-screens a self-hosted safety model over time — ACP Platform, or the SLM pipeline team? | ACP Product | Phase 2 ownership |

## 9. Success criteria

| # | Criterion |
|---|---|
| SC-1 | A deliberate, written fail-mode and streaming posture exists for every Sun Life gateway, and the running ConfigMaps match it |
| SC-2 | A `banned_words` control blocks a crafted request in DEV, and the block is visible in the guardrail activity surface |
| SC-3 | A `pii_detection` control redacts a crafted request in DEV, with the sidecar resolved — proven by the *absence* of `guardrail_evaluator_unresolved` in the evaluation rows |
| SC-4 | Guardrail evaluation latency and the response-path TTFT delta are measured, not estimated |
| SC-5 | CAP-10 in the capability map distinguishes platform capability from Sun Life deployment state |
| SC-6 | A runbook exists for a sidecar outage under a fail-closed posture |
| SC-7 | Phase 2 has a submitted ACPDIS idea and a measured evaluator comparison, or a recorded decision not to pursue it |
| SC-8 | The Phase 2 route is chosen on evidence — content custody, measured latency and verified licence — rather than on which vendor was asked about first |

## 10. Related

- [D1 — Requirements](d1-requirements.md) · [D2 — Design](d2-design.md) · [D3 — Tasks](d3-tasks.md)
- [ACP Capability Map — CAP-10](../../../capability-map.md#cap-10)
- [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
- [Sun Life Deployment of Luminate](../sunlife-deployment/d0-discovery.md)
- [Luminate Gateway & Environment Strategy](../gateway-environment-strategy/d0-discovery.md)
- Upstream design: `luminate-designs` → `docs/projects/luminate/02-architecture-and-design/designs/guardrails/`
