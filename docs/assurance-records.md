# ACP Assurance Records

Every architecture-governance (**ATG**), security-risk-assessment (**ISRA**) and
GenAI-assessment (**GBYD**) record raised for the Agentic Control Plane, in one place,
with the scope each one actually covers.

> **Generated** from `references/assurance-records.yaml` by
> `scripts/generate_assurance_register.py`. Do not hand-edit this page — edit the
> YAML and regenerate. CI fails if the two drift, and fails again if it finds an
> ATG, ISRA or GBYD identifier anywhere under `specs/` or `docs/` that is not declared.

**ServiceNow is the system of record for whether any of these is approved.**
Nothing here queries it. The *State* column is what this repository and Jira can
evidence, and every row says where that evidence came from. Treat a state older than
a few weeks as a question, not an answer.

## Why this page exists

The numbers were scattered: one spec puts them in `spec.yaml`, another in a pattern
header, another in a prose paragraph halfway down a design, and two exist only on
unmerged branches. Nothing validated any of it, so the only way to answer *what have we
got approved* was to grep. The discrepancies called out below were found by assembling
this page, not reported by anything.

## Needs confirming

3 records below carry a number and a programme, but **no recorded
assessed scope**. A number without a scope cannot be cited: there is no way to say
whether a given change falls inside it or outside it, which is the only question an
assurance record answers.

- **ATG0005454** — Supplied by Seth Chalmers on 2026-09-17, who confirmed it is for **Small Language Models / SLM**, with the ServiceNow link below. It appears in **no** repository, on no branch, and in no EACPP ticket — searched 2026-09-17.
- **26-1455** — Supplied by Seth Chalmers on 2026-09-17, who confirmed it is for **Small Language Models / SLM**, without a link. It appears in **no** repository, on no branch, and in no EACPP ticket — searched 2026-09-17.
- **26-1590** — Supplied by Seth Chalmers on 2026-09-17, who confirmed it is for **Small Language Models / SLM**, without a link. It appears in **no** repository, on no branch, and in no EACPP ticket — searched 2026-09-17.

ServiceNow holds the scope for each of these and is not reachable from this repository.
Someone with access needs to paste in the record title and its assessed scope, after
which they become ordinary rows.

Worth settling at the same time: **4 separate records now sit against
the one SLM programme**. That may well be correct — a mirror, a serving tier and a
generalized pipeline are different things to assess — but nothing records what
distinguishes them, so nobody can tell which one to cite for a given change.

## Outstanding actions

| Record | Action |
|---|---|
| `26-1260` | Submit the website unblock request. |
| `26-1260` | Reply to the Jira ticket to DevOps. |

## Summary

| Scope | ATG | ISRA | GenAI | State | Spec | Tracked in |
|---|---|---|---|---|---|---|
| [ACP platform](#acp-platform) | `ATG0005196` | [26-0739](https://sunlife.service-now.com/nav_to.do?uri=x_sulfc_vendor_ass_vendor_assessment.do%3Fsys_id=aa746aeb3b4cc310e9d4223eb3e45ae5) | — | Approved | `sunlife-deployment` | — |
| [Internal M2M identity provider](#internal-m2m-identity-provider) | [ATG0005518](https://sunlife.service-now.com/atg?id=ticket&table=x_sulfc_atg_request&sys_id=34e9753e2b06cb547c8ef5e2fe91bf7f&view=atg_controller_review) | [26-1565](http://sunlife.service-now.com/nav_to.do?uri=x_sulfc_vendor_ass_vendor_assessment.do%3Fsys_id=8b1cf13a2b46cb547c8ef5e2fe91bf79) | — | Approved | `sunlife-deployment` | [EACPP-747](https://sunlife.atlassian.net/browse/EACPP-747) |
| [Hugging Face website unblock (SLM mirror)](#hugging-face-website-unblock-slm-mirror) | — | [26-1260](https://sunlife.service-now.com/x_sulfc_vendor_ass_vendor_assessment.do?sys_id=8e57e3b033dd0b58e11ffe282e5c7b6c) | — | In review | `slm-pipeline` | [EACPP-559](https://sunlife.atlassian.net/browse/EACPP-559) |
| [SLM pipeline — ATG0005454](#slm-pipeline-atg0005454) | [ATG0005454](https://sunlife.service-now.com/atg?id=ticket&table=x_sulfc_atg_request&sys_id=17282d982bf983d0796bfbedec91bf52) | — | — | In review *(scope not recorded)* | `slm-pipeline` | — |
| [SLM pipeline — ISRA 26-1455](#slm-pipeline-isra-26-1455) | — | `26-1455` | — | In review *(scope not recorded)* | `slm-pipeline` | — |
| [SLM pipeline — ISRA 26-1590](#slm-pipeline-isra-26-1590) | — | `26-1590` | — | In review *(scope not recorded)* | `slm-pipeline` | — |
| [Agent patterns](#agent-patterns) | `ATG0005678` | `26-1956` | — | Drafting | `agent-patterns` *(branch)* | [EACPP-1290](https://sunlife.atlassian.net/browse/EACPP-1290) |
| [MCP server patterns](#mcp-server-patterns) | `ATG0005648` | `26-1904` | — | Drafting | `mcp-server-patterns` | [EACPP-1176](https://sunlife.atlassian.net/browse/EACPP-1176) |
| [Model inference patterns](#model-inference-patterns) | [ATG0005693](https://sunlife.service-now.com/nav_to.do?uri=x_sulfc_atg_request.do?sys_id=9f3f3f0acf978314a77ab1ad5d851c38) | [26-1978](https://sunlife.service-now.com/x_sulfc_vendor_ass_vendor_assessment.do?sys_id=61de005ecf9f8314a77ab1ad5d851c20) | [GBYD0001729](https://sunlife.service-now.com/x_sulfc_genai_gen_ai.do?sys_id=507078a2cf1bcb14a77ab1ad5d851c37) | Drafting | `model-inference-patterns` *(branch)* | [EACPP-1320](https://sunlife.atlassian.net/browse/EACPP-1320) |
| [Generalized SLM pipeline](#generalized-slm-pipeline) | — | — | — | Planned | `slm-pipeline` | [EACPP-568](https://sunlife.atlassian.net/browse/EACPP-568) |
| [Luminate gateways in their environment's workload account](#luminate-gateways-in-their-environments-workload-account) | — | — | — | Planned | `gateway-environment-strategy` | [EACPP-1089](https://sunlife.atlassian.net/browse/EACPP-1089) |

**States.** **Approved** — Governance has granted approval. The scope in `covers` is the approved scope. · **In review** — Submitted; awaiting a decision. · **Drafting** — A record number has been issued and the submission content is being written. · **Planned** — A record is known to be needed; nothing has been raised yet.

## Records

### ACP platform

| Field | Value |
|---|---|
| ATG | `ATG0005196` |
| ISRA | [26-0739](https://sunlife.service-now.com/nav_to.do?uri=x_sulfc_vendor_ass_vendor_assessment.do%3Fsys_id=aa746aeb3b4cc310e9d4223eb3e45ae5) |
| GenAI assessment | — |
| State | Approved |
| Spec | `sunlife-deployment` |

**Covers.** The platform and its supporting components — Luminate plus Langfuse, ClickHouse, Valkey and the rest of the deployed tier.

The broader of the two deployment approvals. DD-7 cites it explicitly for the Langfuse data tier, to stop that tier being argued under the narrower IdP approval.

Recorded in:

- `specs/platform/sunlife-deployment/d2-design.md`

### Internal M2M identity provider

| Field | Value |
|---|---|
| ATG | [ATG0005518](https://sunlife.service-now.com/atg?id=ticket&table=x_sulfc_atg_request&sys_id=34e9753e2b06cb547c8ef5e2fe91bf7f&view=atg_controller_review) |
| ISRA | [26-1565](http://sunlife.service-now.com/nav_to.do?uri=x_sulfc_vendor_ass_vendor_assessment.do%3Fsys_id=8b1cf13a2b46cb547c8ef5e2fe91bf79) |
| GenAI assessment | — |
| State | Approved |
| Spec | `sunlife-deployment` |
| Jira | [EACPP-747](https://sunlife.atlassian.net/browse/EACPP-747) |

**Covers.** Keycloak / Authentik as the M2M issuer for the Luminate workload. Deliberately narrow: agentic M2M for this workload only — explicitly not an enterprise IdP, and not edge-exposed. Widening that scope is a new governance conversation.

ETAB presented and approval granted; recorded in the spec on 2026-08-28 (commit `70ab0dbd`, EACPP-596). **The Jira tickets were never closed** — EACPP-747 is Implementing and its two children EACPP-748 (ATG review) and EACPP-749 (ISRA assessment) are In Analysis, all last touched 2026-07-20 and still worded "in progress". The spec is the newer source; the tickets are stale and need closing.

Recorded in:

- `specs/platform/sunlife-deployment/d1-requirements.md`
- `specs/platform/sunlife-deployment/d2-design.md`
- `specs/platform/sunlife-deployment/d3-tasks.md`

### Hugging Face website unblock (SLM mirror)

| Field | Value |
|---|---|
| ATG | — |
| ISRA | [26-1260](https://sunlife.service-now.com/x_sulfc_vendor_ass_vendor_assessment.do?sys_id=8e57e3b033dd0b58e11ffe282e5c7b6c) |
| GenAI assessment | — |
| Risk | `R011092` (Low) |
| State | In review |
| Spec | `slm-pipeline` |
| Jira | [EACPP-559](https://sunlife.atlassian.net/browse/EACPP-559) |

**Covers.** Egress to huggingface.co for the small-language-model pipeline. The action plan replaces the requested broad browser unblock with a read-only, scanned Artifactory pull-through mirror scoped to a single server.

**Open, with two actions outstanding.** The ServiceNow link is a row in a queue filtered to `status != Cancelled` and `status != Completed`, so the record was neither closed nor cancelled when that link was produced. Against that, the action plan in the repo is dated 2026-06-17, still says *Draft for ISA review*, and still carries **4 unfilled `<FILL:>` placeholders** including the risk owner and the target date — while EACPP-559 (ISRA support + Netskope unblock) is marked **Done**. The Jira ticket is the one that looks wrong. EACPP-571 records that this ISRA was rated **Medium** at submission for an insufficiently defined control posture.

Recorded in:

- `specs/platform/slm-pipeline/artifacts/isra-r011092-action-plan.md`

### SLM pipeline — ATG0005454

| Field | Value |
|---|---|
| ATG | [ATG0005454](https://sunlife.service-now.com/atg?id=ticket&table=x_sulfc_atg_request&sys_id=17282d982bf983d0796bfbedec91bf52) |
| ISRA | — |
| GenAI assessment | — |
| State | In review |
| Spec | `slm-pipeline` |

**Covers.** 

The programme is confirmed; what this record **assesses** is not. Whether it pairs with 26-1455, with 26-1590, or stands alone is unestablished, so it is listed as its own row rather than merged into one.

### SLM pipeline — ISRA 26-1455

| Field | Value |
|---|---|
| ATG | — |
| ISRA | `26-1455` |
| GenAI assessment | — |
| State | In review |
| Spec | `slm-pipeline` |

**Covers.** 

### SLM pipeline — ISRA 26-1590

| Field | Value |
|---|---|
| ATG | — |
| ISRA | `26-1590` |
| GenAI assessment | — |
| State | In review |
| Spec | `slm-pipeline` |

**Covers.** 

### Agent patterns

| Field | Value |
|---|---|
| ATG | `ATG0005678` |
| ISRA | `26-1956` |
| GenAI assessment | — |
| State | Drafting |
| Spec | `agent-patterns` |
| Branch | `spec/agent-patterns` — **not on `main`** |
| Jira | [EACPP-1290](https://sunlife.atlassian.net/browse/EACPP-1290) |

**Covers.** The four specified substrates plus the SUB-E / SUB-I admission criteria. A platform admitted against those criteria is in assessed scope; changing the criteria is a change to the assessed scope.

Numbers issued; controls C-1–C-35 and residual risks R-1–R-12 written. The spec is **not on `main`** — it is D3 draft on an open pull request, so these numbers are invisible to anyone reading the default branch.

Recorded in:

- `specs/pattern/agent-patterns/spec.yaml`
- `specs/pattern/agent-patterns/pattern.md`
- `specs/pattern/agent-patterns/d2-design/assurance.md`

### MCP server patterns

| Field | Value |
|---|---|
| ATG | `ATG0005648` |
| ISRA | `26-1904` |
| GenAI assessment | — |
| State | Drafting |
| Spec | `mcp-server-patterns` |
| Jira | [EACPP-1176](https://sunlife.atlassian.net/browse/EACPP-1176) |

**Covers.** The substrate list in the pattern's Hosting page, quoted verbatim under *What ETAB is being asked to approve*. A change to that list is a change to the assessed scope.

Numbers issued and the submission content is written — controls C-1–C-25 and residual risks R-1–R-8 in `d2-design/assurance.md`. The two tasks that turn it into an actual submission, EACPP-1274 (ETAB pack) and EACPP-1275 (control set with evidence), are both still in **Funnel**.

Recorded in:

- `specs/pattern/mcp-server-patterns/spec.yaml`
- `specs/pattern/mcp-server-patterns/pattern.md`
- `specs/pattern/mcp-server-patterns/d2-design/assurance.md`

### Model inference patterns

| Field | Value |
|---|---|
| ATG | [ATG0005693](https://sunlife.service-now.com/nav_to.do?uri=x_sulfc_atg_request.do?sys_id=9f3f3f0acf978314a77ab1ad5d851c38) |
| ISRA | [26-1978](https://sunlife.service-now.com/x_sulfc_vendor_ass_vendor_assessment.do?sys_id=61de005ecf9f8314a77ab1ad5d851c20) |
| GenAI assessment | [GBYD0001729](https://sunlife.service-now.com/x_sulfc_genai_gen_ai.do?sys_id=507078a2cf1bcb14a77ab1ad5d851c37) |
| State | Drafting |
| Spec | `model-inference-patterns` |
| Branch | `spec/model-inference-patterns` — **not on `main`** |
| Jira | [EACPP-1320](https://sunlife.atlassian.net/browse/EACPP-1320) |

**Covers.** Centralized inference as specified in the pattern — cost attribution and model access governance.

The most completely recorded of the set, and the shape the others should copy: an ATG, an ISRA **and** a GenAI assessment, with the ServiceNow URLs carried in `spec.yaml` (`atg_url` / `isra_url`) rather than only the bare numbers. **GBYD0001729 is not yet in `spec.yaml`** — it was supplied directly on 2026-09-17 and should be added alongside the other two. The spec itself is **not on `main`**; D3 draft on an open pull request.

Recorded in:

- `specs/pattern/model-inference-patterns/spec.yaml`
- `specs/pattern/model-inference-patterns/pattern.md`
- `specs/pattern/model-inference-patterns/d2-design/assurance.md`

### Generalized SLM pipeline

| Field | Value |
|---|---|
| ATG | — |
| ISRA | — |
| GenAI assessment | — |
| State | Planned |
| Spec | `slm-pipeline` |
| Jira | [EACPP-568](https://sunlife.atlassian.net/browse/EACPP-568) |

**Covers.** The generalized pipeline rather than the single Hugging Face mirror already covered by ISRA 26-1260.

EACPP-568 (*Generalized-pipeline ISRA + ATG submission package*) is in **Funnel**. No ATG or ISRA number has been raised. Listed so the gap is visible rather than discovered at submission time.

### Luminate gateways in their environment's workload account

| Field | Value |
|---|---|
| ATG | — |
| ISRA | — |
| GenAI assessment | — |
| State | Planned |
| Spec | `gateway-environment-strategy` |
| Jira | [EACPP-1089](https://sunlife.atlassian.net/browse/EACPP-1089) |

**Covers.** One production Luminate control plane governing DEV, SIT, STAGE and PROD gateways that run in the dev, test, stage and prod workload accounts in each serving region (today ca-central-1 and us-east-1, with a procedure for adding regions), and the content-free control link from each gateway to the control plane (IPNSD section 2.3). A delta on the ACP platform baseline (ATG0005196).

Agreed in the Luminate Gateway Environment Deployment Model session on 2026-10-06. No ATG or ISRA number has been raised; the package is the spec's Assurance page (D3 T34 and T35). May need a Security Exception if the control link is not accepted under section 2.3.

Recorded in:

- `specs/platform/gateway-environment-strategy/d2-design/assurance.md`

## Related records

Not assurance submissions, listed so nobody re-derives them from a spec footnote.

| Record | Kind | What | Recorded in |
|---|---|---|---|
| `APM0006505` | APM | The APM record for ACP. | `specs/platform/sunlife-deployment/d2-design.md` |
| `APM0004443` | APM | The previous APM record for ACP, replaced by APM0006505. Some AWS resource tags still carry it; re-tag them rather than treat it as a second record. | `specs/platform/sunlife-deployment/d2-design.md` |
| `CHG0547049` | ServiceNow change | PROD RDS provisioning — four dedicated instances (luminate, keycloak, authentik, langfuse). Paired with DMS request DMS-178186. | `specs/platform/sunlife-deployment/d3-tasks.md` |

ServiceNow **RITM** provisioning requests are deliberately out of scope. They are
requests for infrastructure, not assessments of it; they live in
`luminate-sunlife-deploy` alongside the thing they provisioned.

## Adding a record

1. Declare it in `references/assurance-records.yaml`.
2. Put `atg_reference`, `atg_url`, `isra_reference`, `isra_url` and, where one exists,
   the GenAI assessment, in the spec's `spec.yaml`. `model-inference-patterns` is the
   reference shape — it is the only spec carrying the ServiceNow URLs, which is what
   makes a number checkable rather than merely quotable.
3. Regenerate: `python3 scripts/generate_assurance_register.py`.
4. Commit both the YAML and this page.

A pattern spec additionally carries the pair in its `pattern.md` header and in the
`| Record | Identifier |` table at the top of `d2-design/assurance.md`. Those are
reader-facing; the YAML is the one CI checks.
