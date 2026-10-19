# Netskope Unblock Request — Hugging Face Mirror in Artifactory (Dev POC)

> **Component**: `slm-pipeline` · **Epic**: EACPP-557 · **Task**: EACPP-559 (ISRA support + Netskope unblock)
> **Phase**: 0 (interim POC) · **Environment**: Dev only
> **Status**: Draft for submission — fields marked **`<FILL>`** need values from the requestor / network / Artifactory teams.

This request enables a **read-only, pull-through (remote/proxy) Hugging Face mirror** in the
**dev** JFrog Artifactory instance (`dev-artifactory.sunlifecorp.com`). `huggingface.co` is
currently blocked by Netskope (category **Generative AI / AI**, SLF Block). We are **not** asking to
unblock Hugging Face for the user estate — only for the **Artifactory dev server egress**, so that
Artifactory can cache vetted model weights that are then screened by Sonatype Repository Firewall and served internally. No
end-user or EKS workload talks to Hugging Face directly.

---

## 1. Request Summary

| Field | Value |
|-------|-------|
| Request title | Unblock `huggingface.co` (+ HF content domains) for Artifactory **dev** egress only |
| Requestor | `<FILL: name, SLF email, login>` |
| Business / product owner (sponsor) | `<FILL: ACP product owner>` |
| Team | EDAE — Agentic Control Plane (ACP) |
| Related ISRA | `<FILL: in-flight ISRA / Archer ID>` |
| Related change/ticket | EACPP-559 · ServiceNow `<FILL: INC/CHG/RITM>` |
| Date needed by | `<FILL>` |
| Duration | **Time-boxed POC** — `<FILL: e.g. 90 days>`, review/renew at Phase-1 ISRA+ATG |
| Reversibility | Fully reversible — remove the policy exception; delete the Artifactory remote repo |

---

## 2. Business Justification

As part of the Agentic Control Plane initiative we are running a POC to establish a **governed,
single-source supply chain for open-weight Small Local Models (SLMs)**. Today there is no compliant
path to bring model weights from Hugging Face into our environment: `huggingface.co` is blocked, so
teams have no vetted, scanned, auditable way to obtain weights, which pushes activity toward
uncontrolled channels (developer laptops, public mirrors).

A **read-only Hugging Face remote repository in Artifactory** solves this: Artifactory becomes the
**only** egress point to Hugging Face, caches the artifacts, runs **Sonatype Repository Firewall** supply-chain
scanning on everything it mirrors, and serves the weights internally. This:

- Confines Hugging Face egress to **one hardened server** instead of the user/EKS estate.
- Adds **malware / vulnerability / license screening** (Sonatype Repository Firewall) on every artifact.
- Produces a **full audit trail** of what was pulled, when, and by whom.
- Is **read-only** (GET/HEAD pull-through only) — no uploads or pushes to Hugging Face.

POC scope is intentionally narrow: **dev Artifactory only**, and the repository is restricted by
include-pattern to **Gemma 3n E2B / E4B** model repos for the POC.

---

## 3. Source (who is allowed out) — scope the exception tightly

The exception must apply **only** to the Artifactory dev server's outbound egress, **not** to steered
user traffic.

| Field | Value |
|-------|-------|
| Source host(s) | `dev-artifactory.sunlifecorp.com` (Artifactory dev) |
| Source egress public IP / NAT IP(s) | **`<FILL: Artifactory dev NAT/egress IP or CIDR>`** (from Network team) |
| Steering scope | Server egress / explicit-proxy bypass for these IPs only — exclude from the general "Generative AI" user block |
| Everyone else | **No change** — `huggingface.co` stays blocked for all users and all other workloads (incl. EKS) |

> Netskope policy hint: scope by **source IP/CIDR** (the Artifactory egress), not by user/group, since
> Artifactory is a service account / server, not a steered client. If Artifactory reaches the internet
> via an explicit forward proxy, the equivalent allow must be set there too.

---

## 4. Destination (what to allow) — Hugging Face content domains

Hugging Face downloads are a multi-host flow: the Hub API on `huggingface.co` returns the repo
metadata, then `/{repo}/resolve/{rev}/{file}` issues a **302 redirect** to a CDN/object store for the
actual bytes. Modern repos use the **Xet** content-addressed backend; older/LFS repos use the LFS CDN.
**All** of the following must be allowed (HTTPS / TCP 443, outbound) or downloads will stall at the
blob fetch:

| # | Destination (FQDN / wildcard) | Purpose | Protocol/Port |
|---|-------------------------------|---------|---------------|
| 1 | `huggingface.co` | Hub API, repo metadata, `/resolve/` redirects, Xet token issuance, repo cards | HTTPS / 443 |
| 2 | `*.huggingface.co` | LFS CDN hosts: `cdn-lfs.huggingface.co`, `cdn-lfs-us-1.huggingface.co`, `cdn-lfs-eu-1.huggingface.co` (large weight blobs) | HTTPS / 443 |
| 3 | `hf.co` | Short domain / canonical host used by the client and redirects | HTTPS / 443 |
| 4 | `*.hf.co` | Xet backend root (e.g. `xethub.hf.co`) | HTTPS / 443 |
| 5 | `*.xethub.hf.co` | Xet CAS / transfer hosts: `cas-server.xethub.hf.co`, `transfer.xethub.hf.co` (default high-perf transfer path) | HTTPS / 443 |

**Notes for the reviewer**

- Domains #2/#4/#5 are CDN/object-store fronts (AWS CloudFront / Xet on AWS). The **SNI presented is the
  Hugging Face FQDN**, so allow-listing these FQDNs is sufficient with Netskope domain steering — we do
  **not** need to open broad `*.cloudfront.net` / `*.amazonaws.com`. If your steering resolves to the
  backing CDN hostname instead of SNI, flag it and we'll supply the CloudFront distribution domains.
- **Direction**: outbound only. **Methods**: GET / HEAD (read-only pull-through). No POST/PUT to HF.
- **No authentication / tokens** are required for public open-weight models; the repo is anonymous
  pull-through. (If a gated model is ever needed, a read-only HF token would be stored in
  Artifactory/Vault — out of scope for this POC.)

---

## 5. SSL Inspection / Decryption

| Field | Recommendation |
|-------|----------------|
| TLS inspection | **Bypass decryption** for the destinations in §4 from the Artifactory source. |
| Why | Traffic is large binary model artifacts (multi-GB, up to ~50 GB/file). Decrypting adds latency and offers no DLP value on **inbound** open-source weights. **the Sonatype firewall** already screens every component for malware/CVEs/license at ingestion — quarantining bad artifacts before they are cached — which is the meaningful control point. |
| If decryption is mandatory | Acceptable functionally (no HF cert pinning for these hosts), but expect throughput impact; ensure the Netskope CA is trusted on the Artifactory host. |

---

## 6. Data / Risk Considerations

| Question | Answer |
|----------|--------|
| Data leaving the org? | **No.** Read-only inbound download of public open-weight models. No SLF data is sent to Hugging Face (telemetry can be disabled via `HF_HUB_DISABLE_TELEMETRY=1`). |
| Data classification | Public open-source model artifacts. |
| Who can reach it | Only the Artifactory dev server (§3). EKS / users have **no** direct path (verified). |
| Compensating controls | Sonatype Repository Firewall screening on every component (criticals block publish); include-pattern allowlist (Gemma 3n only for POC); pinning by revision + content digest; full Artifactory audit log; ACP Model Registry approval gate before anything is served. |
| Blast radius if abused | Limited to one server pulling from a single known domain set; read-only; no upload path; time-boxed. |
| Rollback | Remove Netskope exception and/or delete the Artifactory remote repo. |

---

## 7. How the Mirror Is Configured (context for reviewers)

JFrog Artifactory **Hugging Face ML — Remote** repository (proxy / pull-through):

| Setting | Value |
|---------|-------|
| Repository type | Hugging Face ML, **Remote** |
| Upstream URL | `https://huggingface.co` (the HF default endpoint) |
| Mode | Pull-through cache — Artifactory fetches on first request, then serves from cache |
| Restriction | Include-pattern allowlist scoped to **Gemma 3n E2B / E4B** repos for the POC |
| Scanning | Sonatype Repository Firewall enabled on the repo; critical findings block publish/serve |
| Artifactory version | v7.104.15 (ML repo layout) |
| Write access | None — remote/read-only by definition |

Consumption path: internal clients set `HF_ENDPOINT` to the Artifactory virtual repo URL (e.g.
`https://dev-artifactory.sunlifecorp.com/artifactory/api/huggingfaceml/<repo-key>`) so the standard
`huggingface_hub` / `transformers` tooling pulls **through Artifactory** rather than the internet.

---

## 8. Acceptance / Verification (post-unblock)

1. From the Artifactory dev host: `curl -I https://huggingface.co` → 200/redirect (was blocked).
2. Configure the HF remote repo (§7); trigger a Gemma 3n pull through Artifactory.
3. Confirm the blob fetch follows to the LFS/Xet CDN host and completes (validates §4 domains).
4. Confirm the Sonatype firewall screens/quarantines the cached component.
5. From a **non-Artifactory** host / EKS pod: `curl https://huggingface.co` → **still blocked**
   (validates the exception is source-scoped).
6. Capture evidence for the ISRA / Archer record.

---

## 9. Open Items for the Requestor to Fill

- [ ] Artifactory dev **egress/NAT public IP(s) or CIDR** (Network team) — §3
- [ ] Requestor, sponsor, ISRA/Archer ID, ServiceNow ticket — §1
- [ ] POC duration / expiry date — §1
- [ ] Confirm whether Artifactory egresses directly or via a forward proxy (affects where the allow is applied)
- [ ] Confirm SSL-inspection decision with InfoSec — §5
