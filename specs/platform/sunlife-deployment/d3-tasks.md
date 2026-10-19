# Sun Life Deployment of Luminate — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **Epic**: [EACPP-596](https://sunlife.atlassian.net/browse/EACPP-596)

## Scope

This implementation plan turns the [D2 design](d2-design.md) into sprint-ready work
for the **Sun Life Product Team** to deploy Luminate into the Sun Life environment.
It is derived from the product-team lane of the
[30-day work breakdown](../../../../Control%20Plane/internal-docs/consortium/05-luminate-deployment-30-day-plan.md)
(workstreams PT-1…PT-4). The Consortium Engineering lane (sync loop, artifact
mirror, component migration) is tracked separately.

### In Scope

- Analysis of the Luminate code + deploy repos for Sun Life fit.
- Infra prerequisites (Postgres, namespaces/Karpenter, ClickHouse/S3/Valkey, Vault, Okta).
- The re-packaged deploy pipeline (`luminate-sunlife-deploy` Helm fork + Jenkins job).
- Sun Life supporting services (Bedrock consumer-account model, aws-adapter + harness SDK).

### Out of Scope

- Contribution sync loop + Artifactory image mirror (Consortium Engineering).
- Migration of MVP-only components (evaluation-api, governance forms, agent lifecycle).
- The convergence decision itself.

---

## Implementation Status Cross-Reference

> Dev capability state as of **2026-08-12**, verified against the live dev cluster
> `slf-eks-t1k-ca-dev` (namespaces `luminate`, `authentik`, `luminate-observability`).
> Environment promotion below re-verified live **2026-08-20** across all four accounts.
> **The full portal stack — backend, frontend, gateway, DBOS worker, Authentik and the
> Langfuse/ClickHouse observability tier — is LIVE on dev.** Remaining dev gaps are
> secrets management (Vault VSO), image signing, and the edge/API-platform lane.

| Capability | Current State | D3 Action |
|------------|---------------|-----------|
| Forked Helm chart | ✅ `luminate-sunlife-deploy/helm/luminate-portal` (upstream@e91a7d0), `docs/fork-lineage.md` published | Maintain + sync (T4 done) |
| Deploy pipeline | ✅ `Jenkinsfile_deploy` + `pipeline_config_deploy.groovy` (dev/prod) | Cut over manual→Jenkins (T24) |
| Jenkins job | ✅ `EDAEAgentControlPlane/luminate-deploy/luminate-sunlife-deploy` | Add folder AWS creds (T8) |
| App images | ◐ SLF ECR `luminate/{backend,frontend,gateway,pii-detector,authentik-server,dbos-worker}` — **interim** and **unsigned** | Artifactory/GHCR mirror (T20) · sign + drop Connaisseur bypass (T23) |
| Deploy (full stack) | ✅ **LIVE** on dev — backend 2/2, frontend 2/2, gateway 3/3, dbos-worker 2×1/1 (`luminate-portal` rev 17) | Cut over to Jenkins (T24) |
| Ingress (Traefik) | ✅ HTTPRoutes `luminate-portal-portal`, `luminate-gateway`, `authentik`, `keycloak`, `langfuse` on the shared `traefik-gateway`; DNS Alias live for all hosts incl. `keycloak.apps.…` (2026-08-24); portal + `/api/schema/` return 200 | Re-home ALB WAF/access-logs (T11 residual); **Venafi certs missing for `keycloak.apps.…` and `gateway.apps.…` — both fall back to the self-signed `slf-eks-wildcard-tls` (T37, T38)** |
| Postgres | ✅ dedicated RDS `slf-ca-mo-dms-pd-acp-luminate:7620` (PG 17.9), role `luminate`, `sslmode=require`, `search_path=luminate`, `dbos` schema present, `public` unused | Done (T6/T28/T29/T32) |
| Connection sizing | ✅ direct connection (no transaction-mode pooler); `max_connections=1702`, ~71 in use | Done (T33) |
| Secrets (Vault VSO) | ⚠️ plain in-namespace Secrets (`secrets.plain=true`); **no `VaultStaticSecret` in `luminate`/`authentik`** | Vault paths + secrets-guard edit (T7) |
| Secrets (provider credentials) | ❌ `CREDENTIAL_BACKENDS` unset — the portal's Secrets page offers no backend, so every model offering must be keyless | Enable the Vault credential backend (T40) |
| Identity — human SSO | ✅ Entra/Azure AD OIDC wired (`SSO_OIDC_PROVIDER_ID=portal-luminate`, tenant `415bb08f…`) | Done (T21) |
| Identity — M2M | ✅ **Keycloak** live in the `keycloak` namespace; `SERVICE_PRINCIPAL_AUTH_*` points at its OIDC issuer + JWKS | Done (T22) |
| IRSA | ◐ `luminate-observability` SAs annotated (`clickhouse`, `langfuse-sa`); `luminate` app SAs still unannotated | Chart SA IRSA support (T7) |
| Langfuse tier | ✅ **LIVE** in `luminate-observability` — Altinity operator, CHI + Keeper, langfuse web/worker, S3 blob + backup buckets, backup CronJob green, traces landing in ClickHouse | Done (T5/T13) |
| API Platform onboarding | ❌ not started; portal exposes one OpenAPI spec at `/api/schema/` | Light Proxy edge (T25) + Okta onboarding (T26) + API Platform publish (T12) |

### Environment promotion

Dev is the reference deployment. Promotion to the remaining environments is tracked by one
ticket per environment, each with a subtask per prerequisite. Runbooks now live **in the deploy
repo** at `luminate-sunlife-deploy/deploy-checklists/` (promoted out of a local-only folder on
2026-08-20 so all four environments share one source of truth):
[dev.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/dev.md) ·
[test-uat.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/test-uat.md) ·
[stage.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/stage.md) ·
[prod.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/prod.md).

| Env | Account | Cluster | State (verified 2026-08-28) |
|-----|---------|---------|--------------------|
| TEST/UAT | `692797214700` | `slf-eks-t1k-ca-uat` | ✅ **DEPLOYED** — portal, Authentik, observability tier and the AI gateway (cross-account Bedrock) all live |
| STAGE | `775755739292` | `slf-eks-t1k-ca-stage` | ✅ **DEPLOYED** — same footprint; Valkey HA, Langfuse verified end to end, Bedrock Converse 200 |
| PROD | `035722575935` | `slf-eks-t1k-ca-prod` | ✅ **DEPLOYED** — backend, frontend, gateway and dbos-worker all `1/1`+; direct Entra ID SSO; Keycloak deployed and usable as the internal M2M issuer |

> ⚠ The cluster name for test/UAT is **`slf-eks-t1k-ca-uat`**, not `-test`. An earlier revision
> of this doc recorded both TEST/UAT and STAGE as *"blocked — EKS cluster does not exist"*; both
> clusters were in fact created and both environments are now fully deployed.

**Remaining gaps are identical across test/UAT and stage** and are all platform requests, not
deploy work: DNS records (both hosts NXDOMAIN — reachable only via `curl --resolve`), the
Jenkins `acp-eks-deploy-aws-{test,stage}` credential (both were deployed by hand with SSO),
Vault/VSO onboarding (both run on interim plain Secrets), and an Entra SSO app registration
(both use the breakglass admin).

---

## Tasks

### PT-1 · Analyze Luminate repos

| Task | Description | Depends |
|------|-------------|---------|
| **T1** | Deep read of `luminate` (Django apps, gateway, worker, pii) — component/runtime inventory, boot dependencies. | — |
| **T2** | Deep read of `luminate-deploy` (Helm + TF) — enumerate chart assumptions to swap. | — |
| **T3** | Produce the per-service config/env-var inventory + minimal boot config for our cluster. **✅ Done** — backend/worker/gateway ConfigMaps + Secrets in the chart drive all boot config on dev. | T1 |

### PT-2 · Infra prerequisites

| Task | Description | Depends |
|------|-------------|---------|
| **T4** | Maintain the forked chart; document upstream-sync process (`docs/fork-lineage.md`). **✅ Done** — fork lineage documented; sync process in place. | — |
| **T5** | Provision the Langfuse data tier: **Altinity ClickHouse operator + ClickHouseInstallation CR + ClickHouse Keeper** (self-managed in-cluster); **4 dedicated S3 buckets** (events, media, exports, backup — KMS-enforced, IRSA access); **ElastiCache Valkey** (engine 7.2, primary+replica, Multi-AZ, TLS+AUTH, `maxmemory-policy noeviction`) for the Langfuse v3 BullMQ queue/cache. **✅ Done** — live in `luminate-observability`: Altinity operator 0.27.2, CHI `chi-langfuse-default-0-0-0` + Keeper `chk-langfuse-keeper-keeper-0-0-0`, S3 `dev-360967146904-acp-luminate-langfuse` + `-backup`, ElastiCache `slf-t1kacp-luminate-dev-redis`, IRSA roles `slf-t1kacp-luminate-dev-{clickhouse,langfuse}-irsa` bound to the SAs. | — |
| **T6** | Request the dedicated **`luminate` app Postgres DB** (per-instance request to the Sun Life Postgres team; DD-8). **Named app role (not `postgres`)**, **app schema + a `dbos` schema**, role **owns its schema(s)** / has DDL. No superuser — the schema is **team-created**, not auto-managed; password from the Sun Life secret store. | — |
| **T7** | Vault + secrets. **Option A** — keep the chart's ESO and point the SecretStore **provider spec at Vault** (no secrets-guard edit needed). **Option B** — replace with VSO `VaultStaticSecret` (`secrets.enabled=false` + guard edit). Add IRSA roles + SA annotations. | T6, T18 |
| **T8** | Create Jenkins folder AWS credentials `luminate-eks-deploy-aws-{dev,prod}`; ensure namespace RBAC for the deploy user. | — |
| **T18** | Request the dedicated **`langfuse` Postgres DB** (per-instance request; DD-8) — separate from the app DB (T6). **Named `langfuse` role + schema** (role owns schema / has DDL); no superuser; password from the Sun Life secret store. | — |
| **T19** | Request EKS namespace(s) + node capacity for Luminate — tracked in CCE-1047 (already submitted). **✅ Done** — `luminate`, `authentik`, `luminate-observability` all Active with capacity. | — |
| **T20** | Set up the Artifactory mirror pulling partner images from the AI Consortium **GitHub Enterprise** / GHCR (ghcr.io → `consortium-docker`) per the Consortium Code & Artifact Sync Design. Consortium-Engineering-owned; prerequisite for T9/T10. **Still open** — dev currently pulls from SLF ECR, which is an **interim** arrangement; the Artifactory/GHCR integration remains the target state for every environment. | — |
| **T27** | Request the **`authentik` Postgres DB** (per-instance request; DD-8) — **named `authentik` role + schema**, role owns schema / has DDL. Required wherever Authentik is the M2M issuer (approved — ATG0005518 / ISRA 26-1565, [EACPP-747](https://sunlife.atlassian.net/browse/EACPP-747)). **✅ Done** — `authentik` DB co-located on the luminate RDS instance; Authentik server + worker running against it. | — |
| **T28** | Add **`POSTGRES_SCHEMA` / `search_path` support** to the backend `DATABASES` (inject `OPTIONS["options"]="-c search_path=<schema>"`), inherited by the worker — the app cannot use `public` on Sun Life Postgres (DP-2). Confirm Langfuse/Prisma honours a role-level `search_path`. **✅ Done** — solved at the **role level** (`ALTER ROLE luminate SET search_path = luminate`) rather than via app `OPTIONS`; verified live: `show search_path` → `luminate`, `public` unused. | T1 |
| **T29** | Resolve DBOS's **`dbos` schema** in the `luminate` DB (DP-3): grant the app role `CREATE` so DBOS auto-creates it at boot, or have the Postgres team pre-create a `dbos` schema owned by the role. **Confirm the `dbos` name is fixed/acceptable** vs the naming convention (the request form asks for one schema). **✅ Done** — `dbos` schema present in the `luminate` DB alongside `luminate`; DBOS worker running. | T6 |
| **T30** | Remove/disable the `langfuse` + `authentik` **DB-bootstrap Jobs** and the portal's `POSTGRES_USER=postgres` master assumption (DP-1); connect every consumer as its **team-provided named role**, password from the Sun Life secret store via VSO (drop the password-setting bootstrap logic; keep Reloader) (DP-6). | T6, T18, T7 |
| **T31** | Rework/drop the **`clear-migrations` reset Job** (`DROP SCHEMA public CASCADE …`) — incompatible with a named, team-owned schema + non-superuser role (DP-4). First-deploy relies on the team's empty schema + `migrate`; ensure each role **owns its schema / has DDL** for Django (`django_zero_downtime_migrations`), DBOS, and Prisma boot DDL (DP-5). **✅ Done** — no bootstrap or reset Jobs remain in the `luminate`/`authentik` namespaces. | T6 |
| **T32** | Enforce Postgres **TLS**: set `POSTGRES_SSLMODE=require` (or `verify-full`); for a private CA, mount the CA bundle and point psycopg (`sslrootcert`) and Langfuse Node/Prisma (`NODE_EXTRA_CA_CERTS`) at it (DP-7). **✅ Done** — `POSTGRES_SSLMODE=require` on backend + DBOS worker. | T6 |
| **T33** | **Connection sizing + pooler mode** (DP-8): right-size the in-process psycopg3 pool (`DB_POOL_MIN_SIZE`/`DB_POOL_MAX_SIZE`, peak ≈ replicas × 40) vs the DB `max_connections`; **confirm no transaction-mode pooler (PgBouncer)** fronts Postgres — the app's **LISTEN/NOTIFY** (workflow_outbox, gateway fanout, worker listener) requires **session-mode** pooling or a direct connection. **✅ Done** — verified live: direct RDS connection, **no PgBouncer**, `max_connections=1702` vs ~71 in use. | T6 |
| **T40** | **Provider-credential secret backend** ([EACPP-1294](https://sunlife.atlassian.net/browse/EACPP-1294)) — distinct from T7, which covers the platform's *own* bootstrap Secrets. Luminate writes *provider* API keys into a secret manager and stores only a `secret_ref`; `CREDENTIAL_BACKENDS` is unset today, so the portal offers no backend and every offering must be keyless. Set `CREDENTIAL_BACKENDS=vault` with `VAULT_ADDR`, `VAULT_MOUNT`, `VAULT_K8S_ROLE` and `VAULT_K8S_AUTH_PATH`; bind the backend ServiceAccount to a Vault role holding **write** on the KV path (create, rotate and delete all write through); confirm `manage.py check` is clean — `credentials.E002`–`E004` validate the settings at deploy time rather than failing on first portal use. | T7 |

### PT-3 · Deploy pipeline

| Task | Description | Depends |
|------|-------------|---------|
| **T9** | Dry-run the single Helm release on dev (`dryRun=true`) — app + SLF Traefik/Vault templates — fix render issues. **✅ Done** (chart renders cleanly). | T7, T8, T19, T20 |
| **T10** | First real deploy of backend + frontend to dev EKS; verify health behind Traefik. **✅ Done** — `luminate` ns, backend (Django, migrations applied) + frontend (Nuxt) healthy behind Traefik; disposable in-cluster Postgres as interim (T6 replaces). Cleared cluster admission (Connaisseur ns bypass, Gatekeeper CPU-limits + `com.sunlife/*` ns annotations, `cce-managed` tolerations, ECR-only images). | T9 |
| **T11** | Set `.Values.slf.traefik` (real Gateway name + hostnames) in the HTTPRoute chart template; align `ALLOWED_HOSTS`/CORS. Upstream uses **AWS ALB (EKS Auto Mode, classic Ingress API)** — re-home the AWS-native ALB features (TLS, WAF, access logs) onto Traefik/platform equivalents. **✅ Core done** — host `luminate.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com`, DNS Alias live, `/api`+`/_allauth`→backend, `ALLOWED_HOSTS`/CSRF/CORS set. **Residual:** WAF + access-log re-homing. | T10 |
| **T37** | **Venafi TLS certificate — Keycloak hostname.** `keycloak.apps.slf-eks-t1k-ca-<env>.aws.sunlifecorp.com` currently serves the self-signed `slf-eks-wildcard-tls`, so clients reject it and `SERVICE_PRINCIPAL_AUTH_ENABLED` cannot be switched on. Steps: \\ 1. Log into Venafi → Certificate Inventory → **Create a New Certificate**. \\ 2. *Folder* tab — Certificate Folder `CA Server Auth`; Nickname = the Common Name; Application Name `Luminate`; Environment `DEV`; Description `Luminate portal - side-by-side ACP stack comparison`; custom fields, if present — cost centre `183472`, support group `DE T1K Agent Control Plane`. \\ 3. *Certificate Signing Request* tab — leave **Generate a CSR for me** selected. Common Name `keycloak.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com`. \\ 4. *Additional Information* tab — under Subject Alternative Names (DNS) add the Common Name, plus `gateway.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com` to cover T38 on the same certificate. Check Approvers reads `User_Venafi_Approvers_T1KACP`. Tick **Start Processing on Creation**, then **Create Certificate**. \\ 5. Wait for the approval email, then open the download link. \\ 6. Download as **PKCS#12**, leaving **Root Chain selected** — Traefik has to serve the intermediate. \\ 7. `openssl pkcs12 -in cert.p12 -nodes -out bundle.pem`, then split into `tls.crt` (full chain, leaf first) and `tls.key`. \\ 8. Create the secret in the `traefik` namespace and ask the platform team to add a `websecure-venafi` listener pointing at it. \\ Done when `curl https://keycloak.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com/realms/luminate` returns 200 without `-k`. The HTTPRoute and DNS from T11 that this needs are already live (verified 2026-08-24), so nothing here waits on T11's remaining WAF / access-log work. | — |
| **T38** | **Venafi TLS certificate — gateway hostname.** Same steps as T37, with Common Name `gateway.apps.slf-eks-t1k-ca-<env>.aws.sunlifecorp.com`. If this hostname was added as a SAN on the T37 certificate, no separate request is needed — install that certificate and close this task. Done when `curl https://gateway.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com/llm/v1/models` returns 401 without `-k`. | T37 |
| **T23** | Sign the mirrored Luminate images (cosign) so the Connaisseur `securesystemsengineering.connaisseur/webhook: ignore` namespace bypass can be removed. Cluster admission requirements (Gatekeeper CPU limits, `com.sunlife/*` ns annotations, `cce-managed` tolerations, ECR-only images) are now encoded in the chart/values via `slf.*`; image signing is the one remaining bypass. | T10, T20 |
| **T24** | Cut over from the manual `helm upgrade` bring-up to the Jenkins `luminate-deploy-cd` job as the deploy path of record (folder AWS creds T8; secrets no longer via `--set`). | T8, T10 |
| **T12** | **API Platform onboarding** — publish the portal + gateway OpenAPI specs to the SLF API Platform / developer portal for discovery + consumption. Portal API is a single drf-spectacular spec at `/api/schema/` covering the full `/api/v1/*` surface (catalog: applications, agents, mcp-servers, models, providers; IAM: users/roles/groups/service-principals; gateways, guardrails, access-policies, policy-engine, tagging, metrics, model-pricing, approvals, organizations). Gateway (data-plane) API is a separate onboarding. Depends on the edge auth (T26) + Light Proxy (T25). **Finding (2026-07-22):** the portal REST API is **session-cookie only** (`DEFAULT_AUTHENTICATION_CLASSES` = `SessionAuthenticationWithChallenge`) — registration is **UI-first**, so onboarding gives discovery + edge protection but **does not** enable programmatic (M2M) consumption of the registry APIs. Programmatic parity with the internal ACP build requires a net-new inbound **bearer-JWT → `ServicePrincipal`** auth capability, tracked in the consortium spec **`programmatic-registry-api`**. Gateway (data-plane) API already validates bearer JWTs. Portal onboarding is therefore **deferred / governance-driven** until that capability lands (or if API-Platform onboarding is mandated regardless for edge WAF/telemetry). | T11, T25, T26 |
| **T25** | **Add the Light Proxy (networknt) to `luminate-sunlife-deploy`** for the portal API (and gateway API when enabled), mirroring `acp-deploy`'s `k8s/overlays/.../proxy/{service}` (per-service `values.yml` + `openapi.yaml` + `logback.xml` + liveness probe) and `patches-proxy/*` — but as Helm chart templates gated by `.Values.slf.lightProxy`. Terminates edge OAuth/JWT (Okta) in front of the plaintext app port; feed the proxy's `openapi.yaml` from the portal's `/api/schema/`. Unlike ACP's 5 services this is **one** proxy in front of the portal backend + one for the gateway. Route Traefik `/api` (+`/_allauth`) through the proxy instead of straight to the app once enabled. **Note (2026-07-22):** the proxy only enforces edge Okta JWT — the portal app still authenticates by **session cookie**, so a bearer token passes the proxy but **401s at the app** until the inbound bearer-auth capability (**`programmatic-registry-api`**) lands. For the UI, keep the session path (edge proxy in front of a session-auth app is redundant unless mandated). | T10, T26 |
| **T26** | **Okta onboarding for the Luminate APIs** — request Okta OAuth authorization server(s) / resource apps for the portal API and the gateway API (audiences, scopes, JWKS `client.tokenKeyServerUrl: https://okta-oauth.sunlife.com` + `client.tokenKeyUri: /oauth2/{authServerId}/v1/keys`), mirroring ACP's per-service Okta auth-server model. Produces the JWT-validation config the Light Proxy (T25) consumes and the client credentials for programmatic API consumers. **Note (2026-07-22):** these client credentials only yield **usable** programmatic access to the portal registry APIs once the portal accepts inbound bearer tokens (**`programmatic-registry-api`** consortium spec); today the portal is UI-session-only, so Okta client-credentials tokens authenticate at the edge but not at the app. Directly usable now for the **gateway** (data-plane) API. | — |
| **T13** | Enable gateway + worker once Vault secrets + secrets-guard edit land; verify Langfuse traces flow. **✅ Done** — `luminate-gateway` 3/3 and two `luminate-dbos-worker` replicas running; backend points at `langfuse-web.luminate-observability`; traces + observations present in ClickHouse. | T7, T5 |
| **T21** | Set up UI/Portal SSO with **Azure AD/Entra**: submit the **Azure SSO Intake Request** (ServiceNow) to register the Luminate portal as an Entra app (clientId, tenant, redirect URIs, AD-group role claims); wire MSAL into the frontend runtime config (mirrors `agent-control-plane-ui`). **✅ Done** — Entra OIDC live on dev (`SSO_OIDC_PROVIDER_ID=portal-luminate`, `SSO_OIDC_SERVER_URL=https://login.microsoftonline.com/415bb08f…/v2.0`, client ID configured). | T10 |
| **T22** | Internal **M2M identity** decision. Code is **well-abstracted** (`OAuthProvider` interface + registry; gateway JWT validation already IdP-agnostic), so adding an Okta/Entra provider is contained (~3–6 wks/IdP). **Real blocker = governance**: Luminate dynamically creates/deletes an OAuth client per entity via the IdP admin API (Okta Apps API / Entra Graph `Application.ReadWrite.All`). **Options:** (A) build providers; (B) redesign to shared-client + scoped-tokens; (C) approve Authentik near-term; (D) **workload identity federation** — secretless K8s SA tokens with OpenShift/EKS as OIDC provider (SPIFFE/SPIRE, à la enterprise AgentGateway + Vault). **Architect (Greg O):** Okta M2M ill-suited to agentic (per-token licensing, no fine-grained tokens, no OBO merge); Entra=user tokens only (some OBO); Ping Federate=client-facing CA only. **Spike:** can agents authorise to Authentik via K8s SA / SPIFFE? See D2 §M2M analysis + §Architect input. **✅ Resolved — option (C)**: Authentik is deployed in the `authentik` namespace and the portal validates service-principal JWTs against its OIDC issuer/JWKS (`SERVICE_PRINCIPAL_AUTH_*`). | T13 |

> **Deferred (out of scope for this deployment):** adapter / Bedrock integration
> — `aws-adapter` adaptation, `aws-harness-sdk`, and Snowflake/K8s adapter
> continuity — is tracked as a separate later effort, not part of standing up
> Luminate on Sun Life EKS.

### PT-5 · Environment promotion

Dev is the reference deployment (T1–T33). Each remaining environment is promoted via a
single ticket carrying one subtask per prerequisite, mirroring the §0 status table of its
runbook in `luminate-sunlife-deploy/deploy-checklists/`. Each task below links its own runbook;
that file, not this row, is the working checklist.

| Task | Description | Depends |
|------|-------------|---------|
| **T34** | **Promote Luminate to TEST/UAT** ([EACPP-936](https://sunlife.atlassian.net/browse/EACPP-936)) — `692797214700`, **`slf-eks-t1k-ca-uat`**. ✅ **DEPLOYED 2026-08-19.** Portal, Authentik, Langfuse/ClickHouse tier and the AI gateway with cross-account Bedrock are live; 13 images mirrored; Valkey + S3/IRSA applied. Open: DNS, Jenkins credential, Vault, Entra SSO. **TLS:** this cluster has **no `websecure-venafi` listener at all** (verified 2026-08-24) — the portal, gateway and Keycloak hostnames each need a Venafi certificate (T37, T38) or they serve the self-signed `slf-eks-wildcard-tls`. **Runbook:** [deploy-checklists/test-uat.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/test-uat.md) — the working checklist, with the §0 prerequisite table this task's subtasks mirror. | T13 |
| **T35** | **Promote Luminate to STAGE** ([EACPP-953](https://sunlife.atlassian.net/browse/EACPP-953)) — `775755739292`, `slf-eks-t1k-ca-stage`. ✅ **DEPLOYED 2026-08-19.** Same footprint plus HA Valkey (`cache.t4g.medium` ×2, multi-AZ). Verified: CHI+CHK Completed, 0 objects in Postgres `public`, Langfuse `/api/public/projects` 200 from the backend pod, backup drill 47 objects, Bedrock Converse 200. Open: same four platform requests. **TLS:** as with TEST/UAT, **no `websecure-venafi` listener exists** (verified 2026-08-24) — portal, gateway and Keycloak hostnames each need a Venafi certificate (T37, T38). **Runbook:** [deploy-checklists/stage.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/stage.md) — the working checklist, with the §0 prerequisite table this task's subtasks mirror. | T34 |
| **T36** | **Promote Luminate to PROD** ([EACPP-970](https://sunlife.atlassian.net/browse/EACPP-970)) — `035722575935`, `slf-eks-t1k-ca-prod` (ACTIVE, k8s 1.34). Platform is ready (Traefik NLB, wildcard TLS, `selfsigned-ca`, VSO, OIDC provider) — but note the wildcard is the **self-signed** `slf-eks-wildcard-tls` (`CN=SLF EKS Self-Signed CA`, verified 2026-08-24) and only `acp.apps.…prod…` has a real `websecure-venafi` listener, so the portal, gateway and Keycloak hostnames still need Venafi certificates (T37, T38); "wildcard TLS present" does **not** mean TLS is solved. **No luminate footprint.** `slf_elasticache_admin_prod` **now exists** (GEN-2490 delivered), both TFC workspaces exist, and `acp-eks-deploy-aws-prod` already exists in Jenkins. Long pole is the RDS provisioning — **SNOW CHG0547049**, DMS request **DMS-178186** (`https://jira.ca.sunlife/browse/DMS-178186`): four dedicated instances (`luminate`, `keycloak`, `authentik`, `langfuse`), promoted from the dev equivalents at 100 GB / Multi-AZ / 14-day backups, with `<name>_owner` membership instead of owner passwords. **Runbook:** [deploy-checklists/prod.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse/deploy-checklists/prod.md) — the working checklist; §1–§3 carry the RDS detail and §0 the prerequisite table this task's subtasks mirror. | T35, T7, T23 |
| **T39** | **Vanity URL for the PROD portal** ([EACPP-1162](https://sunlife.atlassian.net/browse/EACPP-1162)) — serve the portal on `luminate.sunlifecorp.com` instead of `luminate.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com`, which puts the cluster name in a user-facing address. Four parts: a **DNS CNAME** in the corporate zone (ServiceNow RITM), a **Venafi SAN**, an **Entra redirect-URI add**, and a config change in `values/values-prod.yaml` (`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`, `BACKEND_URL`, `slf.traefik.hostname`) plus `helm/langfuse/values-prod.yaml`. **TLS is done** — the 2026-08-31 Venafi reissue (T38, EACPP-1155) carries `luminate.sunlifecorp.com` as its 8th SAN, so no new Gateway, listener or redeploy is needed. **Entra is done** — the vanity callback was *added* alongside the existing one (not replaced), which is what lets both hostnames work during cutover; `django-allauth` derives `redirect_uri` from the request host, so had it been edited rather than added, the current hostname would have started failing `redirect_uri mismatch`. **DNS is the sole remaining blocker** — see below. Internal-only: the NLB is RFC1918, so this does not deliver internet access. | T36, T38 |

**T36 open decision — prod RDS.** The account has only the two internal-build instances
(`slf-ca-mo-dms-pp-t1k-acp:7230`, `…-t1k-acp-langfuse:5360`), already PG 17.10 `db.r6g.large`
Multi-AZ. Adding the luminate/authentik/langfuse databases to them is a **grants-only CHG
(days)**; new dedicated instances are a **full provisioning CHG (weeks)** — prod has no
QuickDB self-service. An earlier revision asserted "do not reuse" without recording who
mandated it; confirm before spending the CHG.

**T39 — the DNS request is structurally blocked, and a resubmit will fail identically.**
RITM2606155 was closed unfulfilled: *"Host(A) Record 'luminate.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com'
with record type A doesn't exist in BlueCat."* The form was **not** filled in wrongly. `sunlifecorp.com`
is served by **BlueCat**; `aws.sunlifecorp.com` is a **Route 53 private hosted zone**. BlueCat cannot
see the CNAME target, so its pre-flight validation rejects the request — and there is no in-zone
target to point at instead, because the Traefik NLB is outside its zones too.

It is still achievable: `jenkins-dna.sunlifecorp.com` is exactly this shape and is live today, with
BlueCat answering authoritatively for a CNAME to an ELB it does not own. So BlueCat does store
out-of-zone CNAMEs; only the ServiceNow request validation objects. **Ask the DNS team which
mechanism created the `jenkins-dna` record** — External Host Record, or a manual validation
override — and request the same one. Do not blindly resubmit.

With TLS and Entra both landed, **this record is the last thing standing between the cutover and
being a config change.** Once it resolves, the vanity host serves on the existing Traefik listener
and only `values-prod.yaml` and `helm/langfuse/values-prod.yaml` remain.

**Two corrections that apply to every environment**, learned during the stage bring-up:

- **The RDS security-group opening is not needed anywhere.** The DMS SGs carry the SLF managed
  prefix list `pl-0189ac0d039207ed9`, which contains `10.0.0.0/8`; cluster pods are `10.128.x.x`.
  Verified from a pod on stage and confirmed on the prod SG. Do not raise SG tickets.
- **Image signing is not a prod entry requirement.** All four `acp-*` namespaces on the prod
  cluster run with the Connaisseur bypass label, so T23 does not gate T36 the way the critical
  path assumed.

Each promotion ticket carries 16 subtasks mirroring its runbook's §0 prerequisite table.
As of 2026-08-20: **TEST/UAT 11/16 done**, **STAGE 11/16 done**, **PROD 1/16 done**. The five
still open on test/UAT and stage are the same platform requests in both (DNS, Jenkins
credential, Vault, Entra SSO, and the Jenkins-driven deploy that depends on the credential).

---

## Critical Path

1. ✅ **T6 + T18 + T27 (per-instance Postgres) → T28–T33 → T13** — complete: the full
   stack (backend, frontend, gateway, DBOS worker) runs on the dedicated dev RDS with a
   named schema, TLS, and Langfuse traces flowing.
2. ✅ **T19 (namespaces/capacity — CCE-1047) + T8 (deploy creds) → T9 → T10** — dev deployed.
3. ✅ **T20 (image mirror) → T9/T10** — images served from SLF ECR.
4. **T7 (Vault/VSO + IRSA) → T36 (prod)** — prod should not run on plain in-namespace Secrets.
   (T23 image signing was previously shown as gating T36; it does not — the prod cluster's
   `acp-*` namespaces already run with the Connaisseur bypass label.)
5. **T26 (Okta onboarding) → T25 (Light Proxy) → T12 (API Platform)** gate programmatic
   API access; T12 additionally depends on the consortium `programmatic-registry-api` spec.
6. ✅ **T34 → T35** — test/UAT and stage both deployed 2026-08-19. **T36** is next; it is gated
   on the prod RDS decision (reuse vs new), not on the cluster.

## Definition of Done

- ✅ Luminate (backend, frontend, gateway, DBOS worker) runs on dev EKS behind Traefik.
- ✅ Langfuse observability is live (Altinity ClickHouse + Keeper, S3 blob + backup, Valkey,
  dedicated Postgres) with traces landing in ClickHouse.
- ✅ UI/Portal SSO via Azure/Entra and internal M2M via Authentik are working.
- ⬜ Secrets sourced from Vault via VSO (no plain in-namespace Secrets) and images cosign-signed.
- ⬜ Edge API via Okta + Light Proxy, and API Platform onboarding.
- ⬜ Promoted to TEST/UAT, STAGE and PROD.
