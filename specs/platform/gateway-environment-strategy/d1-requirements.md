# Luminate Gateway & Environment Strategy — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: In review | **D0 Approved**: TBD
>
> **Revised 2026-10-06** for the target topology agreed in the *Luminate Gateway Environment
> Deployment Model* session. Requirement IDs were renumbered; D3 cites the new IDs.

## Terminology

| Term | Meaning |
|---|---|
| **Control plane** | The production Luminate install: portal, backend, worker, identity, data and observability tiers. One of it. |
| **Install** | A whole copy of Luminate. Four: dev, test, stage (platform-team only) and prod (the control plane). |
| **Workload environment** | An `Environment` row in the control plane: DEV, SIT, STAGE, PROD. Unqualified, *environment* means this. |
| **Workload account** | The AWS account of an environment: dev, test (for SIT), stage, prod. |
| **Gateway** | A Luminate gateway serving one workload environment in one region, governed by the control plane. |
| **Control link** | The set of gateway-initiated connections from a gateway to the control plane (flows F-3 to F-8). |
| **Deployment** | A catalogue resource placed on a gateway in an environment. |

## Functional requirements

### Topology and placement

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | One production control plane governs every workload environment and region. No second install carries business workloads. | Must |
| FR-2 | The workload environments are DEV, SIT, STAGE and PROD, in that order, each tagged with its `service_tier`. SIT is served from the test account. | Must |
| FR-3 | Each environment has one gateway in each serving region. Today the serving regions are `ca-central-1` and `us-east-1`. | Must |
| FR-4 | Each environment's gateways run in that environment's AWS workload account. | Must |
| FR-5 | Each gateway calls Bedrock in its own account and region. | Must |
| FR-6 | Every workload account has an EKS cluster in each serving region. | Must |
| FR-7 | A gateway moves between clusters or accounts without changing its registered identity, its environment mapping or any workload credential issued against it. | Must |
| FR-8 | Provisioning a gateway creates its environment mapping in the same step, and the smoke test asserts it. | Must |
| FR-9 | The lower installs are used only by the ACP platform team, to test Luminate releases. | Must |
| FR-45 | A serving region can be added without a design change: a cluster in each workload account, a `Location`, one gateway per environment, hostnames, IAM and the control link, by a documented procedure. | Must |
| FR-46 | Each serving region has a short region code that is unique, never reused and never changed; it names the region's gateways and hostnames. | Must |

### Connectivity and trust

| ID | Requirement | Priority |
|---|---|---|
| FR-10 | The only communication between a gateway in a non-production or stage account and the production account is the control link: outbound, TLS 443, to enumerated production hostnames, authenticated by the gateway's own credential. | Must |
| FR-11 | Nothing in the production account initiates a connection into a non-production or stage account. | Must |
| FR-12 | The control link carries no prompt, completion, tool argument or tool result. | Must |
| FR-13 | The control plane decides every request for the gateway the credential proves and refuses a request whose gateway, environment or location claim disagrees. | Must |
| FR-14 | Gateways validate tokens using signing keys fetched from an address reachable and verifiable from every cluster. | Must |
| FR-47 | A provider credential served from a lower account is held in that account; the control plane holds only its name. | Should |
| FR-15 | Every gateway namespace carries a default-deny NetworkPolicy with an enumerated allow list. | Must |
| FR-16 | A call from one environment's resource into another environment is refused unless the published matrix allows it, and the refusal names the matrix. | Must |
| FR-17 | Every gateway is published on a friendly hostname that names its environment and region, independent of its cluster. | Must |

### Segregation of duties

| ID | Requirement | Priority |
|---|---|---|
| FR-18 | Authority is split into infrastructure administration, control-plane administration, governance and business use, each held through its own mechanism. | Must |
| FR-19 | Business users hold deployment authority only in DEV and SIT. | Must |
| FR-20 | Promotion into STAGE or PROD requires an approval that excludes the requester, and a governance approval that also excludes the resource's owner. | Must |
| FR-21 | No role that authors governance rules can approve under them, and the platform refuses to run if role definitions break that separation. | Must |
| FR-22 | Every change to a STAGE or PROD gateway, to the control plane, or to their infrastructure needs a reviewed pull request, a release approver distinct from the author, and a CHG. | Must |
| FR-23 | STAGE and PROD pipeline runs deploy only from `main`. | Must |
| FR-24 | Production infrastructure access is an entitlement on the production account only. Routine access is the namespaced support role, and cluster-admin is break-glass. | Must |
| FR-25 | Holders of standing production authority are re-attested every quarter. | Must |

### Promotion

| ID | Requirement | Priority |
|---|---|---|
| FR-26 | Promotion creates a new deployment of the same catalogue resource on the next environment's gateway, one step at a time. | Must |
| FR-27 | Promotion re-establishes credentials, quotas, access policies and the governance verdict in the target environment, and carries forward the resource, configuration, provenance and evidence. | Must |
| FR-28 | A promoted deployment records the deployment and environment it was promoted from. | Should |
| FR-29 | Promotion changes only the workload's gateway hostname and credential, never its code. | Must |
| FR-30 | The STAGE and PROD steps of a promotion are scripted and audited, not reconstructed from memory. | Must |

### Governance

| ID | Requirement | Priority |
|---|---|---|
| FR-31 | The same rules apply in every environment; they observe in DEV and SIT and enforce in STAGE and PROD. | Must |
| FR-32 | A team sees, in DEV and SIT, every finding that would block it in STAGE and PROD. | Must |
| FR-33 | Model Risk's pre-production checklist is encoded as rules evaluated at the STAGE and PROD gates. | Must |
| FR-34 | Each environment is verdicted in its own right; a STAGE verdict is evidence for PROD, never a substitute. | Must |

### Data isolation

| ID | Requirement | Priority |
|---|---|---|
| FR-35 | Prompt and completion content is removed from telemetry before it leaves the cluster. | Must |
| FR-36 | Telemetry is separated by environment, with a retention limit. | Must |
| FR-37 | A residency-labelled use case runs, and is recorded, only in its permitted regions. | Must |
| FR-38 | Whoever assigns a workload's regulatory regime records it as a governance attribute on the resource. | Should |

### Availability

| ID | Requirement | Priority |
|---|---|---|
| FR-39 | A gateway refuses every call it cannot get a decision for. | Must |
| FR-40 | The control plane runs across three availability zones, on a Multi-AZ database, with rehearsed recovery and alerting on gateway-observed refusals. | Must |
| FR-41 | Control-plane releases pass the dev, test and stage installs before production; gateway releases pass the DEV, SIT and STAGE gateways before PROD. | Must |

### Documentation

| ID | Requirement | Priority |
|---|---|---|
| FR-42 | The promotion path, the personas and the gateway hostnames are published for business teams in `luminate-user-guides`. | Must |
| FR-43 | The operating procedure for moving, adding and rotating a gateway is in `luminate-sunlife-deploy`. | Must |
| FR-44 | The architecture, decisions, controls and residual risks are kept in a form that can be submitted to ATG and ISRA without rework. | Must |

## Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-1 | **No fork of Luminate.** Every need is configuration, or a consortium ask. | Must |
| NFR-2 | **Default-deny** between environments, between namespaces, and from lower to higher trust. | Must |
| NFR-3 | **Blast radius by environment.** A failure or overload in one environment does not degrade another. | Must |
| NFR-4 | **Legible refusals.** Every refusal — unmapped gateway, matrix deny, governance block, quota, residency — names its cause. | Must |
| NFR-5 | **Auditable.** Every promotion, approval, deployment and gateway change is attributable to a person or a pipeline run. | Must |
| NFR-6 | **Transparent to business teams.** Moving a gateway changes nothing a business team configures. | Must |
| NFR-7 | **Cost-proportionate.** Lower environments are sized to their purpose. | Should |

## Constraints

- **One control plane.** Every gateway depends on it for every decision, by design.
- **Pod address ranges overlap across Sun Life EKS VPCs.** A gateway outside the control plane's
  cluster reaches it through the control plane's ingress hostname, not the pod network.
- **There is no wildcard DNS** on the Sun Life clusters. Every hostname is its own DNS record and
  certificate SAN.
- **The corporate DNS zone cannot validate a CNAME into a Route 53 private zone** through the
  standard request; a precedent exists for a non-validated CNAME.
- **The control plane's region** is decided by the us-east-1 relocation work (EACPP-1407).
- **Environment is not an RBAC scope.** Per-environment authority is expressed through the project a
  gateway belongs to.

## Out of scope

- Deploying or upgrading the control plane itself — `sunlife-deployment` (EACPP-596).
- Relocating the control plane to `us-east-1` — `us-cutover` (EACPP-1407).
- Gateways operated by business units — the consortium Federated Gateways design (ACPDIS-124).
- Authoring the content of Model Risk's rules — `acp-cmrm-policy-as-code` and
  `governance-content-packs`.
- Onboarding any specific use case.

## Open questions

- [ ] Does the ISRA require a Security Exception for the control link? *(FR-10)*
- [ ] Final friendly hostnames. *(FR-17)*
- [ ] Should platform operators be split into non-production and production groups? *(FR-18, FR-25)*
- [ ] Day-one holders of Governance Approver per policy domain. *(FR-20, FR-33)*
