# RA&S Dealer Transfer-in Xpress — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: EACPP-1446

## Problem Statement

Dealer Operations processes external transfer-in requests for clients moving wealth assets
from another institution to Sun Life. The discovery session cited approximately one million
external transfer requests per year. Advisors submit transfer forms, sometimes handwritten
and sometimes as editable PDFs; Dealer Operations staff then manually compare the form with
client and account information in systems including Univeris, review relinquishing-institution
details and statements, and check signatures. The session estimated that the manual process
takes 10–15 minutes per request and is difficult to scale and vulnerable to human error.

The team has already built and deployed a production application to assist this work. Dealer
Operations staff sign in to its React UI on OpenShift with SSO and upload the form, which a
Node.js API stores in S3. Starting a validation invokes an orchestrator Lambda through a Light4j
service. The Lambda, written in Python 3.12, makes two Bedrock calls: extraction, which sends a
single PDF holding the transfer form and the account statement and returns the fields as JSON;
and validation, which sends the extracted data with client and contract details from the
Univeris APIs, statement information and a transfer contact list, and returns an in-good-order
(IGO) or not-in-good-order (NIGO) result, an ATON or non-ATON determination, and a report of 12
to 14 validation steps. Results are stored in an RDS PostgreSQL database. The team described the
flow as sequential AI inference, not an agent workflow; it does not use an agent, reasoning loop,
or MCP server, and it does not update the submitted form. When an owner name or rep code does
not match Univeris, the user can confirm that the two are the same; the mapping is stored and
the validation reruns. For a NIGO result the application also drafts an email listing what is
wrong, which Dealer Operations copies and sends to the advisor.

The orchestrator Lambda is the only component that calls Bedrock, and it does so directly in
the team's own AWS workload account; the team confirmed this, and acknowledged the ACP team's
description of it as a boto3 runtime call. That path is outside ACP's governed gateway, so its
inference is not brought under the ACP onboarding, access, usage, and observability controls.
Asked whether the move needs any code change, the team was told it does: the Lambda imports the
Harness SDK in place of the direct Bedrock call, and ACP supplies the credentials and
instructions. The SDK supports the Lambda's Python version, but it sends only chat-completions
requests, and the gateway drops PDF content on that route, so the extraction call cannot move by
swapping in the SDK alone; see Risks.

## Opportunity

Route this existing application's model inference through ACP without replacing its business
workflow. This can bring the inference call onto the governed path and make ACP request traces
and token usage available, while keeping Dealer Operations' existing IGO/NIGO validation and
human follow-up process intact. The session reported that the current application takes about
2–3 minutes per transfer. It had been in production for about a month: the whole Dealer
Operations team uses it for all form types, but adoption, throughput, and performance figures
still need to be verified against production data.

## Stakeholders

| Stakeholder | Role | Key Concern |
|---|---|---|
| Dealer Operations | Business users; the session cited 250-plus people working in dealer operations | Accurate, useful IGO/NIGO reports and continuity of transfer processing |
| RA&S use-case team | Application owner; session participants Vineet A Gupta, Satya Kant (presented the solution), Hardik Pillai and Chandresh Soni | Minimal, clear Lambda integration change and reliable application behaviour; Vineet A Gupta also asked whether data could cross between consortium members (answered: each member runs its own install) |
| ACP Product Team | Onboarding and product owner; Lalit Summan led the session, Pavithra Viswanathan is the ACP product owner, and Kalev Gonvick leads this onboarding (EACPP-1446 assignee) | Capability fit, governance baseline, and onboarding readiness |
| ACP platform team | Harness SDK, gateway, identity, and deployment provider; Ranjula Rowel (principal software engineer) attended | Provide onboarding instructions, credentials, and supported gateway integration |
| Security, Privacy, and application support | Stakeholders to confirm | Data handling, risk classification, logging, availability, and operational support |
| Model Risk and Enterprise Risk | Stakeholders to confirm | Risk band, whether the model is in scope of E-23, and whether IGO/NIGO and ATON results are customer-affecting decisions |

## Scope

### In Scope

- Onboard the existing Dealer Transfer-in Xpress production application to ACP for its Bedrock inference path.
- Assess and implement the change the orchestrator Lambda (Python 3.12) needs to call the ACP gateway: the Harness SDK for chat-completions calls, and the gateway's Responses route, or another agreed way, for the PDF extraction call.
- Determine the ACP application or agent identity, credential, and access-policy setup required for this caller.
- Confirm the inference pattern from [Integration Patterns](../../platform/integration-patterns/d2-design.md) — I1 consumer-account, the default for a team that already calls Bedrock in its own AWS account as this one does, or I2 centralized — and which ACP environment gateway each application environment uses.
- Preserve the existing PDF extraction, Univeris API validation, business rules, IGO/NIGO and ATON/non-ATON results, and generated report unless the use-case team agrees otherwise.
- Establish what ACP gateway traces, token usage, and cost information are available for this workload.
- Define the sandbox onboarding and the evidence required before any ACP production routing change.
- Confirm data classification, retention, logging, risk rating, availability expectations, and the manual operating fallback.

### Out of Scope

- Replacing or redesigning the transfer-processing application or its business rules.
- Introducing an autonomous agent, agent workflow, MCP server, or agent-to-agent interaction; the team said these are not part of the current implementation.
- Automatically changing submitted forms, client records, or transfer decisions. The demonstrated application reports validation findings; it does not update the form.
- Automating the human communication and follow-up process for NIGO results.
- Expanding the application to transfer-out requests; the team said the current tool supports transfer-in only.
- Treating ACP as the system of record for transfer forms or customer account data.

## Capability Requirements

> **Proposed, not confirmed.** The session discussed moving the Lambda's Bedrock call onto the
> ACP gateway with the Harness SDK, but no capability was confirmed against a named ID and none
> was declined. The tables below are ACP's reading of the session mapped to the
> [ACP Capability Map](../../../capability-map.md); they are the agenda for the design review
> Lalit Summan proposed at the end of the session, not the RA&S team's selection.

### Mandatory baseline — acknowledgement pending

All sixteen [mandatory capabilities](../../../capability-map.md#3-the-governance-baseline--mandatory-for-every-onboarding)
apply to this application whether or not the session raised them.

| Confirmed with | Date | Notes |
|---|---|---|
| *Pending — RA&S application owner (Vineet A Gupta, Satya Kant and Hardik Pillai attended; confirm who signs)* | *TBC* | Present the full baseline. **CAP-08 is mandatory, not a selection**: once onboarded, no direct Bedrock path may remain, including as a fallback. CAP-12 quotas are ⚠️ modelled, not enforced; CAP-14 lifecycle and CAP-18 audit are 🟡 partial. CAP-01 is written for agents and this application is not one; Luminate has a first-class `Application` resource that can be deployed to a gateway and own its credential, so confirm with the capability-map owner that application plus CAP-04 deployment registration meets the inventory obligation. CAP-10 needs a deliberate configuration for client documents, not the default — see Risks. |

### Selected capabilities — proposed for discussion

Mandatory capabilities apply even where they are not listed. The rows below are the ones with a
question specific to this application, plus the conditional capabilities whose trigger has to be
decided.

| Capability | Why this application may need it | Proposed priority | Status today | Confirmed by |
|---|---|---|---|---|
| [CAP-08](../../../capability-map.md#cap-08) — Governed AI gateway | Mandatory. Move both of the orchestrator Lambda's Bedrock calls onto the gateway; the team confirmed it is the only Bedrock caller. The extraction call sends one PDF, which only the gateway's Responses route carries to Bedrock — see Risks. | P0 launch | ✅ Available | *Pending* |
| [CAP-02](../../../capability-map.md#cap-02) — Model registry | Use an approved model offering in a region the data may be processed in; the Lambda's current model IDs and region are not yet known. | P0 launch | ✅ Available | *Pending* |
| [CAP-04](../../../capability-map.md#cap-04) — Deployment registry | Deploy the application to each environment gateway it uses; a credential exists only for a deployed (resource, gateway) pair. | P0 launch | ✅ Available | *Pending* |
| [CAP-06](../../../capability-map.md#cap-06) — Machine identity | Attribute the Lambda's non-interactive calls to a credential the application owns, held in the team's secret store. | P0 launch | ✅ Available — hardening in flight upstream | *Pending* |
| [CAP-07](../../../capability-map.md#cap-07) — RBAC and access policy | Allow the application only the approved model offering(s). | P0 launch | ✅ Available | *Pending* |
| [CAP-10](../../../capability-map.md#cap-10) — Guardrails | Mandatory, although the team answered "no data guardrails" when asked in the session. Prompts carry client names, account numbers and statements; agree scope, mode and entities with Privacy, because PII redaction would change the data the extraction depends on. | P0 launch | ✅ Available | *Pending* |
| [CAP-11](../../../capability-map.md#cap-11) — Kill switch | Suspending the application stops automated validation; the manual process must be ready to absorb the volume. | P0 launch | ✅ Available | *Pending* |
| [CAP-12](../../../capability-map.md#cap-12) — Quotas and budgets | Up to about one million transfer requests a year, each needing two model calls (extraction and validation), and two more whenever a user confirms a name or rep-code mapping and the validation reruns. The session overview described cost caps, but no ACP limit holds at runtime until a counter store exists; correct that with the team. | P0 launch | ⚠️ Modelled, not enforced | *Pending* |
| [CAP-13](../../../capability-map.md#cap-13) — Attribute tagging | Record data classification, owner and region so access and guardrail policy can target the application. | P0 launch | ✅ Available | *Pending* |
| [CAP-15](../../../capability-map.md#cap-15) — Risk tiering | Apply the band from Sun Life's risk classification; the application's risk and LVT ratings are not yet known. | P0 launch | ✅ Available — band supplied by Sun Life | *Pending* |
| [CAP-18](../../../capability-map.md#cap-18) — Audit trail | Gateway decisions are audited; the application's own IGO/NIGO outcomes have no external producer path. | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-20](../../../capability-map.md#cap-20) — Observability and cost accounting | The benefit the session named: traces and token usage attributable to this application. | P0 launch | ✅ Available | *Pending* |
| [CAP-16](../../../capability-map.md#cap-16) — Model documentation | Conditional on E-23 scope. Ask Model Risk whether extraction plus an IGO/NIGO and ATON assessment brings the model in scope. | P1 fast follow | 🟡 Partial — build in flight | *Pending* |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation and assurance | Conditional on a customer-affecting decision. The team regards the tool as internal to Dealer Operations, but a NIGO result produces the email that goes back to the advisor and holds up the client's transfer, and the validation also makes the ATON or non-ATON determination; ask Risk whether that triggers it. | P1 fast follow | 🟡 Partial — build in flight | *Pending* |
| [CAP-26](../../../capability-map.md#cap-26) — Conditional access and data-flow control | Conditional on data residency. Client financial documents are likely to carry a residency obligation; do not assume the designed control is available. | P1 fast follow | 📐 Designed | *Pending* |

The capability map disagrees with itself in two places: its catalogue marks CAP-19 mandatory
although the sixteen-item baseline omits it, and the baseline shows CAP-18 as ✅ where the
catalogue row says 🟡 Partial. This spec follows the catalogue rows; raise both with the map's
owner, Seth Chalmers.

### Capabilities explicitly not required — pending review

| Capability | Why not |
|---|---|
| *None confirmed* | Nothing has been offered by ID and declined, and two session statements are not declines. That the application uses no agent, MCP server or agent-to-agent call describes today's implementation: offer CAP-03, CAP-23 and CAP-24 explicitly and record the decision here. "No data guardrails" cannot decline CAP-10, which is mandatory. |

> Any selected capability that is not ✅ becomes a row in the D1 Capability Gaps register and
> follows [Capability Gap Escalation](../../../process/capability-gap-escalation.md).

## Success Criteria

| Criterion | Measurement | Target |
|---|---|---|
| Lambda inference uses the governed ACP path | Trace a representative application request through the ACP gateway, and show that no direct Bedrock path remains — in code, in the Lambda's IAM permissions, or as a fallback | Every production model call carries an ACP trace; exact evidence and rollout scope agreed at D1 |
| Existing transfer validation behaviour is preserved | Compare IGO/NIGO and ATON/non-ATON outcomes and validation findings against the current production workflow using an agreed test set | No unintended behaviour change; test-set size and tolerance to be agreed |
| Inference usage is observable | Verify gateway traces and token usage are attributable to the onboarded application | Confirm required fields and access at D1 |
| Data handling and operational readiness are approved | Record data classification, approved model/data path, retention, logging, risk rating, availability targets, and fallback | Obtain required owners' confirmation before production ACP routing |
| Processing performance is understood | Measure end-to-end processing time and compare with the existing process | Establish a verified production baseline; reconcile reported 10–15-minute manual handling with the reported 2–3-minute application processing time |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|---|---|---|---|
| Harness SDK (Python 3.11+; the Lambda runs 3.12) and a supported way to send the extraction PDF through the gateway's Responses route, which the SDK does not call, with onboarding instructions, credentials, endpoint, and supported model route — Ranjula Rowel undertook in the session to provide these | ACP platform team | Hard | The Lambda cannot use the governed path until the integration contract and access are available |
| Application registration, machine identity, credentials, and access policy | ACP platform team and Security/IAM | Hard | Unavailable or mis-scoped credentials block or over-authorize inference |
| Lambda source/configuration change and release | RA&S application team | Hard | Direct Bedrock calls remain outside the ACP gateway until deployed and verified |
| Bedrock model availability, account, and region through ACP | ACP platform and AWS account owners | Hard | Model or regional mismatch can prevent inference or change operating characteristics |
| Inference pattern — I1 consumer-account (gateway role provisioned into the RA&S account by the `acp-aws-service-catalog` product) or I2 centralized | ACP platform team and RA&S AWS account owner | Hard | Decides who AWS bills, whose Bedrock quotas apply, and where model-invocation logging lands |
| Private network path from the Lambda to the gateway ingress in each environment | RA&S application team and network owners | Hard | No end-to-end test is possible until the Lambda can reach the gateway |
| Univeris API access (Dealer Contract Details and RWP Client Details) and existing validation rules | RA&S application team and Univeris owners | Hard | ACP onboarding must not disrupt business validation or introduce incorrect results |
| Data-flow details still missing (PDF size, Bedrock API and model, AWS accounts, network path) and production onboarding evidence | RA&S application team | Hard | Design review cannot assess data movement and security controls without these artifacts |
| Application inventory/monitoring details and Dealer Operations support model | RA&S team and application support | Soft | Production routing and incident handling may not meet support expectations |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Transfer forms and extracted content may contain client identity, account, signature, and financial information; classification and allowed data path are not established | Medium | High | Confirm classification, approved model and region, data minimization, encryption, access, and retention with Privacy/Security before routing production traffic |
| Existing direct Bedrock calls remain active or a fallback bypasses ACP | Medium | High | The team confirmed the orchestrator Lambda is the only Bedrock caller; remove its direct Bedrock permissions at cut-over, document fallback behaviour, and verify gateway traces after deployment |
| Extraction or model output contributes to a false IGO/NIGO or ATON/non-ATON result | Medium | High | Preserve the current human review and decision process, test representative forms and languages, and confirm whether any result is relied on without review |
| Retention has three answers: the session said uploaded forms leave S3 after one day or possibly 30 days, while the architecture diagram shows a 90-day S3 lifecycle rule and a daily job deleting database records older than 90 days | High | High | Confirm the bucket lifecycle policies, the database purge job and monitoring retention from configuration, and record the approved periods |
| CloudWatch is said to receive non-PII data only, but the diagram's list includes file names, which may carry client names, and neither the diagram nor the session covers ACP's own traces | Medium | High | Trace sensitive fields through application, Lambda, gateway, and observability sinks; confirm file-name conventions, redaction and access controls |
| CAP-12 is mandatory but quotas and budgets are modelled, not enforced | Medium | Medium | Do not represent configured quotas as spend controls; agree separate operational alerting and response expectations |
| The application availability/LVT rating and recovery expectations are unknown | Medium | Medium | Retrieve the APM record and confirm rating, support hours, recovery objectives, and manual processing fallback |
| A like-for-like port would drop the form itself. The extraction call sends one PDF, and the gateway's pinned `agentgateway` v1.5.0 silently discards PDF content on the chat-completions route, the only one the Harness SDK calls, and on the Anthropic Messages route. Only the Responses route turns an inline base64 PDF into a Bedrock document block | High | High | Route the extraction call through the Responses route, or agree another way to send the PDF, with the ACP platform team; run representative forms, including scanned and handwritten ones, through the gateway and compare input token counts and extracted fields with the direct call before any cut-over |
| Guardrails read only the last message's text in a chat request, and do not recognise a Responses request: they scan its whole body as text, base64-encoded PDF included, and apply any redaction to that raw body. Enforce-mode PII redaction would also rewrite the names and numbers the extraction depends on | Medium | High | Agree the guardrail scope (this application), mode and entities with Privacy; test that configuration on the Responses route with the agreed test set before production |
| Inference availability becomes bounded by ACP: every gateway request makes a synchronous access check against the PROD portal and is refused if the portal cannot be reached. At the time of the session no use case had been onboarded to ACP production, and the product team is taking LVT 4 (non-critical) applications first | Medium | High | Confirm the LVT rating before committing to a production date and compare it with ACP's availability and support model; document manual processing as the fallback, never a direct Bedrock call |
| Bedrock capacity and cost move with the call: the PROD install's DEV, SIT, STAGE and PROD gateways all run in the prod account today, so centralized inference would share its Bedrock limits with every other tenant; consumer-account inference keeps RA&S's limits but has not yet been rolled out to a real consumer account | Medium | Medium | Size call rate and tokens at D1; choose I1 or I2 before D2; load-test in a non-production environment |
| Credentials belong to a (resource, gateway) pair, and the DEV, SIT and STAGE gateways are due to move into their own accounts, so non-production credentials will have to be re-issued | Medium | Low | Hold the credential in the team's secret store with a re-issue runbook; schedule the re-issue with the gateway move |

## Open Questions

- [ ] What is the exact application name, owning team, repository, APM ID, and business contact for RA&S Dealer Transfer-in Xpress?
- [ ] What is the confirmed LVT/availability rating, recovery objective, support window, and acceptable downtime? Hardik Pillai expects a low rating because the tool serves Dealer Operations rather than clients or advisors; he and Satya Kant undertook to confirm it from the APM record or the support team's go-live assessment.
- [x] **PDF format and Bedrock callers** — the extraction call sends one PDF per request, holding the transfer form and the account statement, and the orchestrator Lambda is the only component that calls Bedrock (Satya Kant, Teams, 2026-10-07).
- [ ] How large are typical and maximum PDFs (pages and MB), through which Bedrock API (Converse or InvokeModel) are they sent today, and is the NIGO draft email written by the model or from a template?
- [ ] Which Bedrock model(s), AWS account(s) and region(s) does the Lambda use today, and what are its peak call rate and token volume?
- [x] **Lambda runtime** — Python 3.12 (Satya Kant, Teams, 2026-10-07), which the Harness SDK supports (Python 3.11+).
- [ ] What are the Lambda's timeout and retry settings and its latency per call? The SDK's default client timeout is 60 s and its default `max_tokens` is 1024, which may cut off a long JSON response; the Sun Life gateway's nginx front end accepts request bodies up to 25 MB, and base64 encoding adds about a third.
- [ ] Should ACP register this caller as an application or as an agent? The session offered both, with the client ID and secret kept in Vault or AWS Secrets Manager and exchanged for a token per call. Luminate can deploy an `Application` to a gateway and issue it an API key or OAuth client credentials, but the [Integration Patterns](../../platform/integration-patterns/d2-design.md) registration guide documents only agents, models and MCP servers. Who owns the credential, and how is it rotated and revoked?
- [ ] Confirm I1 consumer-account, where RA&S keeps Bedrock billing and quotas in the workload account it already uses, rather than I2 centralized. Which AWS account(s) are involved, and which RA&S environments map to which ACP environment gateways?
- [ ] How will the Lambda reach the gateway (VPC, egress, private endpoint, DNS) from each environment?
- [ ] Which form types and languages are in production? Hardik Pillai said all form types are now processed (an earlier phase covered specific types, such as RRSP forms) and the demo showed French; confirm coverage and the test set it implies.
- [ ] What are the verified annual volume, current adoption, actual processing-time distribution, and measurable accuracy/error rates? Hardik Pillai undertook to get the adoption numbers. Reconcile the stated manual 10–15 minutes with the application's reported 2–3 minutes.
- [ ] What is the actual S3 form-retention period? The session said one day or 30 days; the architecture diagram shows a 90-day lifecycle rule, and a 90-day purge of the database records that hold extracted data and validation results.
- [ ] What data is sent to CloudWatch or other logging/trace systems? Which fields are redacted, and what are the access and deletion controls? The same question applies to ACP's own traces once calls pass through the gateway; ACP offered a follow-up session to show what its traces and logs capture.
- [ ] What are the approved data classification, privacy/security guardrails, residency constraints, and model-use approvals for client transfer documents? Which guardrail mode and scope are acceptable, given that redaction alters the client data the extraction needs and that guardrails do not inspect document or image content?
- [ ] Does a person review every IGO/NIGO and ATON/non-ATON result before action? Users can already confirm an owner-name or rep-code mismatch, and that mapping is stored in the database; who owns decision accountability, and what is the process for uncertain extraction or validation results?
- [ ] Do IGO/NIGO and ATON/non-ATON results influence a customer-affecting decision (CAP-17 trigger), is the model in scope of E-23 (CAP-16 trigger), and do data-residency obligations apply (CAP-26 trigger)?
- [ ] What happens operationally if ACP, the gateway, Bedrock, or the Lambda integration is unavailable? Is manual processing the approved fallback?
- [ ] Confirm the full mandatory baseline by capability ID, including how CAP-01 applies to a non-agent application, how CAP-10 guardrails apply to client documents, and the limits of CAP-12 (not enforced), CAP-14 and CAP-18 (partial).
- [ ] What evidence will prove CAP-08 — that no direct Bedrock path remains in the orchestrator Lambda's code or IAM permissions, or as a fallback?

## References

- Raw discovery transcript: [ras-dealer-transfer-in-xpress-acp-discovery-session.vtt](references/ras-dealer-transfer-in-xpress-acp-discovery-session.vtt) — ACP & RA&S Dealer Transfer-in Xpress Discovery Session; the meeting date is not recorded in it.
- Readable discovery transcript: [ras-dealer-transfer-in-xpress-acp-discovery-session.txt](references/ras-dealer-transfer-in-xpress-acp-discovery-session.txt)
- Architecture diagram from the RA&S team (draw.io): [ras-dealer-transfer-in-xpress-architecture.drawio](references/ras-dealer-transfer-in-xpress-architecture.drawio)
- Follow-up answers from Satya Kant (RA&S) in the Teams chat, 2026-10-07: the orchestrator Lambda's runtime, the PDF it sends, and that it is the only Bedrock caller.
- [ACP Capability Map](../../../capability-map.md), including CAP-08 and the mandatory governance baseline.
- [Capability Gap Escalation](../../../process/capability-gap-escalation.md).
- [Integration Patterns](../../platform/integration-patterns/d2-design.md) — I1/I2 inference patterns, hosting shapes and registration.
- [Gateway Environment Strategy](../../platform/gateway-environment-strategy/d1-requirements.md) — the environment model onboarding specs use (FR-28).
- Source evidence read on 2026-10-06 and 2026-10-07 from the `edaeacp/luminate` mirror at `093285b` (2026-10-05): guardrail scan extraction `gateway/app/guardrails/input_extractor.py`; `/llm/` routing in `gateway/app/middleware/proxy.py`; the `agentgateway` v1.5.0 pin in `gateway/Dockerfile` and its upstream `crates/llm/src/conversion/bedrock.rs` (chat-completions, Messages and Responses conversions); the `Application` resource in `backend/app/applications/models.py`, its deployments in `backend/app/deployments/models.py` and API keys in `backend/app/gateways/models.py`. From `luminate-sunlife-deploy`: the gateway's nginx body limit in `helm/luminate-portal/templates/gateway/nginx-configmap.yaml` and gateway topology in `docs/architecture.md`. From `acp-harness-sdk` at `d84337c`: `src/acp_harness_sdk/gateway.py` and `pyproject.toml`.
- [AWS Harness Integration with Luminate](../../integration/aws-harness-integration/d0-discovery.md).