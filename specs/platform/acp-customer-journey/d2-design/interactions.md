# Interaction points and responsibilities

## Interaction points

Each row is a hand-off — a point where work crosses a team boundary and can therefore stall. These
are the rows to quote when a customer asks "who do I talk to, and when".

| # | Step | From → To | Trigger | Hand-off content | Response expected |
|---|------|----------|---------|------------------|-------------------|
| IP-0 | Entry gate | EU → ACP | Business requests ACP onboarding on any platform instance (Luminate DEV or PROD) | Completed GbyD GenAI Risk Triage Form and ready MRM MBCT ID | Presence confirmed and recorded — not approved. Onboarding starts, or pauses until the missing prerequisite arrives (DD-19) |
| IP-1 | 1.1 | EU → RA | Business group forms an AI idea | Business context | Regional architecture guidance |
| IP-2 | 1.2 | RA → ACP | Regional assessment complete | **Pattern-fit finding** — catalogues and applicable shapes considered, selected shape(s), fit evidence and open criteria; exact match (1.2a) or new pattern required (1.2b) | ACP opens the engagement on the corresponding path |
| IP-3 | 1.2b | RA → platform governance | A new pattern is required | Pattern intent and regional context | Approval request initiated — ATG / ISRA / PIA as applicable; a long-lead request may remain pending through discovery and design |
| IP-4 | 1.3 | ACP ↔ EU | Discovery session booked | Capability map walkthrough; use case presented | Confirmed capability requirements and `d0-discovery.md` |
| IP-5 | 1.3 | ACP ↔ RA | Runs parallel with IP-4 | Use case & requirements | Regional alignment |
| IP-6 | 1.3 | ACP ↔ DA | Runs parallel with IP-4 | The domains the use case touches | Early domain architecture input |
| IP-7 | 1.6 | ACP ↔ EU | `d2-design.md` drafted | Solution architecture presented for review | Confirmed design alignment, or requested changes |
| IP-8 | 1.7 | ACP → ACP EA | Design confirmed on a 1.2b engagement | Solution architecture + the 1.2b finding | Pattern definition and a named delivery owner |
| IP-9 | 1.7 | ACP EA → DA | Review opened | Architecture for domain review | Domain guidance |
| IP-10 | 1.7 | ACP EA → RA | Pattern definition underway | The pattern as drafted | Confirmation of regional context |
| IP-11 | 1.7 | ACP EA → ACP | Pattern defined | Pattern + **named delivery owner** | ACP or CT accepts delivery |
| IP-12 | 1.7 | RA → ACP | Pattern defined and 1.8 about to open | Status of the PIA / ISRA / ATG approval initiated at 1.2b-1 | ACP confirms approval before starting 1.8; delivery does not begin while it is pending |
| IP-13 | 1.8 | ACP → CT | The ask is classified a component change | Delta spec in `acp-consortium-specs` + a consortium idea | Prioritisation and a vote, then upstream delivery — not guaranteed, and not on ACP's timeline |
| IP-14 | 1.8 | CT → ACP | Accepted work lands upstream | The delivered capability in Luminate | ACP re-verifies, updates the capability map, closes the Sun Life ticket (DD-12) |
| IP-15 | 1.9 | ACP → EU, ACP EA, CT, RA, DA | The engagement reaches readiness on either path | Outcome, what was delivered, and that the use case is ready to register | Acknowledgement; the engagement closes (DD-18) |

IP-3, IP-8 through IP-14 are reachable only from **1.2b**. On an exact-match engagement the journey
runs IP-0, IP-1, IP-2, IP-4 to IP-7 and IP-15 — eight hand-offs rather than sixteen.

## Responsibility model

R = responsible, A = accountable, C = consulted, I = informed. **C/I** means the role is consulted on
part of a step and informed on the rest — at 1.1, 1.2 and 1.3 the ACP Enterprise Architect is
consulted on the architectural question and informed of the outcome.

| Step | EU | ACP | ACP EA | CT | RA | DA |
|------|----|-----|--------|----|----|----|
| Entry gate — prerequisite verification | **R** | **R/A** | – | – | – | – |
| 1.1 Business internal assessment | **A** | I | C/I | – | **R** | – |
| 1.2 Pattern-fit decision + governance approval | – | I | C/I | – | **R/A** | – |
| 1.3 Discovery & capability review | C | **R/A** | C/I | – | C | C |
| 1.4 `d1-requirements.md` | C | **R/A** | I | – | I | I |
| 1.5 `d2-design.md` | C | **R/A** | C | – | I | I |
| 1.6 Design review with End User | **R** | **R/A** | I | – | I | – |
| 1.7 Pattern assessment & definition | I | **R** | **A** | – | C | C |
| 1.8 Pattern delivery (integration track) | – | **R/A** | C | – | I | I |
| 1.8 Pattern delivery (consortium track) | – | **A** | C | **R** | I | I |
| 1.8 Consortium hand-back & re-verification | – | **R/A** | C | C | I | I |
| 1.9 Final delivery communication | I | **R/A** | I | I | I | I |

Three accountabilities are load-bearing and each is easy to misread.

**The Regional Architect owns 1.2** — the decision on whether the solution fits an existing pattern,
and the governance approval that follows when it does not. This is the only step where RA is
accountable, and it is the step that determines the shape of everything after it (DD-17).

**The ACP Enterprise Architect owns 1.7**, the definition of a new pattern and the naming of its
delivery owner — ACP cannot self-assign a new pattern. But the EA no longer rules existing-versus-new;
that moved to 1.2.

**On the consortium track the A stays with the ACP Product Team** even though the Consortium does the
building. ACP holds the Sun Life ticket, writes the delta spec and performs the close-the-loop
re-verification (DD-12), so it is the only party that can say the use case's requirement was met.

**The End User is not informed through 1.8.** That is deliberate, not an oversight: delivery runs on
the consortium's or ACP's timeline, and step-by-step updates invite the reading that the business
group has a decision to make. 1.9 carries the outcome to every party at once (DD-18).

The entry gate is a control before Phase 1, not a numbered journey step, and ACP checks that the two
prerequisites are present rather than approving them (DD-19). The six Phase 1 actors must confirm
their own rows before D2 sign-off (NFR-3); the record below tracks who has.

## Confirmation record

NFR-3 requires each actor to confirm its own rows, recorded with a name and a date. This is that
record, and `reviewers` in `spec.yaml` carries the same names at D2 sign-off.

| Actor | Confirmed by | Date | Scope |
|-------|--------------|------|-------|
| ACP EA | _to record_ | 2026-09-04 | Own rows; DD-17, DD-18 |
| RA | _to record_ | 2026-09-04 | Own rows; DD-17 |
| DA | _to record_ | 2026-09-04 | Own rows |
| ACP | _to record_ | — | Own rows |
| EU | — | — | **Outstanding** — rows are ACP's proposal |
| CT | — | — | **Outstanding** — rows are ACP's proposal |

A name here is the role holder at the time of confirmation. A change of individual does not
invalidate a confirmation already given, which is why the journey itself references roles rather
than people (D0 R-8).
