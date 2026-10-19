# Environments, quotas and credentials — DD-7, DD-9

## DD-7 · Environments are shared tiers, and teams are separated by project

`Environment` has no project, folder or tenant key. The four environments are shared by every team,
and that is the right model for an SDLC: per-team environments would fragment the promotion path
and grow the cross-environment matrix combinatorially.

**Separation between teams is the project's job, not the environment's.** A team's resources,
deployments, access policies and usage are scoped to its projects (DD-11), and another team's DEV
deployment is invisible to it even though both are in DEV.

A genuinely private environment — a regulated pilot, a vendor sandbox — is expressed as a dedicated
gateway (Tier 2 of the scaling ladder, DD-3) serving a project-restricted audience, not as a new
environment.

## DD-9 · Quota defaults by tier

| Tier | Requests | Tokens | Spend | Intent |
|---|---|---|---|---|
| DEV | Low | Low | Low | Enough to build; visibly insufficient for load testing |
| SIT | Moderate | Moderate | Moderate | Integration runs |
| STAGE | Production-shaped | Production-shaped | Production-shaped | Meaningful verification |
| PROD | Sized to demand | Sized to demand | Budgeted | Real traffic, with headroom |

`Quota` binds to a target deployment, so tier defaults are applied when the deployment is created —
the moment promotion already touches. A STAGE or PROD quota above the tier default is an
approval-gated change.

**The account is a second, hard ceiling.** Each environment's Bedrock calls are made in its own
account (DD-3), so its spend is also bounded and visible by AWS account, and a DEV workload cannot
spend from the PROD account under any quota setting.

## Credentials across environments and regions

A workload credential is issued for one `(resource, gateway)` pair and shown once. Four
environments and two serving regions today means up to eight credentials per resource; each further region adds four.

| Event | Action |
|---|---|
| Promotion into an environment | A new credential for each target gateway |
| Rotation | Per gateway; rotating DEV does not touch PROD |
| Withdrawal | Deleting the deployment revokes its credential |
| Gateway moves to another cluster or account | **Nothing** — the credential is bound to the gateway record, not to where it runs (DD-3) |

Issuing the credential is the last step of a promotion (DD-4), so the secret is created exactly
when it is first needed and handed to the team that will use it.
