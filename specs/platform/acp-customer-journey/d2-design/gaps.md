# Gaps, exits and open questions

## Failure and exit paths

| Path | Where | Behaviour |
|------|-------|-----------|
| Entry prerequisite missing | Entry gate, before 1.1 | Onboarding pauses until the completed GbyD form and ready MRM MBCT ID are supplied. Rare in practice — most use cases already hold both — and a pause rather than a termination (DD-19) |
| Exact match to an existing pattern | 1.2a | 1.7 and 1.8 are skipped entirely — no pattern to define and nothing to build. The engagement runs 1.3–1.6 and closes at 1.9 |
| End user requests changes | 1.6a | The design returns to 1.5, is redrafted and re-presented at 1.6, so the loop may run more than once |

None of these rows is a rejection. **The entry gate is the only point at which work does not
proceed**, and even there it pauses rather than ends: ACP checks that the two prerequisites are
present, not whether it agrees with them, and onboarding starts as soon as a missing one is supplied
(DD-19). **1.2a is the short path**, not an exit — it still produces `d0` to `d2`
and still closes at 1.9; **1.6a is the only loop in Phase 1**, a rework path that keeps an
unconfirmed design from going further. Once past the entry gate, Phase 1 has no path that terminates
an engagement: the
go/no-go step after discovery was removed (DD-14), and pattern rejection was withdrawn (DD-11) — the
pattern question at 1.2 always ends in either an exact match or a build. The two delivery tracks at
1.8 do different work — integration is built by ACP, while a component change goes upstream as a
delta spec and a consortium idea (DD-4) — but they converge on the same closing communication,
because ACP closes the loop either way (DD-12, DD-18). The gap register in D1 is the single record;
where a gap is open the diagram carries it as a note rather than implying a route through it.

## Relationship to neighbouring specs

| Spec | Relationship |
|------|--------------|
| `integration-patterns` | The identity, invocation and inference catalogue plus the adoption path; one input to the 1.2 ruling (DD-8) |
| [`agent-patterns`](../../../pattern/agent-patterns/d2-design.md) | The agent/application distinction, egress/ingress shapes, hosting catalogue and SUB-E/SUB-I criteria screened at 1.2 (DD-8) |
| `governance-intake` | Risk classification, validation gates and PIA/ISRA/ATG routing. **Deliberately not wired into this journey** — a future ACP capability, see DD-10 |
| `luminate-user-guides` | Portal click-paths from registration onward. This spec owns *who you talk to and in what order*; the guides own *which button* |
| `engineer-onboarding` | Onboarding for ACP engineers, not for use cases. Distinct journey, same gate model |

## Traceability

| Question this spec must answer | Answered by |
|-------------------------------|-------------|
| "What is the process to be onboarded to ACP?" | Step table and journey diagram — as far as pattern readiness |
| "Who do I talk to, and when?" | Interaction points |
| "What will you ask me to produce?" | Artefact model |
| "Who decides whether my solution needs a new pattern?" | The **Regional Architect**, at 1.2 — DD-17 |
| "What is the process to build ACP?" | Steps 1.7–1.8, DD-3, DD-4 |
| "Who builds a new pattern — ACP or the Consortium?" | DD-4, applying the delineation rule in `docs/process/capability-gap-escalation.md` §1 |
| "How does an externally delivered pattern come back?" | DD-12 — the close-the-loop hand-back, confirmed by ACP |
| "What happens while a consortium ask is pending?" | DD-13 — a documented, explicitly temporary interim measure |
| "What counts as an existing agent pattern?" | DD-8 — the applicable shapes in [`agent-patterns`](../../../pattern/agent-patterns/d2-design.md), assessed alongside `integration-patterns` |
| "How will I know it is finished?" | 1.9, the closing communication — DD-18 |
| "How long does this take?" | **Not answered** — no durations or SLAs. CG-4 |
| "What happens after I am ready to register?" | Partly — DD-5 names the specs that cover it. Runtime governance and change management remain unowned (D0 OQ-2) |

## Open questions

Gaps in the process itself are tracked once, in the D1 gap register. One is open and does not block
sign-off here: **CG-4** (per-step durations), carrying an interim measure in D1. **CG-5** — 1.2b-1
having no defined outcome when governance approval is refused — is closed: Phase 1 now assumes
governance approval for a new pattern is eventually granted, so SC-4 is asserted at zero (DD-10).
The residual risk that the assumption is wrong is carried as D0 R-9, not as a process gap.

**DQ-9 is a different kind of item and is not counted against SC-4.** CG-5 was an *undefined
outcome* — no drawn behaviour for a refusal. DQ-9 asks whether an already-*defined* behaviour is
sufficient: nothing between 1.3 and 1.6 re-tests the 1.2 fit finding, which is a stated property of
the journey, not a gap in it. Whether that needs a checkpoint is a correctness question for the
Enterprise Architect and Regional Architect to weigh, not a missing outcome. Scoping questions are
in D0. Design-level questions specific to this document:

| ID | Question | Owner |
|----|----------|-------|
| DQ-1 | **Resolved.** An exact-match engagement takes the short path: the Regional Architect confirms fit at 1.2a and the engagement skips 1.7 and 1.8 entirely, never reaching the Enterprise Architect (DD-17) | ACP EA |
| DQ-2 | **Resolved.** `scripts/sync_mermaid_embeds.py` regenerates the embed and `--check` enforces it in CI | ACP |
| DQ-3 | **Resolved.** The mandatory baseline link resolves to the capability map, §3 | ACP |
| DQ-4 | **Resolved.** `governance-intake` is out of scope for now: GbyD risk triage and MRM model-risk assessment occur before entry, ACP manually verifies their outputs, and platform PIA/ISRA/ATG approval is how a new pattern is authorised at 1.2b-1 — see DD-10 | ACP |
| DQ-5 | Do the six engagement actors need mapping to Luminate portal personas for the hand-off into registration? | ACP |
| DQ-6 | **Resolved.** 1.7 and 1.8 are reached only from 1.2b. An exact match closes no capability gap, so there is nothing to assess and nothing to build | ACP |
| DQ-7 | When and how does the journey move from the First Wave (ACP-led, high-touch) model to the target self-serve, RA-led model? | ACP EA |
| DQ-8 | **Resolved.** 1.2b-1 initiates the applicable PIA / ISRA / ATG approval before discovery. Discovery and design may proceed while the approval is long-lead; ACP confirms approval before 1.8 implementation or upstream delivery. The applicable governance route remains determined by platform governance | ACP EA + platform governance |
| DQ-9 | Nothing between 1.3 and 1.6 re-tests the 1.2 fit finding. Does a wrong exact-match call need a checkpoint, or is the 1.6 design review sufficient? | ACP EA + RA |

## D2 exit criteria

- [x] CG-1 closed — pattern rejection was withdrawn from the journey; there is no rejection outcome left to define recovery behaviour for (DD-11)
- [x] CG-2 resolved — the Consortium hands back to ACP for re-verification (DD-12)
- [x] CG-3 closed — FDES removed from Phase 1, so no engagement criteria are needed (DD-9)
- [x] CG-5 closed — governance approval for a new pattern is assumed eventually granted; residual risk carried as D0 R-9 (DD-10)
- [x] Entry prerequisites recorded as a gate before 1.1 — presence checked by ACP, not approved, with IP-0 and a responsibility-model row (DD-19)
- [x] ACP EA, RA and DA have confirmed their responsibility-model rows (review of 2026-09-04, DD-17 and DD-18)
- [ ] EU and CT have confirmed their responsibility-model rows
- [ ] Confirmation record completed with a name against every actor (NFR-3)
- [ ] Readability reviewed by the ACP Product Owner
- [ ] Published to Confluence and `confluence_page` recorded in `spec.yaml` (NFR-5)
- [x] D0 OQ-1 answered — `platform` spec, registered in `spec.yaml`
- [x] Embedded diagram reconciled with `customer-journey.mmd` and regeneration automated (DQ-2)
- [x] Step 1.2 names the catalogues it rules against — `integration-patterns` and `agent-patterns` (DD-8)
- [x] DQ-1 answered — an exact match takes the short path and skips 1.7 and 1.8 (DD-17)
- [x] DQ-4 answered — `governance-intake` is deliberately out of scope for now (DD-10)
- [x] DQ-8 answered — 1.2b-1 initiates the applicable governance approval; discovery and design may proceed, but ACP confirms approval before 1.8 implementation or upstream delivery
