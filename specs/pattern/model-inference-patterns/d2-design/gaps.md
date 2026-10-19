# Gaps — what the target state requires from the platform

The pattern is the destination. This page names the capabilities it rests on and who owns each, so
that approving the pattern is not mistaken for assuming the platform already delivers every part of
it. The measured delta between here and now, with the work to close it, is [D3](../d3-tasks.md).

Split by owner, because the two halves move through different forums and at different speeds. A
dependency Sun Life can satisfy is a plan; one only the consortium can satisfy is an ask, and
conflating them produces a roadmap nobody can execute.

---

## Consortium — capabilities Luminate must provide

### D-1 · Budget enforcement on the inference path · **Critical**

The pattern's spend control is preventive: a call is refused when a matching budget is exhausted.
That requires a counter store, an atomic check that commits every matched counter together, window
strategies, a two-stage token charge that reserves then settles, a defined failure posture when the
counter store is unavailable, and a throttle response carrying retry guidance.

**Owner**: consortium — **AIC-20** (the enforcement mechanism), **AIC-43** (authoring, approval,
matching, retirement), **AIC-831** (the budget construct itself).

**Sun Life contribution**: **EACPP-834** — a generic `economics` app contributing rollups per
agent/model/tenant/team, budget definitions with soft-warn and hard-cap enforcement, chargeback and
showback reporting, spend-anomaly detection, and quota governance surfaced into the gateway policy
bundle. Sun Life is the member with the immediate chargeback requirement and the cost-centre
discipline to model it against, which makes it the natural contributor.

### D-2 · Spend as a first-class limit dimension · **Critical**

A budget must be expressible in money, not only in tokens or requests. Token price varies by model
and by token dimension, so a token cap bounds a quantity whose price it does not know.

**Owner**: consortium, with EACPP-834 as the contribution route.

> **D-1 and D-2 must land together.** A spend dimension without enforcement is telemetry;
> enforcement without a spend dimension can only cap tokens. Either alone leaves the business
> owner's commitment in [Budgets](budgets.md) unmet.

### D-3 · Complete token metering, including cache dimensions · **Critical**

Every token dimension the provider bills must reach the metering path. Cache reads and cache writes
are priced differently from ordinary input, and a path that records only prompt and completion
tokens under-bills cache-heavy callers specifically — which is a fairness failure, not just an
accuracy one.

**Owner**: consortium — **AIC-679**.

### D-4 · Per-run cost attribution · Medium

The ledger aggregates by UTC day, which is the right grain for finance. Answering *"what did this
run cost"* needs cost at session grain, which the session record does not currently carry.

**Owner**: consortium. **Interim**: MIR-15 — callers supply a session identifier so the correlation
exists in traces even where the ledger cannot aggregate it.

### D-5 · Scoped authorization for the cost surface · Medium

The chargeback surface exposes per-user spend joined to employee email. It needs a scoped
permission rather than a broad administrative one, so the audience is a deliberate grant.

**Owner**: consortium for the permission; **Sun Life for the decision** on the acceptable audience —
see residual **R-6** in [Assurance](assurance.md).

---

## Sun Life — what we own

### D-6 · Inference reachable from the ACP account, per region · **Critical**

Centralized inference requires the provider to be invocable from the ACP production workload
account, in each region a gateway serves. Where an organisation-level control prevents that, lifting
it is a governance decision rather than a configuration change — and the decision must be taken per
region, because the gateway topology is per environment per region.

### D-7 · A priced catalogue, kept current · **Critical**

Every reachable model carries a per-token price for every billed dimension, with a named source and
a refresh date. Provider rate cards change; a stale price produces a wrong bill silently, so drift
detection is part of the dependency, not an enhancement to it.

### D-8 · Cost-centre discipline · **Critical**

Every project that can incur inference spend carries a cost centre in the finance system's own
coding, validated at project creation rather than asserted by convention. It is the single field
joining ACP to finance.

### D-9 · The hand-off to the enterprise chargeback pipeline · **Critical**

The pipeline consumes cost-centre-coded spend and gives finance its single view. ACP must deliver
into it: the receiving interface, the format, the cadence and the finance owner.

**This is the dependency the consortium will not close.** The upstream attribution work is explicit
that chargeback and invoicing are out of its scope, so the pipeline integration is Sun Life's by
construction, not by omission.

### D-10 · The reconciliation practice · **Critical**

A per-period comparison of the ACP figure against the provider invoice, an agreed per-model
tolerance, and the charge gate in front of it. Without this there is no basis for the rule that an
unreconciled period is not charged.

### D-11 · Directory-group integration for human access · Medium

Human access is granted through directory groups, which requires group resolution, group-to-policy
mapping, and defined behaviour when membership changes mid-session.

### D-12 · Residency positions per region · Medium

Each region a gateway serves needs a recorded residency position, because centralized routing means
ACP chooses the region on the consumer's behalf.

---

## Summary

| # | Dependency | Owner | Criticality |
|---|---|---|---|
| **D-1** | Budget enforcement on the inference path | Consortium (AIC-20/43/831) + EACPP-834 | **Critical** |
| **D-2** | Spend as a limit dimension | Consortium + EACPP-834 | **Critical** |
| **D-3** | Complete token metering, cache included | Consortium (AIC-679) | **Critical** |
| **D-4** | Per-run cost attribution | Consortium | Medium |
| **D-5** | Scoped authorization for the cost surface | Consortium **+ SLF decision** | Medium |
| **D-6** | Inference reachable from the ACP account, per region | **Sun Life** | **Critical** |
| **D-7** | A priced catalogue, kept current | **Sun Life** | **Critical** |
| **D-8** | Cost-centre discipline | **Sun Life** | **Critical** |
| **D-9** | Hand-off to the enterprise pipeline | **Sun Life** | **Critical** |
| **D-10** | Reconciliation practice and charge gate | **Sun Life** | **Critical** |
| **D-11** | Directory-group integration | **Sun Life** | Medium |
| **D-12** | Residency positions per region | **Sun Life** | Medium |

**Seven of twelve are Sun Life's, and five of the seven are critical.** The attribution half of this
pattern is almost entirely ours to deliver; what we genuinely need from the consortium is
**enforcement** (D-1, D-2) and **metering completeness** (D-3). That distribution is worth stating
plainly, because the instinct with a consortium platform is to assume the platform will bring the
capability — and here, for the part that matters most commercially, it will not.
