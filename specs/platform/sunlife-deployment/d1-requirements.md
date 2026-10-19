# Sun Life Deployment of Luminate - D1: Requirements

> **Gate**: D1 - Requirements | **Status**: Draft | **Epic**: [EACPP-596](https://sunlife.atlassian.net/browse/EACPP-596)

## Scope

This D1 spec defines the requirements for deploying and operating the consortium
**Luminate** platform in the Sun Life environment, covering the deploy fork, infra
prerequisites, platform integrations (ingress, secrets, identity), the Langfuse
data tier, and Bedrock adapter integration. It is the requirements basis for the
Sun Life Product Team work breakdown delivered in [D3](d3-tasks.md).

| Area | Description |
| - | - |
| Deploy packaging | Forked `luminate-portal` Helm chart on managed EKS, split dev/prod |
| Infra prerequisites | Dedicated Langfuse + app Postgres, ClickHouse, S3, Valkey, namespaces |
| Ingress | Traefik / Gateway API (replaces upstream ALB + WAF) |
| Secrets | Vault VSO (replaces upstream ESO + Secrets Manager) |
| Identity | Okta / Entra + light-proxy **at the edge**; a self-hosted IdP (Keycloak / Authentik) stays for internal M2M only — approved under ATG0005518 |
| Pod AWS access | IRSA (replaces EKS Pod Identity) |
| Observability | Langfuse (ClickHouse + S3 + dedicated Postgres) |
| Bedrock | Consumer-account role-assumption model via aws-adapter / harness SDK |
| API Platform | Okta-enforced onboarding of the HTTP surfaces |

**Out of scope:** contribution sync loop + Artifactory mirror (Consortium Eng);
component migration for MVP-only features; the convergence decision itself.

## Functional Requirements

| ID | Requirement | Priority |
| - | - | - |
| FR-1 | The forked `luminate-portal` chart SHALL deploy to managed EKS via `helm upgrade --install` with per-env values (`values/values-<env>.yaml`). | Must |
| FR-2 | **Platform** environments SHALL each have their own EKS cluster, namespace, credential and approval gate. Four exist: dev, test/UAT, stage, prod. These are installs of Luminate itself — **not** the workload environments a business team promotes through, which are defined in `gateway-environment-strategy`. | Must |
| FR-3 | Ingress SHALL be provided by Traefik / Gateway API `HTTPRoute`; the chart's ALB Ingress templates SHALL NOT be used. | Must |
| FR-4 | Secrets SHALL be materialized from Vault via VSO `VaultStaticSecret`; the chart's ESO path SHALL be disabled. | Must |
| FR-5 | Pod AWS access SHALL use IRSA role ARNs on service accounts (not Pod Identity). | Must |
| FR-6 | The HTTP surfaces (portal API, gateway API) SHALL be onboarded to the Sun Life API Platform with Okta JWT enforcement via the light-proxy sidecar. | Must |
| FR-7 | Langfuse SHALL be deployed with ClickHouse, S3 blob storage, and a **dedicated** Postgres database (not the shared ACP Postgres). | Must |
| FR-8 | The gateway SHALL obtain Bedrock access via the Sun Life consumer-account role-assumption model (aws-adapter / harness SDK), not centralized gateway-held credentials. | Must |
| FR-9 | The deployment SHALL be driven by a Jenkins deploy job (`EDAEAgentControlPlane/luminate-deploy-cd`) consuming images mirrored to Artifactory. | Must |
| FR-10 | The gRPC control plane (backend↔gateway `:50051`) SHALL remain internal, permitted by NetworkPolicy (not API Platform onboarding). | Must |
| FR-11 | Initial bring-up MAY deploy backend + frontend only, enabling gateway + worker once Vault secrets and the chart secrets-guard edit land. | Should |

## Non-Functional Requirements

| ID | Requirement | Priority |
| - | - | - |
| NFR-1 | **Security** — all container images run non-root and pass Gatekeeper/SCC; no secrets on nodes or in images. | Must |
| NFR-2 | **Secrets custody** — all credentials sourced from Vault; rotation-capable. | Must |
| NFR-3 | **Environment parity** — dev and prod differ only by values/overlays, not chart structure. | Must |
| NFR-4 | **Egress** — HTTPS-only through the corporate proxy; images pulled from Artifactory. | Must |
| NFR-5 | **Change control** — prod deploys require a change ticket + lead-group approval. | Must |
| NFR-6 | **Upstream sync** — the fork SHALL be re-syncable against upstream chart changes with a documented diff/re-apply process. | Should |
| NFR-7 | **Observability** — deployed workloads expose health + metrics; Langfuse traces flow. | Should |

## Constraints & Assumptions

- Managed EKS (`slf-eks-t1k-ca-dev/-prod`); Karpenter is installed but no NodePools
  are defined today (nodes via managed node group).
- Account `360967146904` has an SCP deny on Bedrock — Bedrock testing uses a
  separate account via the consumer-account role model.
- Deploy credentials `luminate-eks-deploy-aws-{dev,prod}` and dedicated Postgres,
  Vault paths, and Okta apps are **prerequisites** not yet provisioned.

## Appendix A — Sun Life Platform Bindings

| Concern | Binding |
| - | - |
| Cluster | `slf-eks-t1k-ca-dev` / `slf-eks-t1k-ca-prod` (ca-central-1) |
| Namespace | `luminate` |
| Ingress | Traefik / Gateway API |
| Secrets | Vault (VSO) — `kubernetes/slf-eks-t1k-ca-<env>/360967146904/luminate/*` |
| Registry | Artifactory (`consortium-docker` virtual repo) |
| CI/CD | Jenkins `EDAEAgentControlPlane/luminate-deploy-cd` |
| Deploy repo | `EDAEACP/luminate-sunlife-deploy` |
