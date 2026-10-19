# Luminate Gateway & Environment Strategy — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: In review | **Epic**: EACPP-1089
> **Owner**: Sun Life ACP Product Team
> **Scope**: Where the gateways of the production Luminate control plane run, how the four workload
> environments are kept apart, who may act in each, and how a workload is promoted between them.

!!! note "Revised 2026-10-06"
    This D0 was first written on 2026-08-26, when the question was *which install owns business
    workloads*. That was settled by ADR-0031: the prod install. This revision records the state of
    the estate as measured on 2026-10-06, and the decision taken in the *Luminate Gateway
    Environment Deployment Model* session the same day to move each environment's gateways into
    that environment's AWS account.

## Why this revision

The Agentic Cloud Provisioning work (EACPP-1163) raised section 2.3 of the Infrastructure, Platform
and Network Security Directive against the deployment topology:

> Any new workload communication is strictly prohibited between new environments (e.g. Production,
> Stage, Non-production, Lab), as described in Appendix D, and requires authorized access and
> inspection layers. Legacy environments should adopt these requirements opportunistically.

The topology at the time placed **all eight gateways in the production account**, so every DEV,
SIT and STAGE workload talked to a production-account gateway, and those gateways called back into
non-production backends. A single control plane governing four environments is, by construction,
communication between environments. The question was where the middle ground lies.

### The 2026-10-06 session

**Attendees:** Seth Chalmers, Ranjula Rowel, Kieran Gibney, Kalev Gonvick, Walter Kurzatz, Anirban
Ukil, Gazelle Manavi-pour.

**Agreed:**

| # | Decision | DD |
|---|---|---|
| 1 | One production Luminate portal and control plane continues to govern every workload environment. Its region (`ca-central-1` today, or `us-east-1`) is still to be decided. | DD-1, DD-17 |
| 2 | Each environment's gateways move into that environment's existing workload account — dev, test, stage, prod — with a cluster in `ca-central-1` and `us-east-1` in each. | DD-3 |
| 3 | SIT maps to the test account. The test account can later carry a separate UAT if needed. | DD-2 |
| 4 | Each gateway calls Bedrock in its own account. | DD-3, DD-10 |
| 5 | The lower Luminate installs (dev, test, stage) are internal to the product team, for promoting Luminate releases. | DD-18 |
| 6 | Document the deployment model, the segregation of duties between platform administration and business use, the personas, the promotion process, and the policies and approvers. | DD-4, DD-15 |
| 7 | Submit a new ATG and ISRA specifically for this configuration. | Assurance |
| 8 | Move gateways to friendly hostnames, so promotion and gateway moves are transparent to business teams apart from the hostname. | DD-16 |

**Points raised, and where they are answered:**

| Raised by | Point | Answer |
|---|---|---|
| Gazelle Manavi-pour | Can a mistake by a business user or an administrator in the shared portal change production? | DD-15: business users hold no gateway or STAGE/PROD deployment authority; platform changes are maker-checker with a CHG for STAGE and PROD |
| Walter Kurzatz | Separate administrators for non-production and production; a policy that stops one person maintaining both | DD-15: structurally true for business teams; maker-checker and attestation for the platform team |
| Kieran Gibney | A pull-request model requiring a second approver for deployments | DD-15: required reviewers on `luminate-sunlife-deploy`, and STAGE/PROD deploys only from `main` |
| Kalev Gonvick | Does the account change affect the promotion process? | DD-4, DD-16: no, apart from the gateway hostname, which becomes a friendly name |
| Kieran Gibney | A single central portal means one defect or outage reaches every environment | DD-17: availability design, release promotion through the lower installs, and the consortium's outage design (ACPDIS-133) |
| Gazelle Manavi-pour | Availability of the dependencies outside EKS | DD-17: RDS Multi-AZ with point-in-time recovery; ClickHouse backed up to S3 |
| Anirban Ukil | Agree the approach with the directive owner's team before the ATG | Kieran Gibney relayed the directive owner's position: acceptable once the architecture and its security assessment are signed off |

## Current state — measured 2026-10-06

### Accounts and clusters

| Account | `ca-central-1` cluster | Runs today | `us-east-1` cluster | Runs today |
|---|---|---|---|---|
| dev `360967146904` | `slf-eks-t1k-ca-dev` | dev install (portal, Keycloak, its gateway, a second gateway for its SIT) | `slf-eks-t1k-use1-dev` | Nothing — platform layer only |
| test `692797214700` | `slf-eks-t1k-ca-uat` | test install | **None** | — |
| stage `775755739292` | `slf-eks-t1k-ca-stage` | stage install | **None** | — |
| prod `035722575935` | `slf-eks-t1k-ca-prod` | **Production control plane** and the DEV, SIT, STAGE and PROD gateways for `ca-central-1` | `slf-eks-t1k-us-prod` | DEV, SIT, STAGE and PROD gateways for `us-east-1` |

### The production control plane

| Fact | Detail |
|---|---|
| Version | Luminate `sha-093285b` (prod and dev), deployed from `luminate-sunlife-deploy` |
| Environments | Four rows, ordered dev, sit, stage, prod |
| Locations | `ca-central-1`, `us-east-1`, `Default` |
| Gateways | Eight, all active, all in project **Gateways** under folder *Luminate Platform* |
| Deployments | 15 — DEV 7, SIT 3, STAGE 2, PROD 3 |
| Predefined roles | 34, including Platform Operator, Governance Administrator, Governance Approver, Access Policy Approver and the per-type Approver roles |
| Approval policies | None configured |
| Elevated bindings | One organization-scope Administrator binding; one superuser |
| Business tenancy | Two business folders (*Data & Analytics*, *FDES*); every other onboarded team is on the **dev install** |

### The gateways

| Gateway | Where | Hostname | Reaches the control plane by |
|---|---|---|---|
| `luminate-gateway-dev`, `-sit`, `-stage` | prod account, `ca-central-1`, namespaces `luminate-gw-dev`, `-sit`, `-stage` | `gw-<env>.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com` | In-cluster service, plaintext gRPC under NetworkPolicy |
| `luminate-gateway-prod` | prod account, `ca-central-1`, inside the portal release | `gateway.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com` | In-cluster service |
| `luminate-gateway-us-*` (four) | prod account, `us-east-1`, namespaces `luminate-gw-<env>` | `gw-<env>.apps.slf-eks-t1k-us-prod.aws.sunlifecorp.com` | The portal's ingress hostname over TLS 443 — the pattern every out-of-cluster gateway will use |

Bedrock is in-account: every gateway in the prod account uses the prod account's hub role and
Bedrock. The `us-east-1` gateways validate tokens through a JWKS relay
(`k8s/keycloak-jwks-relay/us-prod`), because the signing-key address the portal pushes is an
in-cluster service name.

### Hostnames

All gateway hostnames are cluster names. The Venafi certificate on `slf-eks-t1k-ca-prod` already
carries the vanity SAN `luminate.sunlifecorp.com`, but its DNS record is blocked: the corporate zone
(BlueCat) cannot validate a CNAME into the Route 53 private zone. `jenkins-dna.sunlifecorp.com`
proves the pattern is possible. The us-east-1 relocation spec (EACPP-1407) proposes friendly portal
names for every install.

### Platform-side duties

From `luminate-sunlife-deploy/docs/operating-model.md`:

| Control | State |
|---|---|
| Jenkins: members trigger, leads approve STAGE and PROD | In place |
| `refTicket` (CHG or INC) on STAGE and PROD runs | In place, shape-checked only |
| Namespaced support and operate roles | In place, but the product team's administrator permission set still grants cluster-admin on stage and prod, so least privilege is advisory |
| Pull-request review on `luminate-sunlife-deploy` | One approval required to merge to `main`, but the project lead group is exempt from the branch rules and can push to `main` directly |
| Deploy reference for STAGE and PROD | Any branch is accepted |
| Pipeline-only changes to production | The release notes record four production deploys made directly with Helm, outside the pipeline, between 2026-10-03 and 2026-10-05 |
| Jenkins deploy credentials | Present for dev and prod; **absent for test and stage** |

### Luminate capabilities — what the target topology can build on

Read from `luminate` `origin/main` at `326ff763e` and checked against the deployed `sha-093285b`.

| Capability | State | Target-topology use |
|---|---|---|
| **Deployment RBAC with gateway attachment** — creating a deployment needs `deployments.gateway_attachment.create` at the gateway's project | Shipped | Per-environment gateway projects make deployment authority per environment (DD-15) |
| **Approval engine** — multi-level chains, approver pools from RBAC roles, requester always excluded, resource owner excludable, approval policies themselves approval-gated | Shipped; subjects are access policies, governance verdicts and approval policies | STAGE and PROD promotion approval (DD-4) |
| **Separated duties** — approval verbs withheld from authoring roles, checked at start-up | Shipped behind `RBAC_GOVERNANCE_MODE_ENABLED`, **off** in every Sun Life install | DD-15 |
| **Enforcement mode** per rule per environment, with impact-report acknowledgement | Switch shipped; **nothing denies on it yet** — access-layer enforcement is Governance Mode Epic H | DD-5 |
| **`CrossEnvironmentRule`** | Table and API only; **not evaluated** at access decisions | DD-6 |
| **Gateway identity in access decisions** | The gateway, environment and location are **taken from the request**; only the bearer is authenticated | DD-14 needs bound identity — consortium Federated Gateways design ACPDIS-124 (Draft) |
| **Signing-key address pushed to gateways** | One in-cluster URI for every gateway | DD-14 needs a gateway-reachable address |
| **Residency labels** (AIC-1075) | Shipped in `sha-093285b`, **off** | DD-10 |
| **Deployment provenance** | Absent | DD-4 |
| **`pre_prod` service tier** | Absent — the seeded domain is `prod` and `non_prod` | DD-2 |
| **Quota spend dimension** | Absent — requests and tokens only | DD-9 |
| **Authorization during a control-plane outage** | Designed upstream (ACPDIS-133) | DD-17 |

## Problem statement

1. **Gateways are in the wrong account.** Non-production and stage traffic, Bedrock use and operator
   access for those environments all sit in the production account.
2. **The cross-environment link has not been assessed.** No ATG or ISRA covers a single control
   plane governing gateways in other environments' accounts.
3. **Duties are not documented end to end.** The platform-side controls exist in the deploy repo,
   the portal-side controls exist in Luminate, and nothing states how they combine, who holds which
   role, or what stops one person changing production.
4. **The portal cannot yet separate deployment authority by environment**, because all gateways
   share one project, no approval policy is configured, and separated duties are switched off.
5. **Gateway trust assumes the production account.** The control plane believes a gateway's claims
   about its own identity, and gateways depend on an in-cluster signing-key address.
6. **Hostnames name clusters.** Moving a gateway breaks every agent configured with its address.
7. **Two clusters are missing.** The test and stage accounts have no `us-east-1` cluster.
8. **Tenants are on the dev install**, which is meant to be a platform-team sandbox.

## Stakeholders

| Stakeholder | Role | Concern |
|---|---|---|
| ACP Product Team | Owner and implementer | Topology, duties, promotion, delivery |
| ACP platform engineering | Operates the clusters, DNS and certificates | Accounts, clusters, friendly hostnames |
| Agentic Cloud Provisioning | Raised the directive question | Environment segregation of gateways |
| Session reviewers (Walter Kurzatz, Anirban Ukil, Gazelle Manavi-pour, Kalev Gonvick) | Reviewers | Segregation of duties; mistakes in a shared portal; availability of dependencies; the promotion process |
| Directive owner — Security Engineering and Advisory | Owner of IPNSD 2.3 | Signed-off architecture and assessment |
| Architecture governance (ATG) and information security (ISRA) | Approvers | This topology and its control link |
| Model Risk (CMRM) | Policy owner for STAGE and PROD gates | Policy as code; approval authority |
| Business teams | Consumers | A predictable promotion path; no change but the hostname |
| Cloud Container Enablement | Provider | The two missing `us-east-1` clusters |

## Dependencies

| Dependency | Owner | Risk |
|---|---|---|
| `us-east-1` EKS clusters in the test and stage accounts | Cloud Container Enablement | High — blocks the SIT and STAGE `us-east-1` gateways |
| Bound gateway identity | Consortium (ACPDIS-124) | High — must land before any gateway leaves the production account |
| Gateway-reachable signing-key address | Consortium | Medium — a relay works where the cluster has no Keycloak of its own, but not on the dev, test and stage clusters |
| DNS for friendly hostnames | Network / DNS (BlueCat) | Medium — the portal's vanity name is already blocked on the same issue |
| ATG and ISRA decisions | Architecture governance; information security | High — the topology change waits on them |
| The control plane's region | us-east-1 relocation (EACPP-1407) | Low for this spec — the design works with either answer |

## Open questions

- [ ] Does the ISRA require a Security Exception for the control link, or does the assessment itself
      satisfy section 2.3?
- [ ] Final friendly hostnames for the eight gateways.
- [ ] The control plane's region.
- [ ] Should the platform team also be split into non-production and production operators, beyond
      maker-checker? (DD-15 records the current answer: no, with attestation.)
- [ ] Does the test account need a separate UAT environment now, or later?
- [ ] Who holds Governance Approver for each policy domain on day one — Model Risk directly, or the
      platform team as steward until Model Risk takes it on?

## References

- Session: *Luminate Gateway Environment Deployment Model*, 2026-10-06 (recording and transcript)
- Directive: *Infrastructure, Platform, and Network Security Directive*, sections 1.3, 2.1–2.11,
  4.1, 4.3, 13 and Appendices C and D
- ADR-0031 *Platform vs Workload Environments*; ADR-0032 *Gateways in their environment's account*
- [`luminate-sunlife-deploy`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse) —
  `values/gateways/`, `pipeline_config_gateway.groovy`, `docs/operating-model.md`,
  `docs/us-region-enablement.md`, `deploy-checklists/prod.md`, `docs/release-notes.md`
- [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse) —
  `docs/building/promoting-your-agent.md`, `docs/personas.md`, `config/environments.yml`
- Luminate `origin/main` `326ff763e` — `backend/app/deployments/views.py`, `backend/app/approvals/`,
  `backend/app/governance/enforcement.py`, `backend/app/shared/permission_registry.py`,
  `backend/app/grpc_server/interceptors.py`, `backend/app/deployments/residency.py`
- Consortium designs: Federated Gateways and Data Residency (ACPDIS-124, Draft); Governance Mode;
  Portal RBAC (Approved)
- Related specs: `agentic-cloud-provisioning` (EACPP-1163), `us-cutover` (EACPP-1407),
  `sunlife-deployment` (EACPP-596), `self-service-onboarding` (EACPP-1325)
