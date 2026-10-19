# `docs/` — Agent Context

Scope: the living documents in this directory. Component specs live in `specs/` and follow a
different lifecycle (D0→D4 gates, PR per gate) — see the root `AGENTS.md`.

## The capability map is three documents, not one

| File | Publishes as | Answers | Verified against | Ages |
|---|---|---|---|---|
| `capability-map-summary.md` | ACP Capability Map — At a Glance | *What is the shape of coverage?* | Nothing — generated | n/a |
| `capability-map.md` | ACP Capability Map (Luminate) | *What can ACP do for my use case **today**?* | Built code on `AI-Consortium/luminate` `origin/main` | Per consortium release |
| `capability-roadmap.md` | ACP Capability Map — Future Roadmap | *What is **coming**, when, and what can I vote for?* | `luminate-designs`, `AIC` epics, `ACPDIS` ideas | Daily |

They are separate pages because they age at different rates. The roadmap used to be §6a of the
catalogue, and a roadmap that was three weeks stale made a catalogue that was still correct
look untrustworthy. In Confluence the summary is the parent and the other two hang off it.

**Refreshing any of them: `.github/skills/capability-map-refresh/SKILL.md`, or `/capability-map-refresh`.**
That skill carries the source-to-column mapping — which authority feeds which column of which
view — and is the thing to read before editing any of the three. Do not refresh one and skip
the others: a capability that reached ✅ on the catalogue and is still listed as upcoming on
the roadmap is the specific failure the split makes easy to introduce.

## Rules that keep them honest

1. **A status is a claim about running code.** ✅ means there is a runtime consumer on the
   request path that changes behaviour. A model, a serializer, an API field or a span
   attribute is ⚠️ — modelled, not enforced. That distinction is the whole point of the
   document, and it is the one that gets eroded first.
2. **Verify against `Code/Luminate/luminate` and `Code/Luminate/luminate-designs` `origin/main`.**
   Never the clones under `EDAE ACP/` — the `luminate` one has run 80+ commits behind and has
   already produced three wrong verdicts in a published spec. Never a feature branch.
3. **A design is not a schedule; an epic is not a decision.** Almost every design in
   `luminate-designs` is `Draft / Decision: Pending`. An `EACPP` epic is what Sun Life
   committed to; only an `AIC` epic is evidence the consortium agreed.
4. **Dates are release windows, not estimates.** Consortium epic dates cluster on a handful of
   days because that is how the squads bucketed release planning. Say "the window it currently
   sits in".
5. **Never hand-edit a generated artefact.** `docs/assets/capability-map*.svg|drawio` and every
   count on the At a Glance view come from `scripts/render_capability_map.py`, which parses §4
   of the catalogue and §1–§2 of the roadmap. A wrong number, or a roadmap card that
   disagrees with the ranked table, means a wrong source table or a skipped regeneration.
6. **Capabilities are confirmed, never inferred.** A meeting is where a refresh gets scheduled,
   not where a status gets decided. The rule and its failure mode are in
   `.github/instructions/capability-mapping.instructions.md`.

## Scripts that touch these files

| Script | Does | Never does |
|---|---|---|
| `render_capability_map.py --export` | Regenerates both diagrams from the tables | Reads Jira or the network |
| `refresh_roadmap_jira.py [--write]` | Rewrites the roadmap's date cells from live `AIC` epics; flags rows sitting in a section their epic's status contradicts | Moves a row between sections — that is a judgement about what the consortium agreed |
| `sync_to_confluence.py --capability-map` | Publishes all three plus the gap-escalation process | Guesses a parent page — a new standalone doc needs entries in **both** `STANDALONE_DOCS` and `STANDALONE_PAGE_PARENTS`, or it raises |

`CONFLUENCE_SPACE_KEY=T1KACP` must be set **inline** on the sync — the shared credential file
exports `DPEP`, which publishes into the wrong space without complaining.

HTTP calls in this repo go through `curl`, not `urllib`: Python's SSL on macOS rejects the
corporate CA chain. See `scripts/jira_http.py`.

## Other living documents here

- `process/capability-gap-escalation.md` — how a use-case need becomes an `ACPDIS` idea, and
  the component-change vs integration delineation that decides whether it is consortium scope
  at all. Published to Confluence alongside the map trio.
- `reference/` — OSFI B-10 / B-13 / E-13 / E-21 / E-23 source text. The authority for the
  Mandatory / Conditional / Optional column and for §7 regulatory traceability. Read it before
  arguing that something is a regulatory requirement.
- `adrs/` — MADR decision records. New ADRs are sequential and never renumbered.
- `templates/` — the D0–D4 spec templates. Changing a template does not retrofit existing specs.
- `process/portal-onboarding-ticket.md` — the T1 ticket every onboarding spec opens with. It
  lives under `process/`, not `templates/`, because MkDocs excludes any `templates/` directory
  from the built site.
