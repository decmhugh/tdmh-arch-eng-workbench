# Sun Life Deployment of Luminate - D0: Discovery

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: [EACPP-596](https://sunlife.atlassian.net/browse/EACPP-596)

## Problem Statement

Sun Life is partnering with three other companies to jointly develop a common
agentic control plane. The consortium's canonical product, **Luminate**, lives in
the AI Consortium's **GitHub Enterprise (GHE)** organization (the consortium has
adopted GHE and is migrating its existing GitHub organization into it) and is
deployed by upstream `luminate-deploy`
into a **self-provisioned** AWS EKS estate (own VPC, ALB+WAF, External Secrets +
AWS Secrets Manager, EKS Pod Identity, self-hosted Authentik, Tailscale).

Sun Life must run Luminate in its **own managed environment**, which differs
materially from upstream:

- **Managed EKS** (`slf-eks-t1k-ca-dev` / `-prod`) — Sun Life does not self-provision
  the cluster/VPC/nodepools.
- **Traefik / Gateway API** ingress (not ALB/WAF).
- **HashiCorp Vault (VSO)** for secrets (not ESO + Secrets Manager).
- **Okta / Entra** identity (not self-hosted Authentik).
- **IRSA** for pod AWS access (not EKS Pod Identity).
- **Jenkins JTE + Artifactory** CI/CD and registry (not GitHub Actions + ECR).
- **Bedrock via a consumer-account role-assumption model** (AWS Service Catalog
  product + aws-adapter/harness SDK), not centralized gateway-held credentials.

Deploying Luminate as-is is therefore not possible; a **re-packaged deployment**
plus Sun Life-specific supporting integrations is required. This spec captures the
**Sun Life Product Team** work breakdown to stand Luminate up in our environment.

## Opportunity

A working Sun Life deployment of Luminate lets us evaluate convergence on the
consortium product without re-owning its infrastructure assumptions. It provides:

- **A running reference** of Luminate on Sun Life managed EKS for evaluation.
- **Reusable platform patterns** — the Helm fork + Vault/Traefik/IRSA swaps become
  the template for any consortium workload we host.
- **An early read on the hard integrations** (identity, Bedrock consumer-account
  model) that gate any deeper adoption.
- **A clear contribution + artifact loop** (Bitbucket sync + Artifactory mirror)
  feeding the deployment.

## Stakeholders

| Stakeholder | Role | Key Concern |
| - | - | - |
| Sun Life Product Team | Implementers | Deploying Luminate into the SLF environment |
| Consortium Engineering | Partner / source owner | Upstream chart + code, contribution loop |
| Platform Architecture | Reviewers | Fit with managed EKS, ingress, secrets standards |
| Cloud Container Enablement | Provider | EKS namespaces, node capacity, Karpenter NodePools |
| DMS (Database Management Services) | Provider | Dedicated Langfuse + app PostgreSQL |
| Security / IAM | Governance | Okta onboarding, Vault paths, non-root, API Platform |
| AI Enablement | Consumer | Bedrock access via consumer-account model |

## Scope

### In Scope

- Analysis of the Luminate code and deploy repos for Sun Life fit.
- Infra prerequisites: dedicated Langfuse + app Postgres, namespaces/Karpenter,
  ClickHouse + S3 + Valkey, Vault paths, Okta app registrations.
- A **re-packaged deployment pipeline** — the forked `luminate-portal` Helm chart
  (`luminate-sunlife-deploy`) with Traefik/Gateway API, Vault VSO, IRSA, and
  API Platform onboarding, split dev/prod.
- Sun Life-specific supporting services: Bedrock consumer-account reconciliation,
  aws-adapter + aws-harness-sdk adaptation to the Luminate build.

### Out of Scope

- Contribution sync loop + Artifactory image mirror (Consortium Engineering — see
  the [sync design](../../../../Control%20Plane/internal-docs/Consortium%20Code%20&%20Artifact%20Sync%20Design.md)).
- Migration of components Luminate lacks vs our MVP (evaluation-api, governance
  forms, agent lifecycle) — Consortium Engineering migration strategy.
- Re-owning upstream base infrastructure (VPC/EKS/nodepools) — Sun Life uses
  managed EKS.
- Product decision on whether to converge on Luminate — this spec enables the
  evaluation, it does not make the decision.

## References

- [Deploy comparison (02)](../../../../Control%20Plane/internal-docs/consortium/02-luminate-deploy-vs-acp-deploy.md)
- [Alignment & assessment (04)](../../../../Control%20Plane/internal-docs/consortium/04-alignment-and-assessment.md)
- [30-day work breakdown (05)](../../../../Control%20Plane/internal-docs/consortium/05-luminate-deployment-30-day-plan.md)
- Deploy fork: `EDAEACP/luminate-sunlife-deploy` (`docs/fork-lineage.md`)
