# Action Plan — ISRA 26-1260 · Risk R011092 (Website Unblock — Hugging Face)

> **Component**: `slm-pipeline` · **Epic**: EACPP-557 · **Task**: EACPP-559 (ISRA support + Netskope unblock)
> **For**: Nabeel Khan (Information Security Advisor) · **From**: `<FILL: requestor>` · **Sponsor**: `<FILL: ACP product owner>`
> **Date**: 2026-06-17 · **Target completion**: `<FILL: target date>` · **Status**: Draft for ISA review

| Field | Value |
|-------|-------|
| ISRA | 26-1260 — Website Unblock — Hugging Face |
| Risk | R011092 |
| Risk rating | Low |
| Risk owner / sign-off | `<FILL: leadership name + title>` |
| Response strategy | **Mitigate** — replace the requested broad website unblock with a read-only, scanned Artifactory pull-through mirror scoped to a single server |

---

## 1. Summary

The risk as written assumes **users are granted browser access to `huggingface.co`**, which would allow
(a) uploading Sun Life Confidential data and (b) pulling unapproved open-source software. **That is not
what we are deploying.** We are **not unblocking Hugging Face for users or workloads.** We are standing
up a **read-only (download-only) Hugging Face *remote/pull-through* repository in JFrog Artifactory**,
and unblocking `huggingface.co` **only** from the Artifactory dev server's egress IP. Both risk vectors
are removed or compensated by design:

- **No upload path exists** — the mirror is read-only (GET/HEAD); users never reach Hugging Face; the
  only host allowed out is a service, not a person, so there is no interactive channel to upload data.
- **No unapproved software** — every artifact is allow-listed against the **ACP Model Registry approved
  set**, screened by **Sonatype Repository Firewall**, and pinned by digest; anything not approved is fail-closed denied.

This converts an "allow a GenAI website" risk into a "governed internal artifact cache" posture.

---

## 2. Direct Response to the Risk Description

The risk description has three clauses. Each is addressed below.

| Risk clause (R011092) | Why it does not apply / how it is mitigated |
|-----------------------|---------------------------------------------|
| *"Hugging Face has the capability for file uploads… users may intentionally or unintentionally upload Sun Life Confidential Data."* | **No user and no workload is granted access to huggingface.co.** Netskope keeps the existing **block in place for the entire user estate and EKS**. The only exception is the **Artifactory dev server egress IP**, and that path is configured as a **read-only pull-through cache (GET/HEAD only)** — Artifactory has **no upload/push capability to Hugging Face** in remote-repo mode. There is therefore no interactive browser session and no write channel through which Confidential data could be uploaded. **DLP exposure: eliminated by removing the upload path entirely.** |
| *"Allowing access to an external repository which hosts pre-trained AI models…"* | Access is **not** granted broadly. It is confined to **one hardened server** acting as a controlled gateway, not the user population. Egress is scoped by **source IP** in Netskope (Artifactory only) and by **destination FQDN allow-list** (the specific Hugging Face content domains — see the Netskope unblock request). |
| *"…potential for downloading open-source unapproved software."* | The mirror is **default-deny**. Only models **approved in the ACP Model Registry** are projected into the Artifactory include-pattern allow-list; for the POC this is restricted to **Gemma 3n E2B/E4B** only. Every cached artifact is **scanned by Sonatype Repository Firewall** (malware / CVE / license), **pinned by revision + SHA-256 digest**, and **safetensors-preferred (pickle rejected)**. Unapproved or unscreened artifacts are never served. **"Unapproved software" cannot transit the mirror.** |

---

## 3. Controls (the action plan)

| # | Control | Addresses | Owner | Target |
|---|---------|-----------|-------|--------|
| A1 | Keep `huggingface.co` **blocked** for all users + EKS; unblock **only** the Artifactory dev egress IP (source-scoped Netskope policy) | Upload DLP; broad access | Network / InfoSec | `<FILL>` |
| A2 | Artifactory HF repo configured as **Remote / pull-through, read-only** (GET/HEAD) — no upload/push to HF | Upload DLP | Platform / Artifactory | `<FILL>` |
| A3 | Destination allow-list limited to the required HF content FQDNs over 443 outbound (no broad CDN opening) | Broad access | Network / InfoSec | `<FILL>` |
| A4 | **Include-pattern allow-list** driven by the **ACP Model Registry approved set**; default-deny; POC = Gemma 3n only | Unapproved software | ACP / Model Registry | `<FILL>` |
| A5 | **Sonatype Repository Firewall** policy on the proxy repo — quarantines malicious / policy-violating components (malware, critical CVE, disallowed license) at ingestion, before caching | Unapproved software | Platform / Security | `<FILL>` |
| A6 | **Digest/revision pinning** + checksum verification; floating tags rejected | Unapproved software; integrity | ACP | `<FILL>` |
| A7 | **Safetensors preferred, pickle rejected/sandboxed** | Malicious model weights | ACP | `<FILL>` |
| A8 | **Telemetry disabled** (`HF_HUB_DISABLE_TELEMETRY=1`) so no metadata egresses to HF | Data leakage | ACP | `<FILL>` |
| A9 | **Full audit trail** in Artifactory (what was pulled, when) + Model Registry transition audit | Monitoring / assurance | ACP | `<FILL>` |
| A10 | **Time-boxed POC** (`<FILL: e.g. 90 days>`, dev only); Phase 1 broad rollout gets a **separate ISRA + ATG** | Scope containment | ACP | `<FILL>` |

---

## 4. Residual Risk & Monitoring

- **Residual rating**: Low → **negligible** for the DLP/upload vector (the upload path is removed, not merely monitored).
- **Monitoring**: Netskope logs confirm HF reachable **only** from the Artifactory egress IP; periodic verification that a non-Artifactory host / EKS pod still receives a block. Sonatype firewall dashboards evidence 100% screening coverage. Model Registry audit evidences approvals.
- **Trigger to revisit**: any expansion beyond dev, beyond Gemma 3n, or any request to enable uploads/gated-model tokens → new risk review under the Phase 1 ISRA.

---

## 5. Verification (post-implementation evidence for the ISRA record)

1. From the Artifactory dev host: `curl -I https://huggingface.co` → succeeds.
2. From an EKS pod / standard workstation: `curl https://huggingface.co` → **still blocked** (proves source scoping).
3. Trigger an approved Gemma 3n pull through Artifactory → Sonatype firewall screen recorded; artifact pinned by digest.
4. Confirm Artifactory remote repo has **no upload/deploy** capability to the HF upstream.
5. Attempt to pull a non-allow-listed repo → denied (fail-closed).
6. Capture all of the above as evidence attached to ISRA 26-1260 / R011092.

---

## 6. Sign-off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Requestor | `<FILL>` | Submitted | 2026-06-17 |
| Product owner / sponsor | `<FILL>` | | |
| Leadership (risk acceptance) | `<FILL>` | | |
| Information Security Advisor | Nabeel Khan | | |

---

## 7. Open Items for the Requestor

- [ ] Artifactory dev **egress/NAT public IP(s)** — A1/A3
- [ ] Requestor, sponsor, leadership signer names — §6
- [ ] POC duration / target dates per control — §3
- [ ] Confirm SSL-inspection decision with InfoSec — see [Netskope unblock request](netskope-unblock-request.md)

> **Supporting documents**: [Netskope unblock request](netskope-unblock-request.md) (destination domains, source scoping, Sonatype firewall compensating control) · `ACP-HuggingFace-Mirror-ISRA.pptx` (architecture deck) · [SLM Pipeline D2 Design](../d2-design.md) (mirror download controls C1–C10, exact Model Registry API).
