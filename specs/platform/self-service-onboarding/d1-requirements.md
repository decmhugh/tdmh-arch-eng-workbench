# Self-Service Onboarding — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: [EACPP-1325](https://sunlife.atlassian.net/browse/EACPP-1325)

## User Stories

### US-1: A tech lead asks for a project and gets one

**As a** business-area tech lead who has been through ACP intake,
**I want** to submit one request for my team's tenancy,
**so that** my engineers can register resources without anyone chasing a named individual.

**Acceptance Criteria**:
- [ ] One form, one submission, one reference I can quote.
- [ ] I am told what was created, what was renamed and what was declined, in the reply.
- [ ] The reply names my portal and my gateway for each environment I was granted.
- [ ] If the request is malformed, I am told which field, before anything is created.

### US-2: A platform administrator approves rather than types

**As an** ACP Product Team engineer,
**I want** to review a rendered plan and approve it,
**so that** I am making the decision and not also performing the twelve database writes.

**Acceptance Criteria**:
- [ ] The plan shows exactly what will be created, changed and left alone.
- [ ] Approving runs it; declining closes the request with a reason the requester can read.
- [ ] I can run the plan without applying it, as many times as I like.
- [ ] Nothing in the request can cause the pipeline to execute code I did not intend.

### US-3: A workload receives a credential it never had to be told

**As a** developer deploying an agent,
**I want** the credential to appear in my team's secret store,
**so that** the secret is never pasted into a chat, a ticket or an email.

**Acceptance Criteria**:
- [ ] The reply contains a secret reference and no secret.
- [ ] The reference resolves in my secret store, from my workload, without further help.
- [ ] Rotation updates the same reference; I am told when, in advance.
- [ ] If the secret store is unavailable, the credential is **not** issued.

### US-4: An owner promotes to STAGE with the approval intact

**As a** project Owner,
**I want** to request promotion with my evidence attached,
**so that** the separation of duties that gates STAGE and PROD is recorded, not improvised.

**Acceptance Criteria**:
- [ ] My approval and the platform administrator's action are separate, recorded events.
- [ ] The pipeline refuses to promote an agent whose models are not already in the target environment.
- [ ] A change record is required for PROD and shape-checked.

### US-5: An operator sees drift before a requester reports it

**As an** ACP Product Team engineer,
**I want** a scheduled report of gateways not joined to environments, deployments with no
route, and credentials approaching rotation,
**so that** the failures that are silent by construction become visible.

**Acceptance Criteria**:
- [ ] Runs on a schedule, not on demand.
- [ ] Each finding names the resource, the install and the fix.
- [ ] A clean run is reported as clean, not as silence.

## Functional Requirements

### FR-1: One request contract

Every front door produces the same JSON request object, and the executor consumes only that.
The contract carries `kind`, `install`, `requester`, `approver`, a `payload` whose shape is
determined by `kind`, and an optional `reference` (Jira key or ServiceNow RITM).

The contract is **schema-validated at the boundary**. A request that fails validation is
rejected by the front door with the offending field named, and never reaches the executor.

*Rationale: three front doors with three behaviours is three systems to operate. The contract
is the only thing that must be stable.*

### FR-2: Eight pipeline kinds

The executor implements exactly these `kind` values. Each is a Jenkins job.

| `kind` | Pipeline | Replaces |
|---|---|---|
| `tenancy` | **P1** — folder, project, users, role bindings | `onboard-team-to-luminate` |
| `access-grant` | **P2** — add or remove a role binding | `docs/administration/granting-access.md` |
| `access-policy` | **P3** — agent → model / MCP server grant | the "tell the platform team which models your agent needs" step |
| `deployment` | **P4** — deploy a registered resource to a gateway | `deploy-mcp-server-to-gateway`, `docs/administration/deploying.md` |
| `credential` | **P5** — issue / rotate / revoke, delivered to a secret store | `docs/administration/credentials.md` |
| `machine-identity` | **P6** — service principal or agent machine identity | `luminate-machine-identity`, `provision-agent-for-delegated-mcp` |
| `promotion` | **P7** — promote a resource to the next environment | `docs/building/promoting-your-agent.md` |
| `inventory` | **P8** — scheduled drift and expiry report | today: nothing |

### FR-3: Dry run is the default

Every pipeline accepts an `apply` parameter defaulting to **false**. A dry run renders the
plan — what exists, what would be created, what would change — and writes nothing. Applying is
an explicit act.

*This inverts nothing: it matches both the devkit scripts (`APPLY=1`) and `Jenkinsfile_deploy`
(`dryRun`). Consistency here is worth more than elegance.*

### FR-4: Verification is a stage, and it drives the real surface

Every pipeline ends with a verification stage that fails the build when it cannot prove the
change. Row counts are not proof. The pass condition per kind:

| Kind | Proof |
|---|---|
| `tenancy` | Drive `ProjectViewSet.as_view({"get": "list"})` as each granted user and as a **negative control** with no binding on the project |
| `access-grant` | Same, for the specific permission granted |
| `access-policy` | The policy is `active` **and** a call through the gateway is authorised, or — where no traffic can be generated — the policy appears in the pushed bundle |
| `deployment` | The endpoint name appears in the gateway's own `config_dump`; for a `delegated_exchange` MCP endpoint, the RFC 9728 `.well-known/oauth-protected-resource/mcp/<name>` returns 200 |
| `credential` | The `secret_ref` resolves from the store, and a token minted with the credential is accepted by the gateway |
| `machine-identity` | A minted token carries the expected `aud` and `sub`; reads succeed on the opted-in surfaces and writes are refused |
| `promotion` | The target environment's gateway serves the resource, and the resource's models are present in that environment |
| `inventory` | N/A — it *is* verification |

> **A 401 from a gateway proves the host and the prefix, not the route.** Authentication runs
> before routing, so a nonexistent endpoint under a live prefix answers 401 as well. Never
> accept a status code as proof of existence.

### FR-5: Injection-safe execution

While the executor runs `kubectl exec ... manage.py shell`, every pipeline **must**:

1. Use a **quoted** heredoc (`<<'PY'`) so the shell performs no substitution into the script.
2. Pass every value through `kubectl exec -- env KEY=value ...` and read it in Python with
   `os.environ`.
3. Validate every identifier against a shape regex (DNS label for names, UUID for ids,
   RFC 5322 for emails) **before** it is passed.
4. Fail closed on anything unrecognised.

*This is not defensive style. `provision-gateway.sh` interpolated `${GW_KEY}` into Python run
by `manage.py shell -c` in the production backend pod — inert under a human, RCE under a build
parameter.*

### FR-6: Credential delivery by reference only

The `credential` pipeline mints the credential, writes it to the requester's secret store, and
returns a reference. The plaintext exists only inside the pipeline process and is never
written to a log, a build artefact, a Jira comment or a message.

If no secret backend is configured for the install, the pipeline **fails**. It does not fall
back to returning the value.

### FR-7: Approval follows the existing model

Approval is inherited from the deploy pipeline's shape rather than invented:

- Non-production installs and reversible acts: no approval.
- Production installs, and any act that grants access or issues a credential: `input` gated on
  a named AD group.
- Production: a ServiceNow change record, shape-checked `(?i)(CHG|INC)\d{7,}` so a Jira key
  cannot satisfy the gate.
- `promotion` to STAGE or PROD additionally requires the project Owner's approval to be
  recorded **separately** from the platform administrator's action.

### FR-8: Idempotency

Re-running a request with the same payload converges rather than duplicating. Each pipeline
reports `EXISTS` / `CREATE` / `CHANGE` per object, and a second identical run reports only
`EXISTS`. A partially failed run can be re-run safely.

### FR-9: The reply closes the loop

On completion the pipeline writes back to the originating front door — a Jira comment, a
ServiceNow work note, a chat reply — carrying: what was created, what was skipped and why,
the verification result, the addresses the requester needs, and the secret reference where
applicable. A failed run replies with a reason, not a build URL alone.

### FR-10: Addresses come from a registry, never from a pattern

Portal and gateway hostnames are read from a checked-in registry
(`deployments.json` in the devkit today) and re-probed before they are published. They are
**not** derived from the install name or by transforming the portal host.

*Measured: the dev install pairs `luminate.apps.…` with `gateway.apps.…`, which invites the
rule "swap the prefix"; the production install serves four environments as `gw-dev`, `gw-sit`,
`gw-stage` — and then PROD itself as plain `gateway`. `gw-prod` does not exist. There is no
wildcard DNS, so a guessed host is NXDOMAIN, not an informative 404.*

### FR-11: Every run is attributable

The audit record must name the human requester and the human approver, not the pipeline's
service account. Where the executor acts as a platform administrator, the `actor_email` in the
payload carries the accountable human and appears in `audit_events`.

### FR-12: The executor is one swappable stage

The `kubectl exec` mechanism is confined to a single shared step. When machine authentication
reaches the administrative surfaces (G-1), replacing it must not touch the request contract,
the approval model, the verification stages or the front doors.

## Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Unattended run time, approved request to verified result | < 30 minutes |
| NFR-2 | Availability of the front door does not depend on the pipeline | A queued request survives a Jenkins outage |
| NFR-3 | Emergency stop (CAP-11) is reachable without any pipeline | Always — a kill switch that needs a green build is not a kill switch |
| NFR-4 | No plaintext secret in any log, artefact, build parameter or process argument | Zero, asserted by a secret-scanning stage |
| NFR-5 | Pipeline definitions live in version control and are reviewed | 100%, no job configured only in the Jenkins UI |
| NFR-6 | A pipeline holds no authority beyond the administrator it replaces | Asserted at design review |
| NFR-7 | Requests and outcomes are retained for the audit period | Per Sun Life records retention for change evidence |
| NFR-8 | The contract is versioned; a front door on an old version is told so | Explicit `version` field, rejected with a message |

## Data Model Requirements

No change to the Luminate data model. This spec adds two artefacts of its own:

| Artefact | Home | Shape |
|---|---|---|
| **Request contract schema** | `acp-product-devkit` | JSON Schema; the single normative definition of every `kind`'s payload |
| **Install registry** | `acp-product-devkit` (`deployments.json`) | Per install: kube context, namespace, portal host, gateway hosts per environment, secret backend and path prefix, Jenkins credential id, approval group |

The `tenancy` payload is the **published intake form made machine-readable** —
`luminate-user-guides` `docs/getting-started/onboarding-intake.md` already asks for the business
area, contacts, project and owner, parent folder, cost owner, people and their access, and the
resources to register. The schema takes its fields from that form rather than defining a second
vocabulary for the same request. The existing devkit request files (`request.example.json`,
`principal.example.json`) supply the remaining payload shapes and are folded in rather than
re-invented.

## Edge Cases

| Case | Expected behaviour |
|---|---|
| Requester names a folder or environment that does not exist | Rejected at validation with the live list of names, before anything is created |
| Requester is granted Owner **and** a per-type Administrator | Flagged as duplicate coverage; Owner alone is granted, and the reply says so |
| A named member has never signed in | User row and verified primary `EmailAddress` created just-in-time, lowercase, with an unusable password |
| Owner requested on an existing project | Refused — `RoleBindingService.create` rejects the Owner role; Owner comes only from `ProjectService.create(owner=)` or `transfer_ownership`, and transfer is a separate audited act |
| MCP server uses `stdio` transport | Deployment refused with the reason; stdio cannot be served by a remote gateway |
| `delegated_exchange` target whose audience cannot be exchanged | Deployment applies but the route is **withheld**, not downgraded. Verification catches it and the reply says the route does not exist |
| Gateway is healthy but not joined to the target environment | Detected in pre-flight; the symptom otherwise is an empty dropdown with no error anywhere |
| Secret store unreachable at credential time | Whole run fails; no credential is minted, so nothing is orphaned |
| Credential minted but the write fails | Credential is revoked before the build exits; a minted-but-undelivered credential is worse than none |
| Two requests for the same project arrive together | Second run converges on the first's result (FR-8); no duplicate folder or project |
| Requester asks for something that is not one of the eight kinds | Routed to a human with the request intact; the pipeline does not guess |
| Request payload contains shell metacharacters | Rejected by the shape regex before execution (FR-5) |

## Constraints

| ID | Constraint | Source |
|---|---|---|
| C-1 | No machine credential is accepted on the administrative REST surfaces | `DEFAULT_AUTHENTICATION_CLASSES`; `RegistryBearerAuthMixin` on three catalog viewsets only |
| C-2 | `SERVICE_PRINCIPAL_AUTH_ENABLED` is `true` in dev only | `values/values-{dev,test,stage,prod}.yaml` |
| C-3 | `CREDENTIAL_BACKENDS` is unset in every Sun Life values file | `luminate-sunlife-deploy` `origin/main` |
| C-4 | Owner cannot be granted through the role-binding service | `OwnerRoleNotCreatableError` |
| C-5 | `RoleBinding` must never be written through the ORM | `scope_tokens` is computed by `ResourceHierarchyService.compute_binding_tokens()` inside the service; a hand-made row is invisible to every list filter while looking correct in the admin |
| C-6 | Credential rotation has no overlap window | The old secret stops the instant the new one is issued |
| C-7 | `luminate-exchange-aud` must be attached as a **default** client scope through the Keycloak admin API | The backend cannot do it; without it the call fails 502 `access_denied: Client is not within the token audience` |
| C-8 | Gateway hostnames are not derivable | No wildcard DNS; `gw-prod` does not exist |
| C-9 | A registered resource cannot be moved between projects, and a deployed one cannot be deleted | Project choice is permanent; the tenancy pipeline must validate the name, not just accept it |
| C-10 | Jenkins is the sanctioned executor | INT-08; approval, credential binding and audit are inherited rather than rebuilt |

## Capability Gaps

> Each row is classified and escalated per
> [Capability Gap Escalation](../../../process/capability-gap-escalation.md).

| Gap | Capability | What is missing | Classification | Impact | Escalation |
|---|---|---|---|---|---|
| **G-1** | [CAP-06](../../../capability-map.md#cap-06) | No machine authentication on the administrative surfaces. `RegistryBearerAuthMixin` is on `agents`, `mcp_servers` and `models` only; `DEFAULT_AUTHENTICATION_CLASSES` is session + user-delegated OAuth. A pipeline can read the catalogue and change nothing | **Component change** | Workaround available — forces the `kubectl exec` executor, which carries R-1 and R-5 | **Consortium ask.** The narrow form: accept a service principal on `organization`, `iam`, `deployment`, `credentials` and `resource-access`, scoped by the principal's own role bindings |
| **G-2** | [CAP-28](../../../capability-map.md#cap-28) · [INT-02](../../../capability-map.md#int-02) | `CREDENTIAL_BACKENDS` unset in all four Sun Life values files, so no secret backend is offered | **Integration** (deployment configuration) | **Blocks launch** of P5 — credential delivery is the whole point | Sun Life. Belongs with `sunlife-deployment` (EACPP-596); needs a Vault address, KV mount and Kubernetes auth role for the `luminate` namespace |
| **G-3** | [CAP-06](../../../capability-map.md#cap-06) | `SERVICE_PRINCIPAL_AUTH_ENABLED` is `false` in test, stage and prod | **Integration** (deployment configuration) | Degrades — even the read half of G-1 is unavailable outside dev | Sun Life. Gate on a decision about the trusted issuer; the setting names a single issuer per install |
| **G-4** | [CAP-28](../../../capability-map.md#cap-28) | Credential minting and the secret writer are unconnected — no code path pushes a newly minted `client_secret` into a store | **Component change** (small) | Workaround available — P5 bridges the two calls itself | Consortium, low priority. Sun Life can bridge it in the pipeline meanwhile |
| **G-5** | [CAP-28](../../../capability-map.md#cap-28) | Rotation has no overlap window; the old secret dies on issue | **Component change** | Degrades — every rotation is a coordinated cutover | Consortium ask: dual-active secrets with a grace period. Until then P5 schedules and announces |
| **G-6** | [CAP-06](../../../capability-map.md#cap-06) | `luminate-exchange-aud` cannot be attached as a default client scope from the backend; it needs the Keycloak admin API out of band | **Component change** | Degrades — P6 needs a second credential and a second call | Consortium. Named as a platform defect in `provision-agent-for-delegated-mcp` |
| **G-7** | [CAP-04](../../../capability-map.md#cap-04) | A gateway not joined to an environment yields an empty dropdown — no error, nothing in the logs | **Component change** (diagnosability) | Workaround available — P8 asserts the join | Consortium, low priority. Sun Life covers it with the inventory pipeline |
| **G-8** | [INT-06](../../../capability-map.md#5-the-sun-life-integration-surface) | No ServiceNow API integration for the ACP Product Team; RITMs are raised through the portal by hand | **Integration** | Degrades — the ServiceNow front door needs an integration account before it can ship | Sun Life. Request an integration account and a catalog item |
| **G-9** | [CAP-04](../../../capability-map.md#cap-04) | Deployment push reports an empty skip list while emitting nothing, so a miss is silent | **Component change** (diagnosability) | Workaround available — P4 verifies against the gateway's own config dump | Consortium, low priority |

**Interim measures** — and the condition under which each is removed:

| Gap | Interim measure | Removed when |
|---|---|---|
| G-1 | Executor runs `kubectl exec ... manage.py shell` under FR-5's injection-safe pattern, confined to one swappable stage (FR-12) | A service principal is accepted on the administrative surfaces |
| G-2 | **None.** P5 does not ship until a backend is configured — a fallback that hands out plaintext would become permanent (R-3) | `CREDENTIAL_BACKENDS` is set and a write succeeds end to end |
| G-3 | Catalogue reads go through the same `kubectl exec` path as the writes | The flag is on and an issuer is agreed per install |
| G-4 | P5 calls `generate-credentials` and then the secret writer, in one pipeline, with revoke-on-failure | The platform offers a single operation |
| G-5 | P5 announces the cutover time and rotates on a schedule the workload owner has agreed | Dual-active secrets exist |
| G-6 | P6 attaches the scope through the Keycloak admin API, with its own credential | The backend can do it |
| G-7, G-9 | P8 asserts gateway↔environment joins; P4 verifies against the gateway config dump | The platform reports the failure itself |
| G-8 | Jira front door ships first and carries the request record | An integration account exists |

## Traceability

| Requirement | Capability | D0 Success Criteria | Pipeline |
|---|---|---|---|
| FR-1 | — | SC-3 | all |
| FR-2 | CAP-04, CAP-07, CAP-28 | SC-1 | P1–P8 |
| FR-3 | — | SC-1 | all |
| FR-4 | CAP-04, CAP-21 | SC-4, SC-5 | all |
| FR-5 | — | SC-7 | all |
| FR-6 | CAP-28, INT-02 | SC-2 | P5 |
| FR-7 | CAP-14, CAP-05 | SC-1 | P1, P2, P5, P7 |
| FR-8 | — | SC-6 | all |
| FR-9 | — | SC-3 | all |
| FR-10 | — | SC-5 | P1, P4, P7 |
| FR-11 | CAP-18, CAP-05 | SC-1 | all |
| FR-12 | CAP-06 | SC-1 | all |
| US-1 | CAP-07 | SC-3, SC-6 | P1 |
| US-2 | CAP-14 | SC-1 | all |
| US-3 | CAP-28 | SC-2 | P5 |
| US-4 | CAP-14, CAP-04 | SC-1 | P7 |
| US-5 | CAP-04 | SC-5 | P8 |
