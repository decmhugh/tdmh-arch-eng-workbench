# Operations — running centralized inference

What has to happen on a cadence, by whom, for the pattern to keep being true after go-live.

## The operational surface

Centralized inference adds three recurring obligations that distributed inference does not have,
because in the distributed shape AWS performs all three implicitly.

| Obligation | Cadence | Owner | Fails how |
|---|---|---|---|
| **Rollup health** — the ledger is materialized for every day | Daily | ACP Platform | Silently. A missing day is an unbilled day and the report still renders |
| **Reconciliation** — ACP total vs provider invoice | Per period, before any charge | ACP Product + Finance | Loudly, if anyone looks. This is the control that catches metering drift |
| **Unattributed review** — spend in the null-project bucket | Per period | ACP Product | Silently. It accumulates as platform cost |

## Rollup health

The ledger is worker-materialized, not queried live. That is the right design — it makes the report
fast and the period stable — and it introduces a failure mode the live-query design does not have:
**a day that never rolled up is indistinguishable, in the report, from a day with no usage.**

The check is therefore not "did the report render" but "is there a row for every day that had
traffic".

## Reconciliation

Specified in [Attribution](attribution.md); the operational point is that it **gates charging**
(MIR-14). An unreconciled period produces showback, not a charge.

Worth protecting against a predictable pressure: when a period fails reconciliation, the tempting
response is to charge anyway and correct later. Correcting a charge after a business unit has
booked it costs more credibility than the delay does, and the second correction is never believed.

## Unattributed spend

The null-project bucket is selectable by design. In the distributed shape it barely exists — AWS
attributes everything to an account. **Centralization is what makes it grow**: any call whose
principal does not resolve to a project lands there, and the platform absorbs it.

Treat the unattributed share as a **service level** (NFR-4) with an agreed ceiling, not as a
curiosity. A rising share is the leading indicator that onboarding has outrun the cost-centre
discipline.

## Access review

Per MIR-34, joined against the usage ledger: grants with no traffic in the period are challenged.
Cheap to run once the ledger is populated, and the natural place to catch a pilot's `all_users`
policy that was never removed.

## Incident response

| Situation | Response |
|---|---|
| A workload is misbehaving or compromised | **Revoke the grant or the credential.** A budget bounds spend, not damage |
| Spend approaching a limit | The soft-warn fires before the cap; raise the limit deliberately or let it stop |
| Metering found wrong for a model | Stop charging for it, restate the affected periods, fix the metering, re-reconcile before resuming |
| A model must be withdrawn urgently | Remove the grant first (immediate), then the catalogue entry; notify callers, who will otherwise see it as an outage |
| Rollup stalled | Backfill before the period closes; a late rollup is recoverable, a missed period is a restatement |

## What makes this sustainable

The operational load is dominated by **reconciliation and unattributed review**, and both scale with
the number of *cost centres*, not the number of calls. That is the argument for keeping the project
as the billing unit: it bounds the recurring work to something that grows slowly, where a per-user
or per-AD-group billing model would grow with headcount.
