# Build pipeline — the approved path and what its gates actually prove

The substance here is the same as
[`mcp-server-patterns` · Build pipeline](../../mcp-server-patterns/d2-design/pipeline.md), and this
page does not restate it in full. What it does is re-verify the two claims that matter, because
both were checked again for this spec and both still hold, and add the parts specific to an
agent.

An agent is not exempt because it is "just a client". It executes model-composed instructions,
pulls a large and fast-moving dependency tree, and holds a credential that reaches a governed
model and a system of record.

## The path

| Stage | JTE library | Requirement |
|---|---|---|
| Agent | `pod_template` | `iac-build-agent` or a language agent |
| Checkout | `git` | — |
| Build + unit test | `python` / `npm` / `maven` / `gradle` / `dotnet` | ASR-25 |
| Static analysis | `sonarqube` | ASR-28 |
| SCA | `snyk` (or the language library's `sca_scan`) | ASR-27 |
| SAST | `checkmarx` | ASR-26 |
| Image | `quay` / `ecr` | ASR-28 |

Configuration lives in `Jenkinsfile` + `pipeline_config.groovy`. The libraries are in
[`CSDP/pipeline-libraries`](https://bitbucket.sunlifecorp.com/projects/CSDP/repos/pipeline-libraries/browse).

## The library defaults are strict. The estate overrides them.

The gates ship **on**: `snyk` defaults `RUN_SNYK_SCAN = true`, `ENFORCE_SNYK_GATE = true`,
`SEVERITY_THRESHOLD = "high"`; `checkmarx` defaults `ENFORCE_CHECKMARX_GATE = true`.

Re-checked 2026-09-08 against the ACP repositories, including the one that *is* the agent
adoption path:

```groovy
// acp-harness-sdk/pipeline_config.groovy
run_snyk_scan = true
enforce_snyk_gate = false
disable_gate_reason_snyk = 'Snyk gate is disabled during initial CI setup for acp-harness-sdk.'
enforce_checkmarx_gate = false
disable_gate_reason_checkmarx = 'Checkmarx gate is disabled until the issue with
    java.lang.Exception: Host name and enforceCheckmarxGate is set to true is resolved.'
```

`agent-control-plane-ui` carries the same two overrides with the same Checkmarx reason. The scans
run; nothing fails on them. Each reason describes a setup-era workaround that has outlived its
setup.

**ASR-28: a disabled gate is an exception with an owner and an expiry, not a default.** An agent
repository is not the place to carry the estate's habit forward.

## A green Checkmarx stage is not a scan

`libraries/checkmarx/steps/code_analysis.groovy` does not scan. It resolves the latest **merged
pull request** for the repository, looks up the scan Checkmarx already ran for that PR, waits for
the gate evaluation and reports it. A repository with no merged PR logs

```text
New repository PR does not exist. Checkmarx scan is skipped.
```

and passes. The default `branches_to_scan` is `["develop"]`, so a repository whose integration
branch is `main` — which is every ACP repository — matches nothing unless it overrides.

**ASR-26 requires the scan id and the gate evaluation, not the stage colour.** This is the single
most load-bearing evidence rule in the profile, and it is inherited from the MCP pattern
unchanged because the defect is in the shared library.

## Agent-specific additions

| Concern | Why it is different for an agent | Requirement |
|---|---|---|
| **Dependency surface** | Agent frameworks pull deep, fast-moving trees — LangGraph, Strands, the AgentCore SDK, MCP clients, and whatever a tool integration drags in. Transitive CVEs land weekly | ASR-27, with the SBOM retained per build |
| **Prompt and tool assets** | System prompts, tool descriptions and skill definitions are code by any useful definition: they change behaviour, they are not covered by SAST, and a change to one can widen what the agent does | Review them under change control alongside code; ASR-12 keeps the catalogue record current |
| **Base images** | No `docker.io` egress from Sun Life cluster pods. Every base and runtime image must be mirrored to Quay or ECR first | ASR-28 |
| **Model and tool pinning** | An agent that resolves its model or its MCP endpoint at runtime from configuration can change what it reaches without a build. Pin them, or make the configuration a governed change | ASR-12, ASR-20 |
| **Lambda packaging** | A signed zip is acceptable in place of an image, provided it is produced by the same pipeline and referenced by version, never `$LATEST` | ASR-28 |
| **AgentCore packaging** | The runtime image is built by the JTE path and pushed to ECR like any other. AgentCore being managed does not move the supply chain out of scope | ASR-25 – ASR-28 |

## Evidence, per requirement

| Requirement | Evidence an assessor can retrieve |
|---|---|
| ASR-25 | The Jenkins job and its stage list |
| ASR-26 | The Checkmarx **scan id** and its gate evaluation, recorded on the build |
| ASR-27 | `snyk-results.html` and `snyk-sbom.json` as build artifacts |
| ASR-28 | SonarQube project + quality-gate status; registry digest matching the deployed digest; `runAsNonRoot` in the manifest |

> **The rule that makes this section worth anything:** a control is met when its artefact is
> retrievable. A green pipeline is not an assessment — the Checkmarx step reports success when no
> scan exists.
