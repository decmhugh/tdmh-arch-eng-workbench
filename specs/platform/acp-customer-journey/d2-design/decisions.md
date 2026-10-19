# Design decisions

## DD-1 — One sequence, two readings

The same steps answer both the customer question ("how do I get onboarded") and the internal
question ("how do we build ACP capability"). Steps 1.1–1.6 and 1.9 are the customer path; 1.7–1.8
are the build path, and an exact-match engagement never enters them. Splitting them into two
documents was rejected: they share the pattern-fit decision at 1.2, and two documents would diverge
at exactly the point that matters. **Effort S / Risk Low.**

## DD-2 — Use-case onboarding runs on the D0→D4 gate model, unmodified

A use case is captured with the same artefacts, and the **same filenames**, as an ACP component
spec. An onboarding engagement is therefore reviewable through the existing PR + gate process,
appears in `specs/README.md`, and maps to a Jira epic without a second mechanism.

Naming the D2 artefact anything other than `d2-design.md` was rejected: a private vocabulary would
break `validate_specs.py`, `assemble_d2_design.py` and `generate_spec_index.py`, all of which key
off the standard names, and would make an engagement's artefacts unreadable to anyone who works on
component specs. Cost: business stakeholders see engineering vocabulary. Mitigation is the artefact
table, which states each file's contents in plain terms. **Effort S / Risk Low.**

## DD-3 — The pattern decision is a hard gate before any build

Nothing is implemented until the pattern question has been ruled and a delivery owner named. The
ruling now happens twice, at two different grains: the **Regional Architect** decides fit at 1.2
(DD-17), and the **ACP Enterprise Architect** defines the pattern and names its owner at 1.7. This
prevents ACP building a bespoke integration that duplicates an approved pattern, and prevents both
ACP and the Consortium believing the other is delivering.

**Effort M / Risk Medium.** Moving the fit decision to 1.2 removes the latency this decision used to
carry for obvious existing-pattern cases — they no longer reach the Enterprise Architect at all,
which is what DQ-1 asked for. The residual risk moves with it: a wrong call at 1.2 now sends an
engagement down the short path with no later checkpoint to catch it (DQ-9).

## DD-4 — Delivery owner follows the delineation rule, and the two tracks are not symmetric

The owner is not the ACP EA's preference. It is a **classification**, and the authoritative test
lives in `docs/process/capability-gap-escalation.md` §1: does closing this require **Luminate itself
to behave differently**? Yes makes it a component change and it goes to the consortium; no means it
is about reaching a Sun Life system, which is integration and the harness absorbs it. This journey
applies that rule rather than restating it.

An earlier draft modelled the two branches as symmetric, with the Consortium producing `d3-tasks.md`
and `d4-verification.md` exactly as ACP does. That was wrong. The escalation process describes two
different shapes of work:

| | Integration — Sun Life track | Component change — consortium track |
|---|---|---|
| Delivered by | ACP, through the harness or a platform team | The consortium, upstream |
| ACP produces | `d3-tasks.md`, `d4-verification.md` | A **delta spec** in `acp-consortium-specs` |
| Enters through | The normal D0–D3 product process | The **idea backlog** — prioritised, then voted |
| Timeline | ACP controls it | Not ACP's, and acceptance is not guaranteed |
| Ends with | "New pattern ready" | Close the loop — DD-12 |

So the consortium branch produces no `d3-tasks.md` of ACP's making. What ACP owes upstream is the
delta spec: what Luminate does today, what is missing, what should change, and what the Sun Life MVP
already proved.

Two refinements come from the same source and are drawn in the journey. **A shared ask splits**
rather than picking a side — audit forwarding is the standing example, where emitting the events is
a component change and shipping them into Sun Life's tenant is integration. And **reclassification
is normal**: an integration ask that turns out to need Luminate to change re-enters the consortium
track at step 1, which is usually the point at which the harness boundary gets sharper.

**Effort M / Risk Medium** — the residual risk is timeline rather than ownership, which DD-13
absorbs.

## DD-5 — The spec stops at pattern readiness, and says so

Registration, runtime operation and governance were drafted and cut. Phase 1 is a coherent unit — it
ends when a use case is specified and its pattern verified — and it is the part the ACP Product Team
controls end to end.

The ground past the boundary is **not** all unwritten, which narrows what the follow-on spec has to
cover:

| After Phase 1 | Already covered by |
|---|---|
| Which button, which field, to register an agent, model or MCP server | `luminate-user-guides` — `building/` |
| Access grants, deployment to a gateway, credential issue | `luminate-user-guides` — `administration/` |
| Register → deploy → credential → store → exchange → invoke → observe | `integration-patterns` — adoption |
| Identity, invocation and inference patterns | `integration-patterns` |
| Agent vs Application, egress/ingress, hosting shapes and the SUB-E/SUB-I conformance criteria | [`agent-patterns`](../../../pattern/agent-patterns/d2-design.md) |
| Risk classification, validation gates, PIA/ISRA/ATG | `governance-intake` |

What genuinely has no owner is **runtime governance and change management** — what happens when a
registered agent changes materially, and who re-runs which gate. **Effort S / Risk Medium.**

## DD-6 — The `.mmd` file is the source; the spec embeds a generated copy

The diagram lives in `customer-journey.mmd`. `d2-design/journey.md` carries a copy between
`BEGIN/END GENERATED` markers so the spec renders standalone in MkDocs and Confluence.

Editing the copy in place is the drift failure this guards against, so the guard is mechanical
rather than a convention: `scripts/sync_mermaid_embeds.py` rewrites the block from source, and
`--check` in CI fails the build when the two disagree. **Effort S / Risk Low.**

**The Miro board the journey started in is retired** (D0 R-7). Keeping it as a stakeholder-facing
view was considered and rejected: a hand-maintained board is a second editable copy, and the moment
the two disagree the "official" journey depends on who you ask — which is the exact failure the
generated embed was built to remove. A board cannot be CI-checked, so nothing would catch the drift.

The `.mmd` is therefore the only editable artefact, maintained by the **ACP Product Team**. If a
presentation view is wanted later, it is *rendered* from the `.mmd`, never redrawn.

## DD-7 — Step numbers are internal; the phase name is the customer-facing unit

Customers are told they are in ACP intake, not that they are at step 1.7-3. Step numbers serve the
ACP Product Team's own tracking and will renumber as the process changes — as they have three times
already: when FDES was removed (1.4–1.7 became 1.3–1.6), when the design review was added and
pattern rejection withdrawn (1.1–1.6 became 1.1–1.7), and now when the Regional Architect's
pattern-fit decision and the final delivery communication were added (1.1–1.7 became 1.1–1.9).
**Effort S / Risk Low.**

## DD-8 — 1.2 rules against written catalogues, not recollection

"Existing pattern" is only meaningful if the set of patterns is written down. The
`integration-patterns` spec remains the catalogue for identity, invocation and inference, plus the
adoption path a team walks. For an agent solution, the RA also screens the complete set of
applicable shapes in [`agent-patterns`](../../../pattern/agent-patterns/d2-design.md): first Agent vs
Application, then egress-only vs ingress, and then the applicable hosting shapes. S1-S4 are
specified examples, not a closed list; any other substrate is assessed against SUB-E/SUB-I.

The finding records the shapes considered, the shape or shapes selected, the evidence for fit, and
any open criteria. The use case must fit an applicable shape, not every shape in the catalogue.
An open or unexercised substrate criterion is not by itself a refusal or a reason to invent a new
pattern; record its impact and decide whether the documented shape still meets the use case's need.
1.2a means an existing documented shape is suitable without defining a new pattern; 1.2b means no
existing shape meets the need and a new pattern is required. The two catalogues are complementary,
not substitutes for one another.

The alternative, leaving "existing" to the reviewer's judgement, was rejected because it makes the
gate unauditable and makes SC-3 unmeasurable: you cannot record that a pattern was selected if there
is no list to select from. **Effort S / Risk Low** — both catalogues are themselves specs in review
(`integration-patterns` and `agent-patterns` are both at D3, draft), so the three move together, and
both must be current and usable by the Regional Architects without the authors in the room.

**Moving the decision to the Regional Architect at 1.2 sharpens this dependency rather than easing
it.** The catalogue is now consulted by six regional architects rather than one enterprise
architect, so both catalogues have to be readable and current without the authors in the room
(DD-17).

## DD-9 — **Withdrawn.** FDES is not a Phase 1 actor

An earlier draft placed the **Forward Deployed Engineering Team** in the journey as optional
development support: an engagement decision at 1.3 and a hand-back at 1.8, with the engagement
criteria left open as CG-3.

D2 review removed it. Whether ACP draws on FDES capacity is a resourcing question inside the ACP
Product Team, not a hand-off in the customer's journey, and drawing it as a branch implied a
decision the business group participates in. It also carried an open gap (CG-3) into a diagram that
is otherwise decided, and it was the only step whose sole outcome was "nothing changes".

FDES is therefore not an actor, has no step, and appears in no interaction point or RACI row. The
accountability that mattered is unchanged and now unconditional: **the ACP Product Team owns the
outcome of every engagement**, whoever it borrows hands from. CG-3 is closed as no longer
applicable. **Effort S / Risk Low.**

## DD-10 — Governance approval is a precondition to implementation; PIA/ISRA/ATG attaches to the pattern

The entry gate that checks the business holds a completed GbyD GenAI Risk Triage Form and a ready
MRM MBCT ID is owned by **DD-19**. What follows here is the separate question of governance
*approval*.

`governance-intake` (EACPP-877) defines a second intake — a form feeding risk triage, producing a
band that drives validation requirements and gated deployment, with PIA/ISRA/ATG routed to
ServiceNow. Wiring it into this journey was considered and deliberately deferred.

Two different things were being conflated, and separating them is what makes both tractable:

- **Use-case governance is a precondition of entry.** A business group arriving at 1.3 is expected
  to hold the governance approvals its use case requires. Phase 1 neither runs risk triage nor gates
  on it.
- **Platform governance attaches to a new pattern, and is initiated before specification starts.**
  Where 1.2 finds that no existing pattern fits, the Regional Architect initiates PIA / ISRA / ATG
  approval at **1.2b-1**, before discovery begins. A long-lead approval may complete after discovery
  and design start, but ACP confirms it before 1.8 implementation or upstream delivery. It is a gate
  before delivery, not a reason to block discovery while the request is being assessed.

This also disposes of DQ-4: PIA/ISRA/ATG is platform governance attached to a new pattern, and it is
the only governance step Phase 1 contains.

**The approval request moved earlier in D2 review.** It previously sat inside the Enterprise
Architect's assessment, after the design was drawn. Placing the request at 1.2b means the long-lead
process starts before discovery, while the approval confirmation remains a delivery gate after the
design and pattern definition are ready. This lets 1.3-1.7 proceed without allowing implementation
or upstream delivery to start before approval.

`governance-intake` becomes part of the ACP product later, and when it does this journey gains a
triage step rather than a second intake. Modelling one now would document a process no team runs.
**Effort S / Risk Medium** — the residual risk is a use case arriving without the approvals it was
assumed to hold, which the 1.3 discovery session has to surface.

**What 1.2b-1 does not define is its own refusal — and Phase 1 now assumes it does not need to.**
PIA/ISRA/ATG can in principle be declined, or granted with conditions, and an earlier draft tracked
that as **CG-5**, an undefined outcome blocking SC-4. **Resolved as an assumption, not a design
change**: for Phase 1, governance approval for a new pattern is assumed to be eventually granted —
outright refusal is treated as out of scope for this journey, on the same basis the platform
governance owners already apply to other mandatory obligations. A conditional approval is not a
refusal and stays drawn: the Regional Architect reworks the pattern intent against the stated
conditions and resubmits at 1.2b-1. Discovery and design may continue, but the 1.8 gate remains
closed until approval is confirmed. CG-5 is closed on that basis; the residual risk — that the
assumption is wrong and a use case is
refused outright with no drawn recovery — is carried as **R-9** in D0, not as an open process gap,
because no journey step is missing, only a possible-but-unmodelled real-world outcome.

## DD-11 — **Withdrawn.** Pattern rejection is not a Phase 1 step

An earlier draft gave Domain Architects a rejection outcome at 1.5c: a proposed new pattern could be
turned down with a rationale, returning the use case to the discovery session for rework.

D2 review removed it. The pattern question now yields exactly two outcomes — the design matches an
existing pattern (1.2a), or a new pattern is required (1.2b) — and a new-pattern finding always
proceeds to definition at 1.7 and build at 1.8. There is no decision step in which the Regional
Architect, the Domain Architects or the Enterprise Architect reject a use case's proposed pattern
outright.

**Rejection was never the right model, because the pattern question classifies rather than judges.**
The question is *which* pattern this design needs — one that already exists, or one that has to be
built. Both answers are outcomes; neither is a refusal. "Reject" presumes a third answer, *no
pattern*, and there is no such thing: a design that fits nothing existing is precisely the
definition of a new pattern, which is a build instruction, not a rebuttal. The diagram notes at 1.2
and 1.7 carry this reading and are the authoritative statement of it.

This argument is unaffected by the decision moving from the Enterprise Architect to the Regional
Architect (DD-17). It is a property of the question, not of who answers it.

An earlier version of this decision argued instead that the design review superseded the rejection
branch. **That argument does not hold and has been withdrawn.** 1.6 is the End User confirming
*business fit* — does this solve my problem. The withdrawn 1.5c was a Domain Architect objecting on
*architecture*. A business group cannot catch an architectural objection, so the two are not
substitutes and the design review never absorbed its purpose. What removes the rejection outcome is
the classification argument above, not the review that precedes it.

CG-1 is closed as no longer applicable — there is no rejection outcome left to define recovery
behaviour for. **Effort S / Risk Low.**

## DD-12 — The Consortium hand-back is the escalation process's close-the-loop step

CG-2 asked what returns an externally delivered pattern to ACP, and who confirms it. The answer
already existed in `docs/process/capability-gap-escalation.md` §3 step 5; it simply was not drawn in
the journey. Inventing a bespoke hand-back here was rejected, because a second route would diverge
from the one the repository already documents for consortium work.

When the consortium delivers, the hand-back is:

1. **The accepted work lands upstream** in Luminate, on the consortium's timeline rather than the
   engagement's.
2. **ACP re-verifies it and updates the capability map.** A capability moving from ⚠️ or ❌ to ✅ is
   the observable evidence that the work landed.
3. **ACP closes the Sun Life ticket referencing the consortium ticket**, so one ask does not carry
   two open statuses in the delivery view.
4. **ACP updates the request status to "new pattern ready"** — the same terminal step as the
   integration branch, which is where the two tracks converge even though their work differs.

**The ACP Product Team confirms it, not the Consortium.** The team that owns the use case owns the
verification, because it is the only party that can say whether the delivered capability satisfies
the requirement that raised it. Self-certification by the delivering team would leave the use case
without a check. Work performed elsewhere still returns to ACP, and ownership never transfers with
it. **Effort S / Risk Low.**

## DD-13 — A use case waiting on a consortium ask ships a documented interim measure

A consortium ask is prioritised and then voted, so it does not return on the engagement's timeline
and it may not be accepted at all. The use case neither waits indefinitely nor gets the gap absorbed
into the harness to hit a date — `docs/process/capability-gap-escalation.md` names that absorption as
an anti-pattern, because it is how Sun Life quietly forks away from the product.

What ships instead is an interim measure that is **explicitly temporary**, recorded in the
engagement's own D1 gap register together with the condition that removes it. That is the same
mechanism the capability gaps in this spec already use, so it needs no new machinery.

**Effort S / Risk Medium** — the risk is an interim measure quietly becoming permanent, which is
precisely what the recorded removal condition exists to prevent.

## DD-14 — Entering the journey is the decision; there is no separate go/no-go step

An earlier draft drew a proceed decision after discovery, branching into "continue specification
development" or "end engagement". D2 review removed both the decision message and the branch.

A business group that has asked for a discovery session has already decided it wants to onboard, so
the branch modelled a choice that was made before step 1.1. Drawing it invited the reading that ACP
qualifies the use case in or out at 1.3, which is not what happens: 1.3 walks the capability map and
produces `d0-discovery.md`. **By default every engagement proceeds.**

The consequence, now that pattern rejection is also withdrawn (DD-11), is that Phase 1 models no
negative or exit outcome at all. Every engagement that enters at 1.1 proceeds through the 1.2
pattern-fit decision and the 1.6 design review to a closing communication at 1.9. A use case that
turns out to be unsuitable is still handled, but as a conversation between ACP and the business
group, recorded in `d0-discovery.md`, not as a drawn path. **Effort S / Risk Low** — the residual
risk is a use case being carried further than it should be, which the 1.2 fit decision and the 1.6
design review both catch.

## DD-15 — A design review with the End User runs before the pattern is defined

Step 1.6 puts `d2-design.md` in front of the End User immediately after 1.5. The business group
confirms the solution meets its need — or asks for changes — while the design is still cheap to
change, rather than finding out at 1.7 that the architecture assumed something the business group
never agreed to. On an exact-match engagement it is the last substantive step before the closing
communication.

This review is about **business fit** — the End User confirming the solution solves the problem they
brought. It is deliberately not an architecture check, and it does not stand in for one: the
withdrawn 1.5c rejection outcome was a Domain Architect objecting on architectural grounds, which a
business group is not positioned to raise. That outcome was removed on its own merits (DD-11), not
because the design review replaced it. **Effort S / Risk Low.**

## DD-16 — This journey is the First Wave model: interim, high-touch, ACP-led

Phase 1 as specified is deliberately high-touch — every hand-off in the interaction model routes
through the ACP Product Team, and every step is scheduled rather than self-served. That is a
statement about where ACP is today, not a target architecture: this is the **First Wave** of
onboarding, run this way because the ACP Product Team is still small, patterns are still few, and
each early engagement is establishing precedent the later ones will reuse.

**Target state is fully self-serve.** The End User will engage their Regional Architect directly,
and the RA — not the ACP Product Team — will own and drive the ACP onboarding engagement end to
end. That end state is known; the timeline and the mechanism that gets there are not, and this spec
does not attempt to design them prematurely (DQ-7).

Modelling the target state now was considered and rejected: a self-serve flow has different actors,
different artefacts and a different accountability model (RA-accountable rather than ACP-accountable
at 1.6), and drawing it before a single engagement has completed First Wave would be speculative
rather than reviewable. This journey documents First Wave as it runs today; a later revision
documents the transition once enough engagements have completed to know what repeats and what
doesn't. **Effort S / Risk Medium** — the risk is First Wave quietly becoming permanent because no
step forces the transition; mitigated by naming the target state here so it stays on record.

## DD-17 — The Regional Architect rules pattern fit, at 1.2, before specification starts

Confirmed in review with ACP EA, RA and DA representatives. The decision on whether a use case's
solution fits an existing pattern moves **out** of the Enterprise Architect's assessment and **in**
to a step of its own at 1.2, owned by the **Regional Architect** — the only step in Phase 1 where RA
is accountable.

Three things follow, and they are the substance of this restructure:

1. **An exact match (1.2a) never reaches the Enterprise Architect.** It runs 1.3–1.6 and closes at
   1.9. Phases 1.7 and 1.8 are skipped entirely. This is the fast path DQ-1 asked for, which is now
   resolved.
2. **A new pattern (1.2b) obtains its governance approval first**, before discovery begins, rather
   than midway through the Enterprise Architect's assessment (DD-10).
3. **The Enterprise Architect's step becomes definition, not classification.** 1.7 defines the
   pattern and names its delivery owner. It is not a second fit decision and cannot reverse 1.2.

**Why the RA and not the EA.** The Regional Architect already performs the business-internal
assessment at 1.1 and holds the regional context the decision needs. Asking the Enterprise Architect
to rule fit meant every engagement — including the obvious ones — queued behind a single person, and
the latency was recorded as a risk from the first draft (D0 R-4).

**What it costs.** Fit is now judged by six regional architects rather than one enterprise architect,
against a catalogue that must therefore be readable without its author present (DD-8). A wrong call
at 1.2 sends an engagement down the short path with no later checkpoint to catch it — nothing
between 1.3 and 1.6 re-tests the finding. Whether that needs a checkpoint is **DQ-9**.
**Effort M / Risk Medium.**

## DD-18 — Delivery is communicated once, at 1.9, not narrated throughout

Also confirmed in the same review. The End User is **not** informed step-by-step through 1.8 — the
RACI shows EU absent from all three delivery rows — and instead receives a single closing
communication at 1.9, which also informs ACP EA, CT, RA and DA. ACP is both responsible and
accountable for it.

The reasoning is that delivery runs on ACP's or the Consortium's timeline, not the engagement's
(DD-4), and a consortium ask may not be accepted at all (DD-13). Narrating that to a business group
invites the reading that it has a decision to make at each turn, when it does not. What the business
group needs is the outcome and the confirmation it can now register — which is exactly what 1.9
carries.

This also gives Phase 1 a defined terminal step on **both** paths. Previously an exact-match
engagement simply stopped after the pattern decision, with no step that told anyone it had finished.
**Effort S / Risk Low** — the residual risk is silence during a long 1.8, which the interim-measure
mechanism in DD-13 partly covers.

## DD-19 — Entry prerequisites are checked before 1.1, as presence rather than approval

The business supplies two prerequisites before the journey starts: a completed **GenAI Risk Triage
Form** from Governance by Design (GbyD) and a ready **MBCT ID** from Model Risk Management (MRM).
The ACP Product Team checks that both are present, records the result, and onboarding begins. This
applies to any ACP platform instance — Luminate DEV as much as PROD.

**What the check is, and is not.** ACP confirms the two artefacts exist. It does not approve them,
re-run the triage behind them, or form a view on the risk they carry — those judgements belong to
GbyD and MRM, and neither team becomes a Phase 1 actor because ACP reads their output. Modelling
the check as an ACP approval was rejected: it would imply a second risk opinion the team is not
qualified to give and nobody asked for.

**Why it is a gate and not a step.** It is a precondition on entry rather than work the journey
performs, so it carries no step number and cannot renumber 1.1–1.9 (DD-7). It appears as **IP-0** in
the interaction register and as its own row in the responsibility model, because it crosses a team
boundary and someone must be accountable for it — but it sits outside the numbered sequence.

**The one case where onboarding does not start.** If either prerequisite is missing, onboarding
pauses until it arrives. This is expected to be rare — most use cases already hold both by the time
they approach ACP — and it is a pause, not a termination: nothing is rejected, and the engagement
begins as soon as the missing artefact is supplied. It is nonetheless the only point in this
document where work does not proceed, which is why it is drawn in the failure-and-exit table rather
than left implicit. **Effort S / Risk Low.**
