# MDx High-Level Architecture

This document is the human-readable overview of what MDx is made of and how Forge, the governed software factory, works end-to-end. It is meant for engineers, agents, and reviewers who want to reason about the system without reading every ADR.

Machine-readable companions: `generated/architecture/mdx-architecture-map.json`, `generated/architecture/harness-runway.json`, `generated/source-map/mdx-source-map.json`.

---

## What MDx Is

MDx is a local-first AI workspace. It lets a team do company work with governed AI specialists, receipts, and fail-closed authority. The three foundational ideas:

1. **Receipts or it did not happen.** Every consequential action produces a ledger receipt. UI claims, verdicts, and handoffs point at evidence, not at narrative certainty.
2. **Fail-closed by default.** Missing provider, missing authority, missing evidence - the system blocks, names what is missing in human language, and waits. It never fakes green.
3. **Local first, cloud optional.** The default path runs on a developer's machine without Docker or Postgres. Docker, Postgres, cloud deploy, external auth, and production writes are separate opt-in gates backed by observed evidence.

---

## Top-Level Components

```
+---------------------------------------------------------+
|  Product Surfaces (Svelte, apps/)                       |
|  Observatory  Concierge  Twin  Forge  Pages  Message    |
+------------------------+--------------------------------+
                         |  HTTP / read models
+------------------------v--------------------------------+
|  mdx-server  (Rust, local CLI + HTTP routes)            |
|  Forge harness routes  Twin routes  Auth  Kernel HTTP   |
+------------------------+--------------------------------+
                         |  domain calls
+------------------------v--------------------------------+
|  mdx-core  (Rust, the kernel)                           |
|  ConstraintEvaluator  Ledger  Charter  Treasury         |
|  MemoryProvider  OutboxProvider  LoopRunner  ReadModels |
+-----+------------------+------------------+------------+
      |                  |                  |
  Postgres         LocalLoopRunner     mdx-codegen
  (optional)       (workflow)          (generated
                                        contracts)
```

### apps/ - product surfaces

| App | Purpose |
|-----|---------|
| `apps/mdx` | Main product shell (nav, theme, shared layout) |
| `apps/twin` | Twin companion: grounded assistant with live or local model |
| `apps/concierge` | Concierge: search and knowledge surface with receipt-backed answers |
| `apps/observatory` | Observatory: system health, loop status, evidence dashboard |
| `apps/forge` | Forge operator shell: build intent, stage trail, evidence |
| `apps/pages` | Pages: world-model documents with provenance |
| `apps/message` | Message: event-plane communication surface |
| `apps/shared` | Shared Svelte primitives, `humanCopy.js`, `uxModel.js`, `localTruth.js` |
| `apps/start` | First-run setup flow |
| `apps/mdx-host` | SvelteKit host app: server hooks, admin access, session handling |

All surfaces are read-only over generated contracts and harness read models. Write authority is receipt-backed and fail-closed until the corresponding rail is proven live.

### crates/ - Rust backend

| Crate | Role |
|-------|------|
| `crates/mdx-core` | Kernel: receipts, policy, Ledger, Charter, Treasury, memory, providers, read models, loop runners, Forge harness primitives |
| `crates/mdx-server` | HTTP server and CLI: all routes, Forge execution sandbox, execution posture logic |
| `crates/mdx-codegen` | Deterministic code and artifact generator |
| `crates/mdx-ctx-engine` | Context engine: retrieval and context injection |
| `crates/mdx-dxr-engine` | DXR engine: developer experience reads |
| `crates/mdx-message-relay` | Realtime message relay bridge |
| `crates/mdx-observability` | Tracing and observability plumbing |

### xtask/ - executable invariant gates

`xtask` holds the drift gates that CI and `make` checks run. Generated contracts must match source declarations or the gate fails.

### generated/ - committed machine-readable contracts

All generated artifacts live here and are never hand-edited. Key maps:

- `generated/architecture/mdx-architecture-map.json` - the machine architecture graph
- `generated/source-map/mdx-source-map.json` - source doc -> generated artifact -> check
- `generated/change-gates/mdx-change-gates.json` - change type -> required checks
- `generated/agents/mdx-agent-work-queue.json` - bounded agent work items
- `generated/ui/mdx-theme.css` - the single token source for colors, spacing, radii

---

## The Kernel (mdx-core)

The kernel is the trust root. It owns:

- **Ledger** - append-only receipt chain (BLAKE3-compatible hash spine). Every consequential action lands here. The Postgres projection keeps a durable copy when the database gate is open.
- **ConstraintEvaluator** - policy engine. Every action gets a policy decision before execution. No policy decision = blocked.
- **Charter** - charter evidence records that back authority grants.
- **Treasury** - budget authorization. Workers, runs, and fleets cannot exceed their declared budget.
- **MemoryProvider** - pluggable memory. Local in-memory and Postgres are the live local drivers. mem0 is a pending vendor slot.
- **OutboxProvider** - event emission for downstream surfaces.
- **Read models** - projections consumed by Observatory, Concierge, and Forge surfaces.
- **LoopRunner** - loop-runner declarations (`evals_runner_agent`, `aegis_scanner_agent`, `charter_attestation_agent`, `forge_orchestrator_agent`, `product_shaping_agent`, `talent_autonomy_agent`). Local driver is `LocalLoopRunner`. Temporal is a pending vendor slot.

The kernel protection ring means: if a PR touches receipts, evidence, generated route catalogs, storage, auth/tenant admission, provider-secret posture, or migrations, the review bar rises from "does this pass checks" to "does this preserve the trust model months from now."

---

## The Harness

The harness is the execution envelope around models and coding agents. It is the infrastructure that makes Forge possible.

### Three Rings

| Ring | What It Owns |
|------|-------------|
| **Runtime** | `LocalLoopRunner`, `TemporalLoopRunner`, `ModelGateway`, deterministic local loop methods |
| **Capabilities** | `StorageProvider`, `MemoryProvider`, `OutboxProvider`, read surfaces, generated tool manifests |
| **Safety and Scale** | `ConstraintEvaluator`, policy receipts, `TreasuryAuthorization`, `CharterRecord`, `Ledger`, `xtask` gates |

### Five Zones

| Zone | Purpose |
|------|---------|
| **Context Injection** | Memory records, role views, read surfaces, Concierge receipt evidence fed to the model |
| **Control** | Constraint evaluation, autonomy ceilings in capability cards, worker scope and expiry |
| **Action** | Loop declarations, tool manifests, `LoopRunner`, server run-loop routes |
| **Observe and Verify** | `EvalVerdict`, local budgets, `make verify-budget`, `xtask`, generated invariant fixtures |
| **Persist** | Ledger, BLAKE3 hash chain, Postgres SQL projection, `CharterRecord`, outbox receipts |

### Non-Negotiables

- One runtime truth. Web, CLI, API, Observatory, Message, Concierge, Twin, and all other surfaces project the same manifest, transcript, receipts, and verdicts.
- Policy before action. Every consequential action gets a policy and permission decision.
- Receipts before confidence. Final answers, verdicts, handoffs, and ship claims point at evidence.
- Local proof before live claims. Deterministic local proof comes before live model, worker, substrate, or deployment claims.
- Replaceable machines. Claude, Codex, Grok, Gemini, local models, and future agents are execution backends, not sources of truth.

---

## How Forge Works

Forge is the governed software factory. It translates a human intent into a scoped, policy-mediated build and delivers verifiable evidence at every step.

### The Build Path

```
intent -> classify -> plan -> build -> test -> review -> security -> evidence -> PR (-> ship)
```

Each arrow is a stage transition guarded by the harness. No stage advances without policy approval and a ledger receipt.

### 1. Admission and Classification

The operator writes an ask. Forge runs `ForgeWorkClassification` (route: `/forge/work-classifications.json`) to produce a typed receipt proposing:

- **work shape**: `run` (single worker) or `mission` (multi-stage, long-horizon)
- **task class**: `bug_fix`, `feature`, `refactor`, `security`, `ci_repair`, `docs_code`, `multi_file`, `architecture`, etc.
- **complexity tier**: `small`, `medium`, `large`, `xl`, or `extreme`
- **suggested checks**, **write scope**, **blocked paths**

Classification never grants execution authority. It records `forge.work_classification.recorded` with `classification_grants_execution_authority=false`.

### 2. Plan

The `LocalHarnessPlanRunner` admits the run manifest, emits a deterministic plan item, records policy decisions and receipts, and refuses any writes. The plan is reviewed - approved hash is recorded - before build begins.

The run manifest is typed (`docs/HARNESS-RUN-MANIFEST-CONTRACT.md`): tenant, actor, surface, mode, scope, blocked paths, policy profile, enterprise pack, budget, quality gates, and exit criteria all live in the manifest before execution.

### 3. Build

Forge runs inside an execution sandbox. On macOS the default posture is `scrubbed_sandboxed`:

- subprocess environment is scrubbed to a toolchain allowlist (PATH, HOME, TMPDIR, locale, cache - never provider keys or credentials)
- Seatbelt profile confines filesystem writes to the workspace, build cache, and temp dirs
- proof commands run with network denied; setup commands keep network (internet-on-setup, locked agent phase)

Four postures exist:

| Posture | When Active |
|---------|------------|
| `scrubbed_sandboxed` | Default on macOS - scrubbed env + Seatbelt |
| `scrubbed_unconfined` | Default where no OS sandbox exists - env scrub only |
| `container` | Docker path when `MDX_PLAN_TEST_EXEC=1` |
| `raw_host_opt_in` | Legacy full-env host execution, explicit opt-in only |

Every posture flip is a ledger event.

The model (Forge builder agent) gets a `shell` tool (read-only exploration) and governed edit tools. Shell calls never count as proof. Ship eligibility comes only from allowlisted `run_command` checks.

### 4. Test and Review

After build, quality gates run. The `LocalHarnessPlanExecuteLoop` records:

- approved plan hashes
- denied dangerous actions
- planned quality gate results
- final verdicts

The tool execution plane (`LocalHarnessReadToolPlane`) mediates reads, searches, lists, and patches with path rules, output caps, policy decisions, receipts, and transcript items.

### 5. Ship Gate

`ForgeRunShipDecision` requires `observed_branch_tip`. The ship route:

1. reads the run's branch from its receipts
2. asks git for the actual current tip
3. refuses `CommitMismatch` when the ratified commit is not that tip

An unverifiable ratification (no repo, no branch, no tip) is refused, never recorded.

Live delivery at `/forge/source-host-live-deliveries.json` requires the `forge.run.ship.decided` receipt and re-verifies the ratified commit against the branch tip at delivery time. A branch that moved after review refuses with `ship_commit_mismatch`.

### 6. Autonomous Delivery (Tier 3, default-off)

When a human records a `self_delivery_scope` on an autonomy envelope, Forge can:

- `SelfOpenPr` - open its own PR after diff firewall and fresh-eyes concurrence
- `SelfConvergeCi` - drive CI to green through bounded fix runs (max 3 iterations)
- `SelfMerge` - merge on green CI + commit-exact binding + N evaluator concurrences + active envelope

The **self-modification firewall** is the load-bearing invariant: `PROTECTED_PATHS` (governance kernel, envelope/registry code, ship/merge gate, `.github/workflows/`, the firewall itself, `docs/adr/`) can never be written by any self-delivery run regardless of the envelope's `allowed_path_scopes`. Production deployment stays human (ADR 0139, unchanged).

The kill switch is `revoke_autonomy_envelope`. Revoking stops in-flight self-delivery at the next turn boundary.

### Work Shapes

| Shape | Use Case |
|-------|---------|
| **run** | Single focused change, one lane, one principal path |
| **fleet** | Multiple independent lanes working in parallel, ratified plan |
| **mission** | Long-horizon, multi-stage work with milestones, budget, and checkpointed review |

### Receipts on Every Outcome

Key receipt kinds emitted by Forge:

- `forge.work_classification.recorded`
- `forge.execution_posture.recorded`
- `forge.run.ship.decided`
- `self.delivery.pr_opened`
- `self.delivery.ci_converged`
- `self.delivery.merged`
- `self.delivery.escalated`
- `worker.spawn_requested`
- `worker.retired`

---

## Workers

Ephemeral workers are bounded job agents. They are not loop-runners or persistent actors. Every spawn requires:

- `sponsor_chain_authority_receipt_id`
- `worker_lease_authority_receipt_id`
- `budget_authority_receipt_id`
- `tool_allowlist_authority_receipt_id`
- `credential_check_receipt_id`

Worker runtime is `PENDING-LIVE-RUN`. Talent is the only intended provisioning path. Workers cannot bypass Talent, exceed budget, ignore expiry, or deploy production changes without approval.

---

## Product Surfaces

### Twin

Grounded assistant. Answers questions using the model the operator connected during setup. History context and answer caps are enforced at the server to prevent truncated replies. Session persona is declared; live provider calls require provider turn-on evidence.

### Concierge

Search and knowledge surface. Returns receipt-backed answers drawn from Pages, source maps, and declared fixtures. `localTruth.js` in `apps/shared` is the client-side projection layer.

### Observatory

System health and loop status. Read-only projection over loop-runner status, ledger counts, charter evidence, and local verification results.

### Pages

World-model documents with provenance. Draft, approve, publish lifecycle is receipt-backed. Context sources are declared and tracked.

### Message

Event-plane communication. Realtime relay bridge (`crates/mdx-message-relay`). Thread projections and outbox receipts back every message.

---

## UI Architecture

All product surfaces are thin operator consoles over generated contracts:

- **Generated token source**: `generated/ui/mdx-theme.css` - one place for colors, spacing, radii, typography, focus rings
- **Shared primitives**: `apps/shared/` - `humanCopy.js`, `uxModel.js`, `harnessRunway` adapters, `localTruth.js`, `FirstViewport.svelte`
- **Visual posture**: dark operational console, dense but calm, near-black backgrounds, color codes state not decoration, 8px radius max
- **Theme modes**: `system`, `dark`, `light` - all three required
- **Human translation layer**: system truth stays strict; `humanCopy.js` translates it into operator-legible English before it hits the first viewport

`FirstViewport.svelte` is required for Observatory, Concierge, and Twin opening surfaces. It answers four questions: what is running now, what needs my judgment, what is the safe next move, and what evidence backs this.

---

## Agent Operating Model

MDx is an agent-built repo. Humans set direction and approve risk; agents author file changes.

```
human intent -> agent branch -> scoped edit -> checks -> PR -> human review -> merge
```

Valid authoring agents: `codex`, `claude`, `gemini`, `grok`, `forge`.

Forge itself is treated as an agent. It obeys the same boundaries: scoped branch, isolated worktree, declared checks, receipts, no hidden authority.

Branch prefixes enforce ownership: `forge/<lane>-<slug>`, `codex/<lane>-<slug>`, `claude/<lane>-<slug>`, etc.

Key generated contracts agents read before work:

- `generated/agents/mdx-agent-work-queue.json` - bounded work items with write scope, blocked paths, required checks, definition of done
- `generated/agents/mdx-frozen-kernel-contract.json` - protected kernel surfaces that require human review
- `generated/agents/mdx-agent-preflight.json` - preflight check list
- `generated/change-gates/mdx-change-gates.json` - change type -> required checks

---

## Current Runtime Status

| Surface / Substrate | Status |
|--------------------|--------|
| Rust harness foundation | `LIVE-LOCAL` |
| Forge local orchestrator | `LIVE-LOCAL-BLOCKED` |
| Forge frontend | `LIVE-LOCAL-READ-SURFACE` |
| Local plan runner | `LIVE-LOCAL-PLAN-ONLY` |
| Transcript and audit replay | `LIVE-LOCAL-AUDIT-REPLAY` |
| CLI inspection | `LIVE-LOCAL-READ-ONLY` |
| Provider coding loop | `LIVE-LOCAL-FAIL-CLOSED` |
| Plan execute loop | `LIVE-LOCAL-FAIL-CLOSED` |
| Forge autonomous delivery (Arc 7) | `LIVE-LOCAL, default-off` |
| Postgres runtime | `LIVE-LOCAL` |
| Durable workers | `PENDING-LIVE-RUN` |
| Temporal workflow runner | `PENDING-LIVE-RUN` |
| TensorZero model driver | `PENDING-LIVE-RUN` |
| mem0 memory driver | `PENDING-LIVE-RUN` |
| OpenTelemetry | `PENDING-LIVE-RUN` |
| Render deployment | `PENDING-LIVE-RUN` |

`PENDING-LIVE-RUN` is intentional and honest. MDx does not call a substrate ready until observed evidence exists.

---

## Key Checks

```sh
# architecture drift
make architecture-check

# harness runway
make harness-runway-check

# agent contracts
make agent-context-spine-check
make agent-work-queue-check
make frozen-kernel-contract-check

# UI
make ui-app-check
make ui-build-check

# fast confidence
make local-smoke
git diff --check

# generated contracts
make generate
make generated-clean
make source-map-check
```

---

## Further Reading

- `docs/AGENT-OPERATING-SYSTEM.md` - agent authoring rules and PR protocol
- `docs/AGENT-CONTEXT-SPINE.md` - progressive disclosure map for all change types
- `docs/KERNEL-101.md` - kernel protection ring primer
- `docs/HARNESS-NORTH-STAR.md` - end-state compass for the harness
- `docs/HARNESS-RUNWAY.md` - incremental harness gate status
- `docs/FORGE-OPERATOR-EXPERIENCE.md` - Forge product experience contract
- `docs/FORGE-EXECUTION-BOUNDARY.md` - execution posture and sandbox details
- `docs/FORGE-AUTONOMOUS-DELIVERY.md` - self-delivery design and Arc 7 status
- `docs/FORGE-WORK-CLASSIFICATION.md` - intent to work-shape classification
- `docs/WORKER-SPAWN-CONTRACT.md` - ephemeral worker authority contract
- `docs/DESIGN.md` - design system and visual contract
- `docs/UI-FRONTEND-ARCHITECTURE.md` - frontend boring-architecture doc
- `docs/DEV-101.md` - minimal maintainer handoff