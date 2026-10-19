# NOVA & ACP Integration — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: [EACPP-895](https://sunlife.atlassian.net/browse/EACPP-895)

**Artefacts inspected**: Nova `IDP/idp_backstage` and `IDP/idp-backstage-sunlife-system-model`
(Bitbucket `main`, 2026-09-04) · `ENTARCH/marketplace-plugins` + `ENTARCH/marketplace-git-plugin`
(Bitbucket `main`, 2026-09-04) · `luminate` `origin/main` `31f908e90` · `luminate-designs`
`origin/main` `66970a4` and branch `d1/skills-registry` `b0085f1`.

**Published specifications referenced** (not "verified" — cited): Agent Plugins v1.0.0 · Agent
Skills specification · `claude-code-marketplace.json` and `claude-code-plugin-manifest.json`
JSON Schemas (schemastore) · OWASP Agentic Skills Top 10 skill-scanner-integration.

---

## 0. What changed since D0

D0 was written on 2026-08-10 from a discovery conversation. Five of its framing assumptions
do not survive contact with the two systems as they actually exist. This section states the
corrections up front because every requirement below depends on them.

| # | D0 said | Verified position | Consequence |
|---|---|---|---|
| C-1 | "NOVA (internal development platform)" — an unspecified system with an API we would design | Nova is **Backstage**. "Nova Build Hub is our internal developer portal built on Backstage" — Confluence [113078141303](https://sunlife.atlassian.net/wiki/spaces/GDEP/pages/113078141303), GDEP, 2026-08-03. Repo `IDP/idp_backstage`, built by EI Cloud Automation Hub, onboarding run by the InnerVerse team | The integration primitive is **not** a bespoke API. It is a Backstage `EntityProvider`, a pattern Nova already runs for the API Platform. We implement against an existing seam rather than negotiating a new one |
| C-2 | Direction is Nova → ACP: "register agents from NOVA into ACP" | Greg Ohannessian's 2026-09-03 note puts the **pull** direction first: "have Nova help populate this list via a provider that pulls in Data from ACP (similar to API platform APIs)" | Both directions are in scope, but they carry **different payloads** and must not both write the same fields. See [§4](#4-the-two-decisions-that-shape-everything-else) |
| C-3 | Centre of gravity is MicroVM observability of coding agents | The live ask has moved to the **plugin and skill supply chain**: which plugins exist, what is inside them, whether they were scanned, and which harnesses may install them | MicroVM observability is retained but demoted. It is [FR-13](#fr-13-microvm-and-harness-session-telemetry-deferred-with-a-stated-condition), explicitly deferred with a stated re-entry condition, not deleted |
| C-4 | "IDP agent catalogue sync" is **out of scope / backlog** (D0, and both [EACPP-895](https://sunlife.atlassian.net/browse/EACPP-895) and [CDSP-390](https://sunlife.atlassian.net/browse/CDSP-390)) | Catalogue sync **is** the integration. It is what Greg's provider does | D0's in/out-of-scope lists invert. This D1 supersedes them |
| C-5 | Header says "Epic: CDSP-390"; `spec.yaml` says `EACPP-895` | Both exist. EACPP-895 (Funnel) *duplicates* [EACPP-850](https://sunlife.atlassian.net/browse/EACPP-850), which is **Rejected**. CDSP-390 (Backlog) is the Nova-side twin. Neither has an assignee | EACPP-895 is the spec epic; CDSP-390 is the counterpart, not a second source of truth. Correct the D0 header. Confirm with Pavithra whether EACPP-850's rejection was a de-duplication or a decision |

Two D0 claims are **unevidenced** and are not carried forward: cross-region agent
discovery/failover, and the "1000 agents/day" load figure used to justify a caching strategy.
Neither has a source. If either matters, it needs a number from the Nova team first.

---

## 1. What Nova is today — verified

| Fact | Value | Where verified |
|---|---|---|
| What it is | Backstage (upstream, not RHDH), branded **Nova Build Hub**, `https://nova-buildhub.sunlifecorp.com/` | Confluence 113078141303; repo `IDP/idp_backstage` |
| Who owns it | EI Cloud Automation Hub builds it; InnerVerse runs onboarding (Confluence space `DA`, Jira project `DA`) | Repo description; Confluence 112766386303 |
| Entity kinds allowed | `Component, API, Resource, System, Domain, Location, Template` (+ `User`, `Group` via locations) | `app-config.yaml` → `catalog.rules` |
| Approved component types | 16, as catalog entities of `kind: Resource`, `spec.type: catalog-component-type` — including **`agent`**, **`ai-skills`**, **`plugin`**, `genai`, `service`, `data-product` | `IDP/idp-backstage-sunlife-system-model` |
| `agent` type annotations | required `sunlife.com/apm-number`, `sunlife.com/agent-framework`, `sunlife.com/agentic`; optional `sunlife.com/is-pool-agent` | same |
| `ai-skills` type annotations | required `sunlife.com/apm-number` **and** `sunlife.com/skill-type`; optional `sunlife.com/skill-model` | same |
| `plugin` type annotations | required `sunlife.com/apm-number`, `sunlife.com/plugin-type`, `sunlife.com/plugin-platform` | same |
| AI Catalog | Ships today — `IDP/idp-backstage-plugin-slf-ai-catalog-frontend`, page "AI Catalog" / "Browse Nova projects, agents, and skills", three tabs | `backstage/packages/app/src/components/ai-catalog/` |
| Repo discovery | `novaTools` provider, 30-minute schedule, DB-backed repo registry (`nova_tools_repos`), REST `/api/catalog-providers/nova-tools/repos`, admin UI under Settings → Catalog Providers | `idp_backstage` |
| Repo discovery **format** | Directory-convention YAML: `agents/*.yaml`, `skills/*.yaml`, `projects/*.yaml` (seed repo `SLCC/vscode-cloud-agents`) | same |
| Existing provider pattern | `APICatalogProvider implements EntityProvider`, config `catalog.providers.catalog-providers.apicatalog`, `cron: '0 */6 * * *'`, timeout 30m, `applyMutation({type:'full'})`, emits `kind: API` **and** `kind: Group`, annotates `sunlife.com/provider`, `sunlife.com/source-api`, `sunlife.com/api-id`, `sunlife.com/current-version`, `sunlife.com/all-versions` | `backend-catalog-providers/src/api-providers/apiCatalogEntityProvider.ts` |
| Nova's own agent runtime | `langgraphServiceUrl: https://nova-agentgateway.sunlifecorp.com`; Backstage actions exposed as MCP via `mcpActions: {name: 'Nova Backstage'}` | prod `app-config` |

Three consequences follow directly.

**Nova already has the entity types.** `agent`, `ai-skills` and `plugin` are approved
component types today. This integration does not need Nova to invent a data model; it needs
Nova to be given rows and ACP to be given the parts Nova cannot hold.

**But there are two parallel models, and a provider must target one.** The approved model
uses `spec.type: ai-skills` in the default namespace. The shipped AI Catalog frontend does
something else: `useNovaEntities.ts` filters `metadata.namespace === 'nova-tools'` and
partitions on `spec.type ∈ project | agent | skill` (singular `skill`), keyed on annotation
`nova-buildhub.sunlifecorp.com/team`. An ACP provider that emits `ai-skills` in the default
namespace will validate against the approved model and **not appear in the AI Catalog**.
This is [Q-1](#open-questions) and it is the first thing to settle in the meeting.

**And the approved types require an APM number.** `agent`, `ai-skills` and `plugin` all require
`sunlife.com/apm-number`. An ACP-originated entity does not have one unless Nova supplied it at
registration, so "project plugin entities into Nova" is not simply a provider change — it needs
an APM answer or a change request against `idp-backstage-sunlife-system-model`, which
[§11](#11-constraints-and-assumptions) puts outside this spec's authority. Folded into
[Q-4](#open-questions).

**Nova runs an agent gateway.** `nova-agentgateway.sunlifecorp.com` and Nova-Backstage-as-MCP
overlap ACP's remit directly. This D1 takes no position on that overlap beyond requiring it be
named ([FR-14](#fr-14-state-the-runtime-delineation-in-writing)); leaving it unstated is how
two control planes end up governing the same traffic.

**`marketplace.json` is not part of Nova today.** Not in `idp_backstage`, not in the seed repo,
and Confluence full-text has no substantive hit. Greg's plugin-discovery idea is a **proposed
change to Nova**, not a description of current behaviour. Any requirement that assumes Nova
reads `marketplace.json` is a requirement **on the Nova team**, and is marked as such below.

---

## 2. What the plugin marketplace is today — verified

`ENTARCH/marketplace-plugins` carries two index files —
`.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` — listing four plugins
sourced from `ENTARCH/marketplace-git-plugin` (`git-subdir`) and npm
(`@sunlife/agentic-gatekeeper`). Clients consume it via the VS Code setting
`chat.plugins.marketplaces` or `claude plugins marketplace add`.

**It is explicitly a demonstration** — the index declares `"name": "sample-marketplace"`,
`"owner": "sample-maintainer"`, and the README says it *"demonstrates two source patterns"* with
*"Example fields: `url`, `path`"*. Nothing below is a criticism of a demo doing its job. It is
the list of what changes between "this proves plugins work at Sun Life" and "this is a governed
distribution channel", and it is worth writing down now precisely because the demo is good
enough to get adopted as-is.

| ID | Finding | Why it matters |
|---|---|---|
| **M-1** | `git-subdir` entries carry `url` + `path` only. The schema defines **two** further fields: `ref` (*"Git branch or tag… Defaults to the default branch"*) and `sha` (*"Specific commit SHA"*, `^[a-f0-9]{40}$`). Neither is used. The npm entry does pin `1.0.1-20260804.112442` | Unpinned, a git-sourced plugin resolves to **whatever the default branch says at install time**. Two developers installing "the same" plugin a week apart can get different instructions and different code. Every downstream control — review, approval, attestation, recall — is a statement about bytes; without a pin they are statements about a name. One field per entry |
| **M-2** | Up to **three** manifest copies per plugin (`plugin.json`, `.claude-plugin/plugin.json`, `.github/plugin/plugin.json`) and **two** marketplace indexes, synchronised by hand — the README says *"Keep both marketplace files in sync when adding or updating plugins"* | The two indexes are **not** duplicates and cannot be byte-identical: `.claude-plugin` uses `https://…/scm/entarch/…` and `.github/plugin` uses `ssh://git@…`. That is a real difference maintained by hand across five files. Drift here means *a plugin approved under one harness is not the artefact installed under another*, which voids the approval silently |
| **M-3** | Manifest schemas diverge, and **none of the three git-sourced plugins would load under Agent Plugins v1**. `plugin-docs-basics` and `plugin-governance-suite` have **no root `plugin.json`** (v1 §5.1 requires one) and no `$schema` (v1 §5.3, required — fatal). `switchboard-lite` has a root manifest but declares `"$schema": "…/claude-code-plugin-manifest.json"`, which is not a recognised Agent Plugins identifier — v1 §5.2 requires the client to **reject** it. Unknown top-level fields (`agents`, `skills`, `id`, `targets`, `requiredSkills`) are **not** the cause: v1 §5.2 and §11.3 make those non-fatal, to be *reported and ignored* | "We will use the plugin standard" is not yet a decision — see [§4.2](#42-which-plugin-standard). And the fix list is three plugins, not two |
| **M-4** | Plugins ship **executable code**: `switchboard-lite/agents/tools/{azure_ad,bitbucket,cdd_generator,code_review,pipeline,dsl_provider}.py` | Installing a plugin is installing code, not just prose. SAST/SCA is not optional and is not covered by a skill scanner. Both plugin standards state manifest `env`/`headers` are visible package data and **must not** carry secrets — worth a specific look at `azure_ad_tool.py` |
| **M-5** | Skill frontmatter drifts from the Agent Skills spec — **in the production-derived plugin, not the samples**. `switchboard-lite/skills/api-platform/SKILL.md` has only `description`: no `name`, which the spec requires and requires to match the parent directory. `switchboard-lite/skills/ai-dlc/SKILL.md` carries `argument-hint`, which the spec does not define. Both sample plugins' `SKILL.md` files are fully conformant | Both plugin standards defer to Agent Skills for skill content, and a conformant client is required to **skip** a non-conformant skill — silently. A governance record for a skill the harness never loaded is worse than no record |
| **M-6** | `@sunlife/agentic-gatekeeper` — "policy checks, telemetry, session notices" — is distributed **as a plugin**, and the README notes Copilot CLI *"does not yet support npm plugin package sources the same way VS Code and Claude Code do"* | The control is installed by the same mechanism it governs, and is not uniformly installable across harnesses. A control a developer can decline to install is a default, not a control. Re-sourcing it as `git-subdir` removes the CLI limitation |
| **M-7** | **The index is itself an execution surface, and it is unpinned.** The marketplace schema lets a *plugin entry* carry, inline in the index: `hooks`, `mcpServers`, `lspServers`, `commands`, `settings`, `dependencies`, and `monitors` — the last documented as *"Background watch scripts the host arms as persistent Monitor tasks (**unsandboxed, same trust tier as hooks**)"*. `strict: false` means *"the marketplace entry provides the manifest"*, bypassing the plugin folder entirely. Top-level `allowCrossMarketplaceDependenciesOn` permits auto-install from another marketplace. Meanwhile the README's documented consumption path is `…/marketplace-plugins.git#main` — **a branch tip, re-read on every resolution** | This is the most serious finding in the section. One merge to `main` of `marketplace-plugins` places unsandboxed commands on every configured developer workstation **without touching any plugin repo, without any component digest changing, and without a scan gate ever seeing a plugin.** Pinning plugin sources ([FR-5](#fr-5-pin-every-marketplace-source-and-the-index-itself-immutably)) does nothing about it. The index needs its own controls |

Every one of these is cheap to fix now and expensive to fix after adoption.

---

## 3. What ACP can hold today — verified

| Thing | Status in ACP / Luminate | Evidence |
|---|---|---|
| Agent record, lifecycle, ownership | ✅ Available | [CAP-01](../../../capability-map.md#cap-01) |
| MCP server / tool registry | ✅ Available | [CAP-03](../../../capability-map.md#cap-03) |
| Model registry | ✅ Available | [CAP-02](../../../capability-map.md#cap-02) |
| Approval workflow | 🟡 Partial — single-step, no SoD | [CAP-14](../../../capability-map.md#cap-14) |
| Audit trail | 🟡 Partial | [CAP-18](../../../capability-map.md#cap-18) |
| **Skill entity** | ❌ **Nothing.** No `skills` app under `backend/app/`. `git grep -il '\bskill' -- backend/ gateway/ frontend/ packages/` on `origin/main` returns **3 files**, all `THIRD_PARTY_NOTICES.md` — dependency licence text, no implementation | `luminate` `31f908e90` |
| **Plugin / bundle entity** | ❌ Nothing | same |
| **Version pinning, provenance, recall** | ❌ Nothing | same |
| Skills Registry **design** | 📐 Draft D1 only — `luminate-designs` branch `d1/skills-registry`, PR [#106](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/106) **(draft)**, Andrew Culberson (TELUS), 2026-07-14, *Status: Draft, Decision: Pending* | `b0085f1` |
| API Resources **design** (its lockstep dependency) | 📐 Draft D1 only — PR [#105](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/105) **(draft)** | `36b9d71` |

**The load-bearing sentence of this D1**: *ACP cannot store a plugin or a skill today, and the
design that would let it is an unmerged draft whose own dependency is also an unmerged draft.*

Every requirement below is therefore written to be **true on both sides of that decision** —
deliverable now against artefacts we control, and a strict subset of the Skills Registry if and
when it lands. Nothing here is blocked on PR #106, and nothing here has to be thrown away if
PR #106 is approved.

---

## 4. The two decisions that shape everything else

### 4.1 Plugin or skill — which is the unit of governance?

Greg: *"skills on their own are too granular, and the coding harnesses don't have controls at
the skill level, they are all at the plugin level (e.g. which marketplaces are allowed to be
used, and marketplaces only list plugins)."*

The TELUS Skills Registry D1 models the **skill version** as the governed entity — immutable,
integrity-pinned, individually reviewed, individually recallable — and does not model a bundle
above it.

Both are right about different things, and the disagreement mostly dissolves once it is noticed
that they are scoped to **different runtimes**.

The Skills Registry is scoped to **Luminate-governed agents**, where it has a real enforcement
path: adoption is pinned per agent, bundles are fetched from Luminate at load time, and the
Gateway's default-deny denies anything a skill's instructions attempt beyond the agent's grants.
A skill-level control point exists there. It just is not on a laptop.

Greg is describing **developer-workstation coding harnesses**, where no such path exists. The
harness has one lever and it is the marketplace/plugin allowlist.

| | Plugin | Skill |
|---|---|---|
| What it is | The unit of **distribution and installation** | The unit of **behaviour and risk** |
| Enforcement point in a **coding harness** | Marketplace allowlist, plugin install allow/deny. The only lever Copilot and Claude Code expose | **None.** No coding harness has a skill-level control |
| Enforcement point for a **Luminate-governed agent** | Not modelled today | Adoption pinning + Gateway default-deny (Skills Registry D1) |
| What the risk literature addresses | SCA/SAST on bundled code | OWASP AST01–AST10; NVIDIA SkillSpector scores and SARIF **per skill file** |
| Approval question it answers | "May this be installed here?" | "What does this make an agent do, and was that reviewed?" |

**Requirement**: for the coding-harness case, govern the **plugin** as the unit of distribution,
approval and entitlement, and inventory the **skill** as the unit of risk, review evidence and
recall. One record type with a parent/child relation, not two competing registries. Greg's own
note leaves the door open — *"we could identify the skills inside a plugin if needed"*. This
makes that the design.

The practical consequence, and it is a limitation rather than a feature: **in a coding harness a
recall is authored at the skill level and can only be enforced at the plugin level.** Pulling one
poisoned skill means republishing the marketplace index without the plugin versions that contain
it, which prevents new installs and flags nothing on an already-provisioned workstation. The
Skills Registry's own recall reaches further within its runtime, because adoption is pinned and
distribution is served. Neither mechanism substitutes for the other.

### 4.2 Which plugin standard?

Two candidates are in play and the demo repo currently straddles both.

| | Claude Code plugin manifest | Agent Plugins v1.0.0 |
|---|---|---|
| Manifest | `.claude-plugin/plugin.json`, open-ish; the demo also uses root `plugin.json` and `.github/plugin/plugin.json` | Root `plugin.json` only, **closed schema**, `$schema` + `name` required |
| Components | `skills[]`, `agents[]`, hooks, MCP, commands — declared in the manifest | **Skills and MCP servers only.** Discovered from fixed locations `skills/` and `mcp.json`; the manifest cannot list or override them |
| Agent definitions | First-class | **Out of v1** — "too client-specific for a stable portable contract" |
| Marketplace / index | `marketplace.json`, schemastore-schema'd | **Not defined.** v1 is silent on distribution, installation and permissions |
| Governance | Nothing defined | Nothing defined |

Neither standard defines a marketplace with integrity pinning, an approval state, or a scan
attestation. Agent Plugins v1 does not even define a marketplace. **So the governance metadata
has to live somewhere non-standard regardless.** For skills there is a partial home — the Agent
Skills spec defines an optional `metadata` string map for exactly this — but it is per-skill and
carries no authority. For plugins the choice is an `extensions["com.sunlife.acp"]` namespace
(which Agent Plugins v1 explicitly reserves for client-specific data) or a sidecar store.

**Requirement**: target Agent Plugins v1 as the **portable floor** and carry Sun Life governance
metadata under the reverse-domain extension namespace `com.sunlife.acp`, with the Claude Code
manifest retained as a client-specific superset for the `agents[]` that v1 does not cover.
This is the only option that (a) survives a client switching to a v1-conformant loader, (b) does
not fork the manifest, and (c) has a spec-sanctioned home for governance fields.

**With one hard constraint**: anything a plugin ships can *claim* anything. The manifest block is
a **non-authoritative mirror for display and tooling convenience only**. The authoritative record
is the attestation store, and no tool may read an approval decision out of a plugin's own
manifest — see [D2 DD-4](d2-design.md#2-design-decisions).

---

## 5. User stories

### US-1: One list of agents, wherever I start

**As a** Sun Life developer,
**I want** the agents I can see in Nova's AI Catalog to be the same agents ACP governs, with
their governance state visible,
**So that** I do not have to know which portal is authoritative for which fact.

**Acceptance Criteria**:
- [ ] **Given** an agent registered in ACP, **When** the Nova provider next runs, **Then** it appears in Nova's AI Catalog with its ACP governance state and a deep link back to ACP
- [ ] **Given** an agent whose ACP approval is revoked, **When** the provider next runs, **Then** Nova reflects the revoked state within one provider interval, and the entity is not silently deleted
- [ ] **Given** an agent discovered by Nova from source but never registered in ACP, **When** a developer opens it, **Then** Nova shows it as **unregistered** rather than omitting it — the gap is the point

### US-2: Install only what has been through the gate

**As a** developer using Copilot or Claude Code,
**I want** the Sun Life marketplace to list only plugin versions that passed scanning and
approval,
**So that** "it was in the corporate marketplace" is a defensible statement.

**Acceptance Criteria**:
- [ ] **Given** a plugin version whose scan produced an unwaived critical finding, **When** the marketplace index is published, **Then** that version is absent from the index
- [ ] **Given** an approved plugin version, **When** a developer installs it, **Then** the bytes they receive are the bytes that were scanned, established by an immutable source pin
- [ ] **Given** a plugin version later withdrawn, **When** the index is republished, **Then** it is absent — preventing new installs. Existing installs are **not** reached; see [FR-10](#fr-10-withdraw-a-version-and-state-the-limit-of-that-reach)

### US-3: Know what is inside a plugin

**As a** security reviewer,
**I want** each plugin version's skills, agent definitions, MCP servers and bundled code
enumerated with per-file digests,
**So that** I review an artefact rather than a name.

**Acceptance Criteria**:
- [ ] **Given** a plugin version, **When** I open its record, **Then** I see every `SKILL.md`, every reference and asset file a skill can progressively load, every declared agent file, every `mcp.json` entry and every bundled script, each with a SHA-256
- [ ] **Given** a skill that declares `allowed-tools`, **When** the publication gate runs, **Then** the version is held for **blocking human review** — the Agent Skills spec defines the field as tools *"pre-approved to run"*, so it removes a confirmation prompt in any client that implements it. It is a privilege-elevating declaration, not a description
- [ ] **Given** an `mcp.json` entry or a marketplace-entry `mcpServers`/`channels` block naming a remote server, **When** I open the record, **Then** I see whether that server is registered in ACP ([CAP-03](../../../capability-map.md#cap-03)) and, if not, that it is ungoverned egress

### US-4: One authoritative answer per field

**As an** ACP governance lead,
**I want** each field to have exactly one system of record,
**So that** Nova and ACP cannot disagree about the same fact.

**Acceptance Criteria**:
- [ ] **Given** the field ownership table in [FR-2](#fr-2-split-the-system-of-record-by-field-not-by-entity), **When** either side writes a field it does not own, **Then** the write is rejected or reconciled on the next sync, never silently merged
- [ ] **Given** ACP-owned fields projected into Nova, **When** a user edits them in Nova, **Then** either the field is read-only or the edit is round-tripped to ACP — not both

### US-5: Prove it to an examiner

**As a** compliance officer,
**I want** to show, for any **published** plugin version, who approved it, what scanned it, what
it contained and when it was withdrawn,
**So that** the agent-instruction supply chain is evidenced like any other dependency.

**Acceptance Criteria**:
- [ ] **Given** any published plugin version, **When** I request its evidence record, **Then** I get the source pin, the scan report reference and verdict, any waiver and its approver, the approver identity and timestamp, the component inventory with digests, and the lifecycle history
- [ ] **Given** a withdrawn version, **When** I request its evidence record, **Then** the record persists — withdrawal never deletes evidence

> **Scope limit, stated deliberately.** This evidences what was **published**, not what is
> **installed**. No installed-base inventory exists: there is no installation-recording
> mechanism in Phases 0–1, the only plausible source is the gatekeeper plugin, and
> [FR-12](#fr-12-do-not-claim-per-skill-runtime-enforcement) plus
> [Q-6](#open-questions) explain why that is not yet a control. A statement of the form
> *"no developer machine is running a withdrawn plugin"* **cannot be made** on this design.
> Tracked as [G-7](#10-capability-gaps).

---

## 6. Functional requirements

Grouped by the three seams. Seam A and Seam B are independent; neither blocks the other.

### Seam A — ACP → Nova (the provider)

#### FR-1 — Publish an ACP catalogue endpoint the Nova provider can consume

ACP exposes a read-only catalogue projection of its governed entities. It must be shaped for a
Backstage `EntityProvider` doing a **full mutation** on a schedule, because that is what
`APICatalogProvider` does and matching it is most of the delivery cost saved.

**API Contract Sketch**:

```
GET /api/v1/catalog/nova-projection?environment={env}&page={n}
Authorization: Bearer <service principal JWT>

Response: {
  "generated_at": "2026-09-04T14:00:00Z",
  "page": 1, "pages": 3,
  "entities": [
    { "acp_id": "01a01b8b-...", "kind": "agent",
      "name": "fdes-pharmacy-agent", "display_name": "FDES Pharmacy Agent",
      "owner": { "project": "Pharmacy", "team_ref": "..." },
      "governance": { "state": "active", "approval": "approved",
                      "risk_tier": null, "policy_count": 2 },
      "source": { "repo_url": "...", "apm_number": "..." },
      "acp_url": "https://luminate.../agents/01a01b8b-..." }
  ]
}
```

- Must be **stable and complete per call** — a full-mutation provider deletes anything absent, so a partial response silently deletes catalogue entries. Pagination must be snapshot-consistent or absent
- Must carry `acp_id` as the immutable join key. Names change; ids do not
- Must be reachable by a **machine identity**. This lands on [CAP-06](../../../capability-map.md#cap-06) — see [G-3](#10-capability-gaps)

#### FR-2 — Split the system of record by field, not by entity

The failure mode to design out is two write-masters on one record. Ownership is per field:

| Field group | System of record | Direction |
|---|---|---|
| Source repo, build pipeline, APM number, owning team, tech stack | **Nova** | Nova → ACP at registration |
| Agent identity (`acp_id`), lifecycle state, approval state, access policies, credentials, risk tier, kill state | **ACP** | ACP → Nova, read-only in Nova |
| Display name, description, icon, catalogue tags | **Nova** | Nova → ACP as advisory metadata only |
| Plugin/skill approval state, scan verdict, provenance, recall state | **ACP** | ACP → Nova, read-only in Nova |
| Plugin/skill content, versions, source location | **The marketplace Git repo** | Repo → both |

Fields projected into Nova from ACP must be **read-only in Nova**, or round-tripped. Whichever
is chosen, it must be the same choice for every field in the group.

#### FR-3 — Represent unregistered agents rather than hiding them

The provider projects ACP-governed agents. Nova independently discovers agents from source
(`novaTools`, 30 min). The **difference between those two sets is the shadow-AI number** and is
the most valuable single output of this integration. Nova must show discovered-but-unregistered
agents as a distinct state, and ACP must be able to report the count.

#### FR-4 — Match the API Platform provider's operational contract

Schedule, timeout, mutation type, annotation namespace and failure behaviour follow
`APICatalogProvider` unless there is a stated reason to differ: `applyMutation({type:'full'})`,
scheduled (6h for APIs; **30 min proposed here** — governance state changes faster than an API
catalogue), 30-minute timeout, `sunlife.com/*` annotations. Provider errors must not empty the
catalogue: a failed fetch **skips** the mutation rather than applying an empty one.

> **Note.** `IDP/idp-backstage-plugin-slf-api-platform-portal` is a *different* thing — a
> frontend plugin that iframes the API Factory. The provider to copy is
> `backend-catalog-providers/src/api-providers/apiCatalogEntityProvider.ts`. Confirm which one
> is meant whenever someone says "like the API platform plugin".

### Seam B — Marketplace supply chain → ACP

#### FR-5 — Pin every marketplace source, and the index itself, immutably

**Plugin sources.** Every `git-subdir` entry carries a 40-character commit sha in the schema's
**`sha`** field — not `ref`, which the schema defines as *"Git branch or tag"*. Tags are not
acceptable pins: a tag is a movable ref and can be deleted and re-pushed to a different commit.
Every `npm` entry carries an exact version and an integrity hash. An entry that cannot be pinned
is not published.

**The index.** The README's documented consumption path is `…/marketplace-plugins.git#main` — a
branch tip re-read on every resolution ([M-7](#2-what-the-plugin-marketplace-is-today-verified)).
Until a client supports pinning an index, the index repo must be protected as production code:
branch protection on `main` with required review, **tag-write restriction**, no force-push, and
CI as the only writer of generated files. This is a compensating control, not a fix, and the
residual is stated in [G-6](#10-capability-gaps).

This requirement is the **prerequisite for everything else in Seam B**. Scanning an unpinned
source certifies nothing.

#### FR-6 — Generate the marketplace indexes; stop hand-syncing them

Both `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json`, and the per-plugin
manifest copies, are **generated** from a single source of truth in CI, and CI fails if the
committed files differ from the regenerated ones.

The two indexes legitimately differ — one carries `https://` clone URLs, the other `ssh://` —
so "keep them identical" is not the fix; **derive both from one record** is. Five hand-maintained
files per plugin become one.

This is the same enforcement this repo already applies to `specs/README.md` and
`epic-mapping.json`: generated files are never hand-maintained. It closes
[M-2](#2-what-the-plugin-marketplace-is-today-verified) by construction rather than by discipline.

#### FR-7 — Gate publication on a skill-aware scan plus conventional SAST/SCA

Publication to the marketplace index requires, per plugin version:

| Layer | Covers | Tool posture |
|---|---|---|
| Skill-aware scan | OWASP AST01–AST10: malicious instructions, over-privilege, injection, capability drift | NVIDIA **SkillSpector** (Apache-2.0) — static mode needs no API key; emits SARIF 2.1.0 with a 0–100 risk score |
| SAST | Bundled code — `scripts/`, `agents/tools/*.py` | Existing Sun Life SAST |
| SCA | Declared dependencies of bundled code, npm-sourced plugins | Existing Sun Life SCA (Snyk) |
| Manifest/skill conformance | Agent Plugins v1 manifest validity; Agent Skills frontmatter (`name` present and matching directory; no undefined fields) | Schema validation + `skills-ref validate` |
| **Index-entry conformance** | The marketplace entry itself: reject any entry carrying `hooks`, `mcpServers`, `lspServers`, `commands`, `monitors` or `settings` inline; require `strict: true`; require `dependencies` to be absent; require top-level `allowCrossMarketplaceDependenciesOn` to be an explicit empty list | Schema validation against an SLF-narrowed profile of `claude-code-marketplace.json` |

The index-entry layer exists because of [M-7](#2-what-the-plugin-marketplace-is-today-verified):
without it the whole gate is walked around by putting the payload in the index instead of in a
plugin. `strict: true` forces a real manifest in the plugin folder rather than one supplied by
the entry, and an empty cross-marketplace allowlist blocks dependency-driven resolution from a
marketplace [FR-11](#fr-11-restrict-harnesses-to-approved-marketplaces) never authorised.

Findings from all layers compose on the SARIF `artifacts[].hashes["sha-256"]` join key with
`properties.layer` naming the producing class, per the OWASP multi-scanner interoperability
pattern. **The digest is the join key and the evidence anchor** — the same digest that pins the
artefact ([FR-5](#fr-5-pin-every-marketplace-source-and-the-index-itself-immutably)) binds the
finding to it. Note the asymmetry: the source pin is a SHA-1 commit id while component digests
are SHA-256, and **the SHA-256 file digests are the authoritative binding**.

Greg's ask — *"ideally that is part of existing SAST processes"* — is satisfied by treating
SkillSpector as one more SARIF producer in the existing pipeline rather than a new pipeline.

**Waivers are separated from authorship.** A waiver on a critical/high finding is an *input* to
the gate, so it must not live in the author's own change: it lives on a restricted path with its
own CODEOWNERS, and CI rejects a waiver whose approver is the version's author. ACP cannot
enforce separation of duties for us — [CAP-14](../../../capability-map.md#cap-14) has no multi-step
or SoD approvals — so this is enforced in CI or not at all. Tracked as [G-8](#10-capability-gaps).

#### FR-8 — Record a plugin version, its components and its verdict in ACP

ACP holds, per plugin version: source pin, manifest digest, component inventory (each skill,
reference and asset file, agent definition, MCP server entry and bundled script with SHA-256),
scan verdict and report reference, any waiver and its approver, approver identity and timestamp,
lifecycle state.

**This is the requirement that has no home in ACP today** — see
[§3](#3-what-acp-can-hold-today-verified) and [G-1](#10-capability-gaps). Until the Skills
Registry lands, the record is held in the marketplace repo as CI-written, branch-protected,
review-gated artefacts ([D2](d2-design.md) DD-6) and ACP references them. The **schema is
identical either way**, so the migration is a load, not a redesign.

#### FR-9 — Enumerate every declared MCP server against the MCP registry

Every MCP server a published plugin can cause a client to connect to is reconciled against ACP's
MCP registry ([CAP-03](../../../capability-map.md#cap-03)). That is three declaration sites, not
one: the plugin's `mcp.json`, the Claude Code manifest's `mcpServers`, and the marketplace
entry's `mcpServers`/`channels` blocks. A `streamable-http` or `sse` server not registered in
ACP is **ungoverned egress from a developer workstation** and is flagged at review. `stdio`
servers are local execution and are a SAST concern, not a registry one.

Reconciliation is a call into ACP and therefore needs the machine identity
[G-3](#10-capability-gaps) blocks. **Enumeration and flagging run in Phase 0; automated
reconciliation lands with Phase 1.**

#### FR-10 — Withdraw a version, and state the limit of that reach

Withdrawal republishes the index without the affected plugin versions and marks the record
`withdrawn` with a reason. Evidence is retained; the record is never deleted.

**The limit is part of the requirement.** Republishing prevents **new** installs. It does not
reach an already-provisioned workstation and — because no installation-recording mechanism exists
in Phases 0–1 — it cannot even enumerate who holds it. Reaching that far requires the gatekeeper
plugin ([M-6](#2-what-the-plugin-marketplace-is-today-verified)) made mandatory and cross-harness,
or endpoint management. That is [Q-6](#open-questions) and [G-7](#10-capability-gaps). Until they
are answered, "recall" means **unpublish and notify**, and must be described that way to any
risk audience.


#### FR-11 — Restrict harnesses to approved marketplaces

Developer harnesses are configured to the Sun Life marketplace and the defaults are removed:
VS Code `chat.plugins.marketplaces`; Claude Code `claude plugins marketplace add`. The
marketplace allowlist is **the only enforcement point either harness offers**, which is
precisely why [§4.1](#41-plugin-or-skill-which-is-the-unit-of-governance) puts approval at the
plugin level.

This is a managed-configuration requirement on the Sun Life estate
(INT-08 in the [capability map](../../../capability-map.md)), not an ACP feature, and
it needs a **named owner in endpoint management / GDS** — assumption
[A-5](#11-constraints-and-assumptions). It is stated as a requirement because without it every
other requirement in Seam B is advisory: `chat.plugins.marketplaces` is a user-editable setting,
and the marketplace README itself instructs users to add and remove marketplaces by hand. Absent
FR-11, Phase 0 delivers *an attested marketplace for those who opt in*, which is worth having
but is not a supply chain.

#### FR-12 — Do not claim per-skill runtime enforcement

No requirement in this spec may assert runtime blocking of an individual skill. No harness
exposes it. Skill-level control is **review-time and inventory-time**; plugin-level control is
distribution-time; there is no runtime layer for either on a developer workstation.

Stated as a requirement because the temptation to imply otherwise is the most likely way this
spec would mislead a risk committee.

#### FR-13 — MicroVM and harness session telemetry (deferred, with a stated condition)

D0's MicroVM observability requirement is retained and deferred. It re-enters scope when a
Sun Life-developed agent **executes inside Nova's own runtime**
(`nova-agentgateway.sunlifecorp.com`), because that is server-side traffic ACP could plausibly
govern. Developer-workstation harness sessions are a different problem with a different
control set and are explicitly out of scope here.

ACP has no external audit-producer profile today ([CAP-18](../../../capability-map.md#cap-18),
gap [EACPP-826](https://sunlife.atlassian.net/browse/EACPP-826)), so this requirement is
blocked on that regardless.

#### FR-14 — State the runtime delineation in writing

Nova operates `nova-agentgateway.sunlifecorp.com` and exposes Backstage actions as MCP. ACP
operates a governed gateway ([CAP-08](../../../capability-map.md#cap-08)). The written delineation
must answer: which agent traffic traverses which gateway, whether Nova-Backstage-as-MCP is
registered in ACP's MCP registry, and who governs Nova's LangGraph service. A one-page answer
agreed at the meeting is worth more than a design that assumes one.

---

## 7. Non-functional requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Freshness | ACP governance state visible in Nova | ≤ 1 provider interval (30 min proposed) |
| NFR-2 | Integrity | Published plugin versions resolvable to immutable bytes | 100% — an unpinnable entry is unpublishable |
| NFR-3 | Availability | Provider fetch failure must not empty the Nova catalogue | Skip mutation on error; alert on 2 consecutive failures |
| NFR-4 | Performance | Catalogue projection endpoint, full page | < 2s p95, ≤ 500 entities/page |
| NFR-5 | Security | Provider authenticates as a machine identity; no shared static secret | OAuth2 client credentials ([CAP-06](../../../capability-map.md#cap-06)). **Phase 1 interim exception**: a scoped API key, while [G-3](#10-capability-gaps) stands. Expires when service-principal auth is on by default |
| NFR-6 | Scan latency | Plugin version scan-to-verdict in CI | < 10 min p95, static mode |
| NFR-7 | Evidence retention | Plugin version evidence records incl. withdrawn | Retained per record-retention schedule; never hard-deleted |
| NFR-8 | Determinism | Regenerating marketplace indexes from source yields byte-identical output | 100%, enforced in CI ([FR-6](#fr-6-generate-the-marketplace-indexes-stop-hand-syncing-them)) |
| NFR-9 | Observability | Every sync run emits count in/out, deltas, errors, duration | All runs |

---

## 8. Data model requirements

Written to be a strict subset of the Skills Registry D1's model so it can be absorbed rather
than migrated.

| Entity | Key fields | Relationships |
|---|---|---|
| **Plugin** | `id`, `name` (Agent Plugins name constraints), `owner_project`, `repository`, `harness_targets[]` | has_many PluginVersion |
| **PluginVersion** | `id`, `version`, `source_pin` (40-char sha / npm version+integrity), `manifest_digest`, `manifest_standard` (`agent-plugins-1.0.0` \| `claude-code`), `state` (`draft`→`scanned`→`approved`→`published`→`deprecated`→`withdrawn`), `approved_by`, `approved_at`, `withdrawn_reason` | belongs_to Plugin; has_many Component; has_many ScanAttestation; has_many Waiver |
| **Component** | `id`, `type` (`skill` \| `reference` \| `asset` \| `agent_definition` \| `mcp_server` \| `script`), `path`, `sha256`, `declared_name`, `conformance` (`valid` \| `invalid` + reason) | belongs_to PluginVersion; skill components may reference MCPServer |
| **ScanAttestation** | `id`, `layer` (`skill` \| `sast` \| `sca` \| `conformance` \| `index-entry`), `tool`, `tool_version`, `verdict`, `risk_score`, `report_uri`, `artifact_digests[]`, `run_at` | belongs_to PluginVersion; joins Component on `sha256` |
| **Waiver** | `id`, `finding_ref`, `justification`, `approved_by`, `approved_at`, `expires_with_version` | belongs_to PluginVersion; `approved_by` ≠ the version author (enforced in CI) |
| **Installation** *(Phase 2, conditional on [Q-6](#open-questions))* | `id`, `plugin_version_id`, `principal`, `harness`, `first_seen`, `last_seen` | belongs_to PluginVersion |
| **CatalogProjection** | `acp_id`, `kind`, `nova_entity_ref`, `last_synced`, `sync_state` | maps ACP entity ↔ Nova entity |

`reference` and `asset` are not padding. In `switchboard-lite` they are **the bulk of the
instruction payload**: ~30 files under `skills/api-platform/references/` and ~40 under
`skills/ai-dlc/.aidlc-rule-details/`. That content is loaded progressively by the agent, is
exactly what AST01/AST02 target, and the second lives in a **dot-directory** — so the inventory
must digest dotfiles rather than skip them. An inventory covering only `SKILL.md` would miss most
of what actually shapes behaviour.

Two deliberate omissions. **No `Skill` top-level entity** — a skill exists as a `Component` of a
`PluginVersion`, per [§4.1](#41-plugin-or-skill-which-is-the-unit-of-governance). And **no
required-API declaration**: the Skills Registry D1's declaration model depends on API Resources
(PR #105, draft) and is out of scope until that has a decision. `allowed-tools` is captured on the
skill component as a **blocking review trigger**, not as a grant.


## 9. Edge cases

| Scenario | Expected behaviour |
|---|---|
| Nova provider fetch fails or times out | Skip the mutation entirely. Never apply an empty full mutation — it would delete every projected entity |
| ACP entity deleted | Projection removes it on the next full mutation; ACP retains the audit record |
| Same agent discovered by `novaTools` **and** projected from ACP | Join on `acp_id`; if absent, join on repo URL + name; if still ambiguous, show both and flag a reconciliation task. Never silently merge |
| Plugin version passes scan, then the upstream git ref moves | Impossible once [FR-5](#fr-5-pin-every-marketplace-source-and-the-index-itself-immutably) holds. Before that: the index is republished from source and the digest mismatch is a hard CI failure |
| Skill fails Agent Skills conformance ([M-5](#2-what-the-plugin-marketplace-is-today-verified)) | Record it as `conformance: invalid` and block publication. A conformant client would skip it silently, so an inventory row without this flag would assert governance over something never loaded |
| `mcp.json` names an unregistered remote server | Flag at review as ungoverned egress; do not auto-register |
| Plugin declares `agents[]` under the Claude Code schema and targets Agent Plugins v1 | Inventory the agent files as components; record `manifest_standard`; note the fields are ignored by a v1 client |
| Two harnesses resolve the same plugin name differently | Fails CI under [FR-6](#fr-6-generate-the-marketplace-indexes-stop-hand-syncing-them) — indexes are generated from one source |
| Withdrawn plugin still installed on a workstation | Flag the installation; no runtime revocation is claimed ([FR-12](#fr-12-do-not-claim-per-skill-runtime-enforcement), [Q-6](#open-questions)) |
| Nova AI Catalog uses the `nova-tools` namespace model; provider emits the approved `ai-skills` model | Entity validates but does not appear in the AI Catalog. Blocked on [Q-1](#open-questions) before any provider is written |

---

## 10. Capability gaps

> Classified per [Capability Gap Escalation](../../../process/capability-gap-escalation.md).

| Capability | What is missing | Classification | Impact | Escalation |
|---|---|---|---|---|
| **G-1** — no skill/plugin entity | ACP has no entity for a plugin, a version, a component or an attestation. Zero code. The Skills Registry D1 is an unmerged draft with `Decision: Pending`, and its dependency (API Resources) is also an unmerged draft | **Component change** — consortium | Blocks [FR-8](#fr-8-record-a-plugin-version-its-components-and-its-verdict-in-acp) natively; workaround available (attestations in the marketplace repo) | Ask the consortium to **move PR [#106](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/106) to a decision**, and to amend it per G-2. New EACPP ticket required |
| **G-2** — Skills Registry has no bundle level | PR #106 models the skill version as the top governed entity. The only control point the harnesses expose is the **plugin**. Without a bundle parent, an approved skill cannot be mapped to an installable artefact | **Component change** — consortium, and an *amendment* to a design in flight | Determines whether the registry is usable for coding-harness governance at all | Comment on PR #106 with the plugin-containment model from [§4.1](#41-plugin-or-skill-which-is-the-unit-of-governance) — cheapest while it is still a draft |
| **G-3** — machine identity is default-off | `BearerServicePrincipalAuthentication` exists but `SERVICE_PRINCIPAL_AUTH_ENABLED=False` in **all four** SLF values files, is appended per-view rather than in `DEFAULT_AUTHENTICATION_CLASSES`, and the trusted issuer is a single env string | **Integration** (SLF config) + **component change** (multi-issuer) | Blocks [FR-1](#fr-1-publish-an-acp-catalogue-endpoint-the-nova-provider-can-consume) — the Nova provider is a machine caller | Same blocker as Vulcan; [CAP-06](../../../capability-map.md#cap-06). Do not raise twice — attach to the existing track |
| **G-4** — no external audit producer | ACP ingests audit only from its own gateway; no producer profile for a Sun Life system | **Component change** — consortium | Blocks [FR-13](#fr-13-microvm-and-harness-session-telemetry-deferred-with-a-stated-condition) | [EACPP-826](https://sunlife.atlassian.net/browse/EACPP-826) — existing |
| **G-5** — no Sun Life standard for agent plugin marketplaces | No EA standard, no GDS approval requirement, no security review pattern exists for plugin marketplaces or agent skills. Confluence searches for `marketplace.json`, Claude Code plugins and OWASP Agentic Skills return nothing substantive | **Integration** — Sun Life governance | Not a blocker; an **opportunity**. There is no incumbent to displace | Propose the marketplace control model as the standard, jointly with EA (Greg) and the InnerVerse team |
| **G-6** — the marketplace index cannot be pinned by the client | Both harnesses consume the index from a branch tip (`#main`), and the schema permits unsandboxed inline execution in an index entry ([M-7](#2-what-the-plugin-marketplace-is-today-verified)). No client supports pinning or verifying an index | **Integration** — Sun Life, plus an upstream limitation neither ACP nor the consortium owns | Residual risk on the highest-privilege artefact in the design | Compensate via repo hardening + the index-entry conformance layer ([FR-7](#fr-7-gate-publication-on-a-skill-aware-scan-plus-conventional-sastsca)); raise index signing with the harness vendors |
| **G-7** — no installed-base visibility or runtime recall | Nothing records which workstation holds which plugin version, and nothing revokes one. [CAP-11](../../../capability-map.md#cap-11) is a **P0** map gap — no first-class runtime kill, no cascade, *and no design* | **Integration** (endpoint management) for workstations; **component change** for ACP-side recall | Bounds [US-5](#us-5-prove-it-to-an-examiner) and [FR-10](#fr-10-withdraw-a-version-and-state-the-limit-of-that-reach). "Recall" means unpublish and notify | [Q-6](#open-questions); [EACPP-646](https://sunlife.atlassian.net/browse/EACPP-646) for the ACP-side kill switch |
| **G-8** — no separation of duties in approval | ACP has no multi-step or SoD approvals ([CAP-14](../../../capability-map.md#cap-14), **P1**), and no plugin-approver role exists at Sun Life ([Q-8](#open-questions)). Nothing platform-side prevents an author approving their own plugin or waiver | **Component change** (consortium) + **Integration** (CI enforcement now) | An approval gate that permits self-approval is a formality | Enforce author ≠ approver in CI ([FR-7](#fr-7-gate-publication-on-a-skill-aware-scan-plus-conventional-sastsca)); attach the platform ask to the existing CAP-14 track |
| **G-9** — no signed evidence pack | [CAP-19](../../../capability-map.md#cap-19) is **P0**: a governance-scoped export ships, but the signed, immutable evidence pack — crosswalks, coverage scoring, attestor signoffs — is designed and in build, not shipping. OSFI itself is expressible as a regime | **Component change** — consortium | [US-5](#us-5-prove-it-to-an-examiner) is served by the marketplace attestation store, **not** by ACP. Do not trace a compliance claim to a capability that does not exist | [EACPP-649](https://sunlife.atlassian.net/browse/EACPP-649) — existing |

**Interim measures**

| Gap | Interim measure | Removed when |
|---|---|---|
| G-1 | Plugin version records and scan attestations are CI-written artefacts in the marketplace repo, schema-identical to the eventual ACP entity | Skills Registry ships and the records are loaded |
| G-2 | The plugin/skill containment relation lives in the SLF schema and in a comment on PR #106 | The consortium adopts a bundle level (or rejects it, at which point SLF owns the relation permanently) |
| G-3 | Provider uses a scoped API key or a per-view service-principal exemption in the SLF deployment. Note this needs **both** `SERVICE_PRINCIPAL_AUTH_ENABLED` and `SERVICE_PRINCIPAL_AUTH_SCOPE_ENFORCED` — with the latter off, machine tokens are admitted but their scopes narrow nothing | Both flags on by default with multi-issuer support |
| G-6 | Branch protection, tag-write restriction and required review on `marketplace-plugins`; CI as the only writer of generated paths; index-entry conformance layer | A client supports pinning or verifying a marketplace index |
| G-7 | "Recall" is described as unpublish-and-notify everywhere it appears | An installation-recording mechanism exists and is mandatory across harnesses |
| G-8 | CI enforces author ≠ approver on both approvals and waivers | ACP supports multi-step / SoD approvals |

---

## 11. Constraints and assumptions

**Constraints**

- Nova is upstream Backstage. Anything that cannot be expressed as a Backstage entity, annotation or provider is not deliverable in Nova, and Backstage's entity model is not ours to change
- Nova's approved component types are governed by `IDP/idp-backstage-sunlife-system-model`. Adding or altering a type is a change request to that repo, not a decision this spec can take
- The harnesses enforce at marketplace and plugin level only. Nothing in Copilot or Claude Code enforces at skill level, and neither can pin or verify a marketplace index
- A git **tag** is not an immutable pin — tags can be deleted and re-pushed to a different commit. Only a 40-character commit sha is
- The marketplace schema permits a plugin *entry* to declare `hooks`, `mcpServers`, `lspServers`, `commands`, `settings` and `monitors` inline, the last documented as unsandboxed. The index is therefore a higher-privilege artefact than any plugin it lists
- Agent Plugins v1 defines **no** marketplace, distribution, permission or credential model. Governance metadata must live in the `extensions` namespace or a sidecar — there is no standard slot, and anything shipped in a plugin is attacker-controlled data
- ACP cannot store a plugin or a skill today, and the design that would allow it is unapproved
- Sun Life SAST/SCA tooling (Snyk, Checkmarx, SonarQube) is the incumbent pipeline; a skill scanner joins it as a SARIF producer rather than replacing it
- OSFI is expressible as a Luminate compliance regime — Governance Mode ships the regime schema, not the regimes, and Sun Life supplies the E-23/B-13 control catalogue ([CAP-19](../../../capability-map.md#cap-19)). What no claim can rest on yet is the *signed evidence pack*, which is designed and in build rather than shipping

**Assumptions** — each falsifiable, each with an owner

| # | Assumption | Falsified by | Owner |
|---|---|---|---|
| A-1 | Nova will accept a new `EntityProvider` for ACP on the `APICatalogProvider` pattern | Nova team declining, or requiring a different ingestion path | InnerVerse / CAH |
| A-2 | `ENTARCH/marketplace-plugins` is the intended production marketplace, not only a demo | A different marketplace repo being designated | EA (Greg) |
| A-3 | The marketplace repo can run CI capable of scanning and generating indexes | Bitbucket/Jenkins constraints in ENTARCH | EA + CI owners |
| A-4 | SkillSpector (or equivalent) is approvable for use in the SLF pipeline | Tooling approval refused | Security |
| A-5 | Developers will be centrally configured to the Sun Life marketplace | No managed-configuration path for VS Code/Claude Code settings | GDS / endpoint management |

---

## 12. Traceability

| Requirement | Capability | Seam | D0 success criterion | Jira |
|---|---|---|---|---|
| FR-1 | [CAP-01](../../../capability-map.md#cap-01), [CAP-06](../../../capability-map.md#cap-06) | A | Unified catalogue | EACPP-895 |
| FR-2 | [CAP-01](../../../capability-map.md#cap-01) | A | Zero manual registrations | EACPP-895 |
| FR-3 | [CAP-01](../../../capability-map.md#cap-01) | A | 100% governance coverage | EACPP-895 |
| FR-4 | [INT-08](../../../capability-map.md) | A | — | EACPP-895 |
| FR-5 | — *(no ACP capability; the pin is a marketplace-side control)* | B | Audit trail coverage | EACPP-895 |
| FR-6 | INT-08 | B | — | EACPP-895 |
| FR-7 | G-5, G-8 *(no ACP capability — supply-chain scanning is not [CAP-17](../../../capability-map.md#cap-17), which is model/agent evaluation)* | B | Compliance gates at registration | EACPP-895 |
| FR-8 | G-1, G-2 | B | Audit trail coverage | EACPP-895 |
| FR-9 | [CAP-03](../../../capability-map.md#cap-03) | B | — | EACPP-895 |
| FR-10 | G-7 *(**not** [CAP-11](../../../capability-map.md#cap-11) — that is agent kill switch, itself a P0 gap. Withdrawal here is index republication)* | B | — | EACPP-895 |
| FR-11 | INT-08 | C | Governance at scale | EACPP-895 |
| FR-12 | — | C | *(negative requirement — bounds the claim)* | EACPP-895 |
| FR-13 | [CAP-18](../../../capability-map.md#cap-18), G-4 | C | MicroVM observability | [EACPP-826](https://sunlife.atlassian.net/browse/EACPP-826) |
| FR-14 | [CAP-08](../../../capability-map.md#cap-08) | C | — | EACPP-895 |
| US-1 | CAP-01, CAP-21 | A | Unified catalogue | EACPP-895 |
| US-2 | G-1 | B | Approval before production | EACPP-895 |
| US-3 | G-1 | B | Classification of agent types | EACPP-895 |
| US-4 | CAP-01 | A | Single source of truth | EACPP-895 |
| US-5 | G-9 *(**not** [CAP-19](../../../capability-map.md#cap-19) — that is a P0 gap with nothing shipping. Evidence comes from the marketplace attestation store)* | B | 100% audit coverage | EACPP-895 |

---

## Open questions

These need answers from the Nova/EA side. Ordered by how much downstream work each unblocks.

| # | Question | Why it blocks | Proposed answer |
|---|---|---|---|
| **Q-1** | Which Nova model does an ACP provider target — the approved `spec.type: ai-skills` component type, or the AI Catalog's `namespace: nova-tools` + `spec.type ∈ project\|agent\|skill`? | An entity emitted against the wrong one validates and then **does not appear in the AI Catalog**. Blocks all of Seam A | Converge the AI Catalog onto the approved model, and have the ACP provider target the approved model only |
| **Q-2** | Is `ENTARCH/marketplace-plugins` the production marketplace, or a demo to be replaced? Who owns it, and can it run CI? | Decides whether Seam B is built there or somewhere else | Promote it, with EA as owner and InnerVerse/CI support |
| **Q-3** | Agent Plugins v1 as the portable floor, with Claude Code as a client superset — agreed? | Decides the manifest schema, and therefore where governance metadata lives | Yes, per [§4.2](#42-which-plugin-standard) |
| **Q-4** | Does Nova intend to discover plugins from `marketplace.json`, given `novaTools` today reads `agents/*.yaml`, `skills/*.yaml`, `projects/*.yaml`? And if ACP projects plugin entities instead, **where does `sunlife.com/apm-number` come from** — it is required on the `plugin` and `ai-skills` types, and an ACP-originated entity does not have one | Greg's note describes plugin discovery as a future capability; it is not current Nova behaviour. The APM requirement means "just project them" needs an answer or a change request to `idp-backstage-sunlife-system-model` | Add a `marketplace.json` reader to `novaTools` (which keeps APM attribution on the Nova side, where the repo registry already lives) rather than projecting plugins from ACP |
| **Q-5** | What governs `nova-agentgateway.sunlifecorp.com` and Nova-Backstage-as-MCP? | Two gateways with overlapping remit and no written boundary ([FR-14](#fr-14-state-the-runtime-delineation-in-writing)) | Register Nova-Backstage-as-MCP in ACP's MCP registry; agree gateway scope in writing |
| **Q-6** | Is there a path to enforce plugin withdrawal on an already-provisioned workstation? | Determines whether recall is a real control or a notification | Via the gatekeeper plugin ([M-6](#2-what-the-plugin-marketplace-is-today-verified)) if it can be made mandatory and cross-harness; otherwise notification only, stated as such |
| **Q-7** | Was [EACPP-850](https://sunlife.atlassian.net/browse/EACPP-850) rejected as a duplicate, or on the merits? | If on the merits, this spec needs a different sponsor before it advances | Duplicate — confirm with Pavithra |
| **Q-8** | Who owns the plugin approval decision — EA, Security, the InnerVerse team, or a joint board? | [FR-8](#fr-8-record-a-plugin-version-its-components-and-its-verdict-in-acp) records an approver identity; no approver role exists yet, and [G-8](#10-capability-gaps) means self-approval is possible until one does | Joint: automated gate blocks, named security approver signs, EA owns the standard. Author ≠ approver enforced in CI from day one |
| **Q-9** | What is the **data classification** of content vendored into a plugin? `switchboard-lite/skills/api-platform/SKILL.md` records *"Source: DAADP · Last crawled: 2026-05-11 · Pages: 140 · Total words: 38,231"* — internal platform documentation, crawled into a bundle installable from a `file://` path or a clone | EA will raise this immediately and no scanner catches it. Classification, redistribution rights and re-classification of the source are all unaddressed | Require a classification declaration per plugin version; restrict internal-only plugins to authenticated sources; re-review on source re-classification |
| **Q-10** | Is branch protection, required review and tag-write restriction already in force on `ENTARCH/marketplace-plugins`? | [FR-5](#fr-5-pin-every-marketplace-source-and-the-index-itself-immutably) and [G-6](#10-capability-gaps) treat it as the compensating control for an index nobody can pin. It is currently **assumed, not verified** | Verify with the repo owner before Phase 0 starts; if absent, it is the first task |
| **Q-11** | How does a developer learn a pinned install is stale, and who runs the incident when a previously-clean plugin turns critical? | Pinning makes updates explicit, which also makes staleness silent. [§7](#7-non-functional-requirements) alerts on a new critical finding but names no owner, no runbook and no SLA | Publish an update-available signal from the index; name an owning team for plugin security incidents at the same time the gate goes blocking |

---

## References

- [D0: Discovery](d0-discovery.md) — superseded in the five respects listed in [§0](#0-what-changed-since-d0)
- [D2: Design](d2-design.md)
- [ACP Capability Map](../../../capability-map.md) · [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
- Luminate **D1 Skills Registry** — `luminate-designs` branch `d1/skills-registry`, PR [#106](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/106) (draft), Andrew Culberson (TELUS)
- Luminate **D1 API Resources** — PR [#105](https://ai-consortium.ghe.com/AI-Consortium/luminate-designs/pull/105) (draft)
- [Agent Plugins specification v1.0.0](https://agent-plugins.org/specification) · [Agent Skills specification](https://agentskills.io/specification)
- [OWASP Agentic Skills Top 10 — Skill Scanner Integration](https://owasp.org/www-project-agentic-skills-top-10/skill-scanner-integration) · [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)
- Sun Life: [`ENTARCH/marketplace-plugins`](https://bitbucket.sunlifecorp.com/projects/ENTARCH/repos/marketplace-plugins/browse) · `ENTARCH/marketplace-git-plugin` · `IDP/idp_backstage` · `IDP/idp-backstage-sunlife-system-model`
- Confluence [113078141303](https://sunlife.atlassian.net/wiki/spaces/GDEP/pages/113078141303) — Nova Build Hub Onboarding Guide
