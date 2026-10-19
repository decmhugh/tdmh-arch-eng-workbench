# Segregation of duties — DD-8, DD-15

## DD-15 · Four layers of authority, and no one person holds two of them for production

**Decision.** Authority over the topology is split into four layers, each held by different people
through different mechanisms. **No change reaches STAGE or PROD on one person's authority**: every
such change has a maker and a different checker, and the systems refuse a checker who is also the
maker or the owner.

| Layer | What it controls | Where it is enforced | Held by |
|---|---|---|---|
| **1 · Infrastructure administration** | AWS accounts, EKS clusters, Helm releases, Terraform, the deployment pipelines | AWS IAM Identity Center, EKS access entries, namespaced Kubernetes RBAC, Jenkins, Bitbucket | ACP platform team |
| **2 · Control-plane administration** | Environments, locations, folders, projects, gateway registration, gateway attachment in STAGE and PROD | Luminate RBAC | ACP platform team |
| **3 · Governance** | The rules that apply in each environment, and the verdicts and approvals given under them | Luminate RBAC, with approval verbs separated in code | Governance administrators (authoring) and governance approvers (deciding) — separate people |
| **4 · Business use** | A team's own agents, models, tools and applications, and their DEV and SIT deployments | Luminate RBAC, scoped to the team's folder and projects | Business teams |

Business teams never act in layers 1 or 2. They see no gateway administration, no environment
administration and no other team's project. What they see and can do follows from the role
bindings on their own projects.

## Personas

| Persona | Layer | Luminate role, at what scope | Infrastructure access | Can | Cannot |
|---|---|---|---|---|---|
| **Business viewer** | 4 | Viewer on the team's project | None | Read the team's catalogue, deployments and findings | Change anything |
| **Builder** | 4 | Editor (or a per-type Editor) on the team's project; **Gateway Attacher** on the DEV and SIT gateway projects | None | Register resources; deploy to DEV and SIT; create access policies; request promotion to STAGE and PROD | Deploy to STAGE or PROD; issue credentials; approve anything |
| **Project owner** | 4 | Owner on the team's project | None | Everything a builder can, plus issue DEV and SIT workload credentials, delegate roles within the project, and give first-level approval of the team's promotions | Deploy to STAGE or PROD; approve their own request |
| **Platform operator** | 2 | Platform Operator at organization | None by itself | Create and order environments and locations; create folders and projects for new teams | Touch catalogue resources, deployments, access policies, governance or secrets |
| **Gateway administrator** | 2 | Gateway Administrator on the gateway projects | Deploy pipeline (as maker) | Register gateways, map them to environments, rotate gateway credentials | Approve their own pipeline run |
| **Production deployer** | 2 | Gateway Attacher on the STAGE and PROD gateway projects, plus deployment and credential verbs | None by itself | Create STAGE and PROD deployments after their approvals are complete; issue the workload credential | Approve the promotion they are carrying out; deploy to DEV or SIT on a team's behalf |
| **Governance administrator** | 3 | Governance Administrator at organization | None | Author rules, scopes, frameworks and enforcement mode per environment | Approve, verdict or transition a resource |
| **Governance approver** | 3 | Governance Approver, Access Policy Approver and the per-type Approver roles, at organization | None | Approve or reject promotions, access policies and governance verdicts | Author the rules they approve under; approve their own request; approve a resource they own |
| **Release engineer** | 1 | None required | Jenkins member; support and operate tiers on each cluster | Author changes to `luminate-sunlife-deploy`; trigger pipelines; triage | Merge their own pull request; approve a STAGE or PROD pipeline run |
| **Release approver** | 1 | None required | Jenkins lead (`User_JenkinsProdACPLead_ML`) | Review and approve pull requests and STAGE and PROD pipeline runs | Approve a run they triggered |
| **Break-glass administrator** | 1, 2 | Superuser (one account) | Cluster-admin through the account's administrator permission set | Recover from an incident | Act without a ticket; act without a second person present |

**Gateway Attacher** and **Gateway Administrator** are custom roles built from existing permissions
(`deployments.gateway_attachment.*` and `gateways.gateway.*`). Every other role is a predefined
Luminate role.

## How Luminate enforces the environment boundary

**Deploying a resource needs authority over both ends of the attachment.** Creating a deployment
requires the typed create permission at the **resource's** project and
`deployments.gateway_attachment.create` at the **gateway's** project. The second grant is the
environment control.

**So gateways are placed in one project per environment:**

| Project, under folder *Luminate Platform* | Holds | Gateway Attacher held by |
|---|---|---|
| **Gateways — DEV** | `luminate-gateway-dev`, `luminate-gateway-us-dev` | Builders and project owners |
| **Gateways — SIT** | `luminate-gateway-sit`, `luminate-gateway-us-sit` | Builders and project owners |
| **Gateways — STAGE** | `luminate-gateway-stage`, `luminate-gateway-us-stage` | Production deployers only |
| **Gateways — PROD** | `luminate-gateway-prod`, `luminate-gateway-us-prod` | Production deployers only |

A business team therefore can stand a deployment up in DEV and SIT on its own, and cannot in STAGE or
PROD, whatever role it holds on its own project. That is the structural form of *self-serve below,
gated above* (DD-8). It is a role binding, not a convention: an attempt without the binding is
refused by the authorization layer and audited.

**Placing a gateway at a residency-labelled location is a governance action.** Under Data Residency
(AIC-1075), placing a gateway at a labelled `Location` takes the same governance authority as
changing a residency label. The platform team registers and runs the gateway; the placement also
needs the Governance Administrator, so a gateway cannot be moved into a region by one team alone.

## The rule for production

**A change to STAGE or PROD needs two people, and the platform refuses the second if they are the
first.** This holds at every layer:

| Change | Maker | Checker | Enforced by |
|---|---|---|---|
| Promote a resource into STAGE or PROD | Builder or project owner, by request | Project owner, then governance approver | Approval chain with `exclude_requester` and the `resource_owner` relation excluded at the governance level |
| Governance verdict on a resource | — | Governance approver | Separated-duty permissions: approval verbs are withheld from every authoring role in code |
| Create the STAGE or PROD deployment | Production deployer | The completed approval chain above | Gateway attachment granted only on the STAGE and PROD gateway projects |
| Change a STAGE or PROD gateway's configuration or version | Release engineer, by pull request | Release approver, on the pull request and on the pipeline run | Bitbucket required reviewers; Jenkins lead approval; a ServiceNow change (CHG) |
| Change STAGE or PROD infrastructure | Release engineer, by pull request | Release approver | As above, through the Terraform pipeline |
| Change the rules in force | Governance administrator | Governance approver | Approval policies are themselves approval-gated (`approval_policy` subject) |

**Walter's question, answered directly.** *Can one person manage both non-production and production?*

- **For a business team, no.** Its members hold deployment authority in DEV and SIT only. STAGE and
  PROD are reached by request, approved by someone other than the requester, and carried out by a
  production deployer who is not a member of the team.
- **For the platform team, not alone.** Platform engineers work across environments by design, but
  every STAGE and PROD change needs a different approver at the pull request, at the pipeline and,
  for the control plane, in the approval chain. The people holding standing production authority —
  Jenkins lead, production deployer, break-glass — are named groups that are re-attested every
  quarter.

## Infrastructure access per account

Production access is an AWS entitlement on the **prod account** only. Holding access to the dev
account confers nothing in the prod account, so the account boundary in DD-3 is also an access
boundary.

| Tier | Identity | Cluster authorization | Granted in |
|---|---|---|---|
| **Support** | `luminate-support` role | Read and logs in the Luminate namespaces | Each account |
| **Operate** | Same role, operate tier | Support, plus restart and delete pod | Each account |
| **Deploy** | `slf-t1kacp-eks-deploy` → `luminate-deployer` | Namespaced admin in the Luminate namespaces | Jenkins only, never humans |
| **Break-glass** | The account's administrator permission set | Cluster-admin | Ticketed and time-boxed |

The product team's day-to-day entitlement on the stage and prod accounts is the support role. The
cluster-admin permission set is not held for routine work.

## Change paths

Every change to a gateway, the control plane or their infrastructure goes through a pull request
to `luminate-sunlife-deploy` and a pipeline. There is no supported path that bypasses them.

| Change | Pipeline | DEV and SIT gateways | STAGE and PROD gateways, control plane |
|---|---|---|---|
| Gateway version or configuration | `luminate-gateway-deploy` | Pull request approved by another engineer | Pull request + release approver + CHG |
| Control-plane version or configuration | `luminate-sunlife-deploy` | — | Pull request + release approver + CHG |
| AWS infrastructure | `luminate-terraform` | Pull request approved by another engineer | Pull request + release approver + CHG |
| Verification | `luminate-smoke` | None (read-only) | None (read-only) |

**STAGE and PROD deploy only from `main`.** A STAGE or PROD pipeline run refuses any other
reference, so what runs in production is always what was reviewed and merged.

**Configuration in the portal is not code.** Registering an agent, creating an access policy or
approving a promotion changes what a gateway serves through the control plane's own audited
workflows. It deploys no code and needs no CHG. The control is the approval chain above.

## Attestation

| Cadence | What is re-attested | By |
|---|---|---|
| Quarterly | Holders of Administrator, Platform Operator, Gateway Administrator, production deployer, Governance Administrator and Governance Approver bindings | ACP product owner, with the governance lead for layer 3 |
| Quarterly | Jenkins lead group membership; break-glass holders; stage and prod account entitlements | ACP product owner |
| On every change of role | Remove the bindings the person no longer needs | Their manager, through the access request |

## DD-8 · Self-serve below, gated above

| Action | DEV | SIT | STAGE | PROD |
|---|---|---|---|---|
| Register a resource | Team | Team | Team | Team |
| Deploy | **Team** | **Team** | Production deployer, after approval | Production deployer, after approval |
| Create an access policy | **Team** | **Team** | Team, approval-gated | Team, approval-gated |
| Issue the workload credential | Project owner | Project owner | Production deployer | Production deployer |
| Set quotas | Tier defaults | Tier defaults | Tier defaults, platform-set | Platform-set |
| Promote into | **Team** | **Team** | Gated | Gated |

The gate sits between SIT and STAGE because that is where Sun Life's own change discipline begins:
STAGE is the first environment with real integrations, and enforcement starts there (DD-5).
