# D2 Design — The Agent Pattern

> **Gate**: D2 — Design | **Status**: Draft | **D1 Approved**: TBD
>
> `d2-design.md` beside this directory is **generated** from these pages by
> `scripts/assemble_d2_design.py` — edit the pages, not the generated file.

## The distinction that organises everything

An MCP server is only ever called. An agent both calls and is called, and those are two
registrations with two requirement sets. Establish which one you need before anything else.

**But first, one question comes before even that: is it an Agent at all?** The platform has two
consumer identities. **A chatbot is an Application, not an Agent** — and an Application is
egress-only by construction: no `ApplicationDeployment`, and no `application` member on
`AccessPolicyTargetType`, so nothing can ever be routed to it or granted it. The deciding test is
*can anything need to call it?* — see [Registration](registration.md).

```mermaid
flowchart LR
    subgraph EG["EGRESS — the agent as caller"]
      direction TB
      A1["Agent record<br/>+ Deployment<br/>+ credential"]
      A2["AccessPolicy<br/>source_agent → target"]
      A3["calls /llm · /mcp · /a2a"]
      A1 --> A2 --> A3
    end
    subgraph IN["INGRESS — the agent as callee"]
      direction TB
      B1["Agent record<br/>+ Deployment<br/>+ **AgentDeployment**<br/>endpoint_name · backend_endpoint"]
      B2["AccessPolicy<br/>source → target_agent"]
      B3["served at /a2a/{endpoint_name}"]
      B1 --> B2 --> B3
    end
    style A1 fill:#e3f2fd,stroke:#1565c0
    style B1 fill:#e8f5e9,stroke:#2e7d32
```

**Registering an agent and granting it a model makes it a governed caller. It does not make it
callable.** The thing that makes it callable is an `AgentDeployment` — a row carrying an
`endpoint_name` and a `backend_endpoint`. Eight of the ten agents registered in SLF dev do not
have one, and one of them is already the target of an active access policy.

## The pattern in one picture

```mermaid
flowchart LR
    subgraph caller["Calling workload"]
        A["Agent A<br/>holds a machine credential"]
    end
    subgraph acp["ACP · Luminate"]
        GW["Gateway<br/>/llm · /mcp/{ep} · /a2a/{ep}"]
        P["Portal<br/>catalogue · CheckAccess<br/>RFC 8693 exchange"]
    end
    subgraph targets["What A may reach"]
        M["Model"]
        T["MCP server"]
        B["Agent B<br/>A2A JSON-RPC"]
    end

    A -->|"1 · Bearer"| GW
    GW -->|"2 · CheckAccess<br/>source, target_type, selector"| P
    GW -->|"3 · forward"| M
    GW -->|"3 · forward per identity mode"| T
    GW -->|"3 · **exchange**, then forward"| B
    P -.->|"config push"| GW
    style B fill:#e8f5e9,stroke:#2e7d32
    style GW fill:#e3f2fd,stroke:#1565c0
```

Steps 1 and 2 are identical on all three lanes. Step 3 is where they differ, and the A2A lane is
the one with a token exchange in the middle of it.

## Pick your shape

Four questions, answered in order. The first decides which requirement set you are reading; the
second is disqualifying for ingress; the third decides your substrate annex; the fourth decides
what your agent must implement.

```mermaid
flowchart TD
    Q0{"Is it an Agent,<br/>or an Application?"}
    Q0 -->|"nothing will ever call it —<br/>chatbot, batch job, UI backend"| APP["**Application.**<br/>Egress-only by construction.<br/>No endpoint, no target policy,<br/>no governance sweep"]
    Q0 -->|"something may call it"| Q1
    Q1{"Will another agent<br/>need to invoke yours?"}
    Q1 -->|"no — it only calls out"| EGO["**Egress only.**<br/>Agent record + Deployment<br/>+ credential + source policies.<br/>Record the decision — otherwise<br/>it reads as an omission"]
    Q1 -->|yes| Q2{"Is it a remote HTTP service<br/>speaking A2A JSON-RPC?"}
    Q2 -->|"no — a library, a queue<br/>consumer, an SDK entry point"| X["**Cannot be an A2A callee.**<br/>Front it with an A2A HTTP<br/>service first"]
    Q2 -->|yes| Q3{"Where does it run?"}
    Q3 -->|"OpenShift"| H1["**S1 · OpenShift**<br/>corp ingress · SLF PKI in the<br/>gateway's merged trust bundle"]
    Q3 -->|"EKS, gateway's cluster"| H2["**S2 · EKS in-cluster**<br/>ClusterIP · NetworkPolicy<br/>is the control"]
    Q3 -->|"Bedrock AgentCore"| H3["**S3 · AgentCore**<br/>VPC endpoint · custom JWT<br/>authorizer · encode the ARN"]
    Q3 -->|"AWS Lambda"| H4["**S4 · Lambda**<br/>Function URL or API GW ·<br/>cold start vs the token cache"]
    H1 & H2 & H3 & H4 --> Q4{"Can the serving gateway<br/>run the on-behalf-of exchange?"}
    Q4 -->|yes| I1["**Delegated.** Your agent receives<br/>a token audienced to its<br/>**deployment** and must validate it"]
    Q4 -->|no| I2["**Withheld.** 503 at the gate.<br/>Serving it would reach your agent<br/>as the gateway — see Identity"]
    style EGO fill:#e3f2fd,stroke:#1565c0
    style APP fill:#ede7f6,stroke:#5e35b1
    style X fill:#ffebee,stroke:#c62828
    style I2 fill:#fff8e1,stroke:#f9a825
    style I1 fill:#e8f5e9,stroke:#2e7d32
```

## The catalogue of shapes

| # | Shape | Who it is for | Egress | Ingress | Maturity |
|---|---|---|:--:|:--:|---|
| **S1** | **OpenShift-hosted** — behind Sun Life corporate ingress | Teams already on OpenShift | ✅ | ⚠️ needs SLF PKI in the gateway bundle | **Not yet exercised** for A2A |
| **S2** | **EKS in-cluster** — ClusterIP beside the gateway | Platform-owned and demo agents | ✅ | ✅ | **Works today** — `policy-assistant` |
| **S3** | **Bedrock AgentCore runtime** | Teams on AWS with an AgentCore footprint | ✅ | ✅ *(dev)* | **Works today via a VPC endpoint** — `fdes-pharmacy-agent`. Prod's registration is a different shape and serves no credential |
| **S4** | **AWS Lambda** | Event-driven and thin agents | ✅ | ⚠️ needs a stable URL | **Not yet exercised**; cold start vs the token cache is the real constraint |

Four substrates are specified in detail because they are in use or in flight. **They are not the
allowed list.** Any other hosting platform — vendor agent products, managed runtimes, whatever
ships next — is admitted on the same terms: assessed against the numbered **SUB-E** and **SUB-I**
criteria in [Hosting](hosting.md). Meeting the egress set makes a platform viable for agents that
consume AI resources; meeting both makes it viable for agent-to-agent delegation. A platform that
falls short has a *named open criterion*, not a refusal.

## What is true on every shape

These are platform properties a team cannot change, and they drive most of the profile.

| Property | Consequence for the agent |
|---|---|
| **Registration ≠ reachability.** An `AgentDeployment` is what emits a route | Declare your direction, and create the deployment if you want to be callable — [Registration](registration.md) |
| **One route per agent deployment.** `pathPrefix = /{endpoint_name}`; no shorthand ever existed for A2A | Your agent owns a path segment and is addressed at `{gateway}/a2a/{endpoint_name}`, **not** by its id or key |
| **There is no agent identity mode.** `Agent` has no `identity_mode`; `AgentAssignment` has no `backend_auth` | Every routable deployment is a delegated target. The only alternative is the degrade path, which sends nothing — [Identity](identity.md) |
| **The control plane is on the request path.** `CheckAccess` per request, no cache; portal unreachable → deny | Your availability is bounded by the portal's; there is no fail-open posture |
| **Authorization is per agent, in each direction separately** | A source grant covers everything that agent may do; a target grant covers every method it exposes — [Authorization](authorization.md) |
| **No guardrail can target an agent** | You cannot require a scan of your own inbound traffic. Every caller must carry one |
| **Quotas are not enforced anywhere** | Bound yourself at the substrate |
| **There is no REST lane.** The gateway matches `/llm/`, `/mcp/` and `/a2a/` and nothing else | An enterprise API is reached through an MCP server, and the API Platform owns that hop — [Reaching a REST API](api-access.md) |
| **The platform never probes your agent** | Health, restarts and capacity are entirely yours — [Operations](operations.md) |
| **Deactivation stops ingress, not egress** | The stop path is credential and policy revocation — [Operations](operations.md) |
| **The registered query string is discarded** on the A2A hop | Put everything you need in the path — [Registration](registration.md) |

## Reading order

| Page | Covers | Answers |
|---|---|---|
| [Registration](registration.md) | **Agent vs Application**, the catalogue model, deployments, credentials, endpoint hygiene, lifecycle | *Is it even an agent — and what makes me reachable?* |
| [Hosting](hosting.md) | S1–S4, the SUB-E / SUB-I admission bar, reachability, TLS, network control | *What must my platform provide?* |
| [Identity](identity.md) | What the agent holds; what a callee receives; the exchange; RFC 9728 | *What credential reaches me, and what do I validate?* |
| [Authorization](authorization.md) | Source and target policies, the boundary, guardrails, quotas | *What is actually enforced, and what must I enforce?* |
| [Reaching a REST API](api-access.md) | The MCP boundary, the Keycloak→Okta break, API Resources and Skills | *How do I call a business system, and whose identity arrives?* |
| [Build pipeline](pipeline.md) | The JTE path, SonarQube / Snyk / Checkmarx, image provenance | *How do I build it so it will be accepted?* |
| [Operations](operations.md) | Audit, tracing, run correlation, cost, the stop path | *What is visible once it runs, and how do I stop it?* |
| [ETAB and ISRA](assurance.md) | The architecture to present and the control table to assess | *What do I take to the board?* |
| [Gaps](gaps.md) | What is blocked, who owns the ask | *What am I accepting as residual?* |

## The two rules that catch everyone

**1 · Registered is not reachable.**

```mermaid
flowchart LR
    P["AccessPolicy<br/>claims-intake → **agent** claims-adjudicator<br/>status: active"] --> G{"route for<br/>claims-adjudicator?"}
    G -->|"no AgentDeployment"| F["**Fails at the proxy hop.**<br/>Authorized, then unroutable.<br/>Nothing reconciles the two"]
    style F fill:#ffebee,stroke:#c62828
```

That policy is live in SLF dev today.

**2 · Deactivating an agent does not stop it.**

```mermaid
flowchart TD
    K["Agent.status = inactive"] --> IN["**Ingress: stopped.**<br/>authz.rego requires<br/>agent.status == 'active'<br/>on the target"]
    K --> EG["**Egress: unaffected.**<br/>_source_matches compares<br/>policy.source_id to jwt.sub<br/>and never reads status"]
    EG --> R["Real stop = revoke the credential<br/>+ revoke the source policies"]
    style IN fill:#e8f5e9,stroke:#2e7d32
    style EG fill:#ffebee,stroke:#c62828
```

Design your incident runbook around the right-hand branch, not the left.
