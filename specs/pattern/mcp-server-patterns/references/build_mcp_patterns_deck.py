#!/usr/bin/env python3
"""Generate the MCP Server Patterns architecture brief for ETAB / ATG / ISRA.

Content is derived from specs/pattern/mcp-server-patterns/ (D0-D3). Every factual claim on
these slides is verified in the spec against luminate origin/main @ 10d6ee89, the
live SLF dev estate, and CSDP/pipeline-libraries, all read 2026-09-01.

Visual language deliberately matches acp-consortium-specs/atg_isra_aug20/
build_luminate_identity_deck.py so the two submissions read as one series.

The repo's committed .venv does not carry python-pptx, so install it into a
throwaway environment rather than adding ~10 MB of packages to a tracked venv::

    python3 -m venv /tmp/deckenv && /tmp/deckenv/bin/pip install python-pptx
    /tmp/deckenv/bin/python build_mcp_patterns_deck.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# ---- palette (matches the Luminate identity deck) ----
NAVY = RGBColor(0x1A, 0x1A, 0x2E)
BLUE = RGBColor(0x00, 0x96, 0xD6)
AMBER = RGBColor(0xFF, 0xB3, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x2B, 0x2B, 0x3C)
GRAY = RGBColor(0x60, 0x60, 0x70)
RED = RGBColor(0xC6, 0x28, 0x28)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
PALE = RGBColor(0xC9, 0xD3, 0xE0)
BLUE_FILL = RGBColor(0xDA, 0xE8, 0xFC)
GREEN_FILL = RGBColor(0xD5, 0xE8, 0xD4)
YELLOW_FILL = RGBColor(0xFF, 0xF2, 0xCC)
RED_FILL = RGBColor(0xF8, 0xCE, 0xCC)
PURPLE_FILL = RGBColor(0xE1, 0xD5, 0xE7)
LIGHT = RGBColor(0xF4, 0xF5, 0xF7)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height

KICKER = "AGENTIC CONTROL PLANE · MCP SERVER PATTERNS"
FOOT = "MCP Server Patterns — registration, deployment and utilization · ETAB / ATG / ISRA submission · EACPP-1176"


# ---------------------------------------------------------------- helpers ----
def add_box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is not None:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if line is not None:
        shp.line.color.rgb = line
        shp.line.width = Pt(1)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=4):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for item in runs:
        text, size, color, bold = (tuple(item) + (None,) * 4)[:4]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space_after)
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.color.rgb = color if color else DARK
        r.font.bold = bool(bold)
        r.font.name = "Calibri"
    return tb


def bg(slide, color):
    add_box(slide, 0, 0, W, H, fill=color)


def header(slide, title, kicker=KICKER):
    bg(slide, WHITE)
    add_box(slide, 0, 0, W, Inches(1.15), fill=NAVY)
    add_box(slide, 0, Inches(1.15), W, Pt(4), fill=AMBER)
    add_text(slide, Inches(0.55), Inches(0.12), Inches(12), Inches(0.35), [(kicker, 10.5, AMBER, True)])
    add_text(slide, Inches(0.55), Inches(0.42), Inches(12.3), Inches(0.7), [(title, 25, WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)


def footer(slide, n):
    add_text(slide, Inches(0.55), Inches(7.02), Inches(11), Inches(0.35), [(FOOT, 8.5, GRAY)])
    add_text(slide, Inches(12.2), Inches(7.02), Inches(0.8), Inches(0.35), [(str(n), 9, GRAY, True)], align=PP_ALIGN.RIGHT)


def lede(slide, text, y=Inches(1.42), size=14, color=DARK, bold=True):
    add_text(slide, Inches(0.55), y, Inches(12.2), Inches(0.55), [(text, size, color, bold)])


def card(slide, x, y, w, h, title, lines, fill, tcolor=DARK, accent=BLUE, size=10.5):
    add_box(slide, x, y, w, h, fill=fill)
    add_box(slide, x, y, w, Pt(6), fill=accent)
    add_text(slide, x + Inches(0.15), y + Inches(0.12), w - Inches(0.3), Inches(0.4), [(title, 12.5, DARK, True)])
    b = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.58), w - Inches(0.3), h - Inches(0.68))
    tf = b.text_frame
    tf.word_wrap = True
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(3)
        r = p.add_run()
        r.text = "• " + ln
        r.font.size = Pt(size)
        r.font.color.rgb = tcolor
        r.font.name = "Calibri"


def table(slide, cols, rows, col_w, x=Inches(0.55), y=Inches(1.95), size=10.5, row_h=Inches(0.34), emphasis=None):
    """emphasis: dict of row-index (0-based, body rows) -> fill colour."""
    n_rows, n_cols = len(rows) + 1, len(cols)
    tbl = slide.shapes.add_table(n_rows, n_cols, x, y, sum(col_w), row_h * n_rows).table
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = cw
    for j, c in enumerate(cols):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.margin_left = cell.margin_right = Inches(0.06)
        cell.text = c or " "
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(size)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = WHITE
        p.runs[0].font.name = "Calibri"
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            if emphasis and (i - 1) in emphasis:
                cell.fill.fore_color.rgb = emphasis[i - 1]
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else LIGHT
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.text = val or " "
            p = cell.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(size - 1)
            p.runs[0].font.color.rgb = DARK
            p.runs[0].font.name = "Calibri"
    return tbl


def arrow(slide, x, y, w, h=Inches(0.22), color=GRAY, label=None):
    a = add_box(slide, x, y, w, h, fill=color, shape=MSO_SHAPE.RIGHT_ARROW)
    if label:
        add_text(slide, x, y - Inches(0.3), w, Inches(0.28), [(label, 9, GRAY, True)], align=PP_ALIGN.CENTER)
    return a


def chevrons(slide, y, items, height=Inches(1.15), size=11):
    n = len(items)
    total = Inches(12.2)
    gap = Inches(0.08)
    cw = (total - gap * (n - 1)) / n
    for i, (kick, title, sub, fill) in enumerate(items):
        x = Inches(0.55) + (cw + gap) * i
        add_box(slide, x, y, cw, height, fill=fill, shape=MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON)
        add_text(slide, x + Inches(0.28), y + Inches(0.1), cw - Inches(0.5), height - Inches(0.2),
                 [(kick, 8.5, GRAY, True), (title, size + 2, DARK, True), (sub, size - 2, DARK, False)],
                 anchor=MSO_ANCHOR.MIDDLE, space_after=1)


N = 0


def new(title=None, kicker=KICKER):
    global N
    N += 1
    s = prs.slides.add_slide(BLANK)
    if title:
        header(s, title, kicker)
        footer(s, N)
    return s


# ------------------------------------------------------------- 1 · title ----
N += 1
s = prs.slides.add_slide(BLANK)
bg(s, NAVY)
add_box(s, 0, Inches(3.05), W, Pt(4), fill=AMBER)
add_text(s, Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.4),
         [("ARCHITECTURE BRIEF · ETAB / ATG / ISRA SUBMISSION", 13, AMBER, True)])
add_text(s, Inches(0.8), Inches(1.95), Inches(11.7), Inches(1.1),
         [("MCP Server Patterns", 32, WHITE, True)])
add_text(s, Inches(0.8), Inches(3.2), Inches(11.7), Inches(0.6),
         [("How a tool server is built, deployed, registered and consumed on the Agentic Control Plane", 17, PALE)])
add_text(s, Inches(0.8), Inches(4.15), Inches(11.7), Inches(2.1),
         [("Approve one pattern, one conformance profile and one control set — assessed once per server, not once per integration",
           14.5, WHITE, True),
          ("No new product, licence or platform component · built on Luminate, Keycloak, OpenShift / EKS and the approved Jenkins JTE pipeline",
           12.5, PALE),
          ("Conformance profile MSR-1 to MSR-30 · 10 design decisions · 12-item threat model · 25 ISRA controls · 8 residual risks",
           12.5, PALE),
          ("Verified 1 Sept 2026 against Luminate origin/main 10d6ee89, the live ACP dev estate and CSDP/pipeline-libraries",
           11.5, AMBER)])

# --------------------------------------------------------------- 2 · ask ----
s = new("The Ask")
lede(s, "Approve the pattern by which MCP tool servers are onboarded to the Agentic Control Plane, and the control set they are assessed against.", size=15)
card(s, Inches(0.55), Inches(2.15), Inches(3.9), Inches(3.95), "What we ARE asking",
     ["Approve the pattern: an MCP server is reached only through a Luminate gateway",
      "Approve MSR-1 to MSR-30 as the bar any served MCP server must meet",
      "Accept DD-2 / DD-3 — authorization is per server, and the endpoint boundary is the compensating architecture",
      "Accept the 8 residual risks, notably R-1 and R-3",
      "Endorse enabling the Snyk / Checkmarx / SonarQube gates on MCP server repositories"], GREEN_FILL, accent=GREEN)
card(s, Inches(4.65), Inches(2.15), Inches(3.9), Inches(3.95), "What we are NOT asking",
     ["No new product, licence or vendor",
      "No new platform component — everything is already deployed dev to prod",
      "No internet-facing exposure; all MCP traffic stays behind the gateway",
      "Not approving vendor-hosted MCP servers — deliberately deferred (DD-5)",
      "Not asking the consortium to change Luminate as a condition of approval"], RED_FILL, accent=RED)
card(s, Inches(8.75), Inches(2.15), Inches(4.0), Inches(3.95), "Why now",
     ["MCP servers are already live and arriving faster than any stated requirement",
      "Seven business use cases are onboarding and each re-derives the same decisions",
      "Every new tool server is currently a bespoke architecture review and a bespoke ISRA",
      "The current estate posture is measurably weaker than intended — see next slide"], BLUE_FILL)

# -------------------------------------------------------- 3 · background ----
s = new("Background — What Is Driving This")
card(s, Inches(0.55), Inches(1.55), Inches(3.9), Inches(4.6), "Agents need tools; MCP is how they get them",
     ["Model Context Protocol is the emerging open standard for exposing tools, data and prompts to AI agents",
      "It is what a governed agent calls to look up a claim, read a policy or retrieve a document",
      "Already live at Sun Life: FastMCP on OpenShift, in-cluster services on EKS",
      "Bedrock AgentCore runtimes and vendor-hosted endpoints are close behind"], BLUE_FILL)
card(s, Inches(4.65), Inches(1.55), Inches(3.9), Inches(4.6), "Arriving faster than any statement of what one must be",
     ["No requirement set a team can be pointed at before it builds",
      "Consequences are measured, not theoretical — see the estate assessment",
      "Substrate, TLS, identity and build path all differ per server and are written down nowhere",
      "Nothing tells a team that a local stdio server can never be onboarded remotely"], YELLOW_FILL, accent=AMBER)
card(s, Inches(8.75), Inches(1.55), Inches(4.0), Inches(4.6), "A tool server is the workload that most needs a control set",
     ["Invoked by a NON-DETERMINISTIC caller, with arguments the model composed",
      "Executes against a system of record",
      "Its output re-enters the model's reasoning on the next turn",
      "OSFI E-23 inventory and change control; B-13 Principle 15 least privilege, Principle 17 incident response"], RED_FILL, accent=RED)

# ------------------------------------------------------- 4 · current state --
s = new("Current State — What the Estate Actually Looks Like")
lede(s, "Verified 1 September 2026 against the live ACP dev environment. This is the baseline the pattern is being introduced to correct.", size=13.5)
table(s,
      ["MCP server", "Transport", "Identity mode", "Backend endpoint", "Tool records"],
      [["claims-tools", "http", "gateway_identity", "http:// … luminate.svc.cluster.local:8000/mcp", "5"],
       ["underwriting-tools", "http", "gateway_identity", "http:// … luminate.svc.cluster.local:8000/mcp", "5"],
       ["pharmacy-mcp-server", "http", "gateway_identity", "https:// dev-corp-aws-ca1-k8s.sunlifecorp.com / … /mcp", "0"],
       ["claims-tools-bedrock", "http", "gateway_identity", "(deprecated)", "5"]],
      [Inches(2.3), Inches(1.15), Inches(1.95), Inches(5.4), Inches(1.4)],
      y=Inches(2.05), size=11,
      emphasis={2: YELLOW_FILL})
add_text(s, Inches(0.55), Inches(4.05), Inches(12.2), Inches(0.4), [("Four findings that follow directly", 14, DARK, True)])
card(s, Inches(0.55), Inches(4.5), Inches(2.95), Inches(2.05), "No credential reaches any tool server",
     ["All four are gateway_identity — the mode in which the gateway strips the caller's credential",
      "Network reachability is the entire boundary today"], RED_FILL, accent=RED, size=9.5)
card(s, Inches(3.63), Inches(4.5), Inches(2.95), Inches(2.05), "Two are reached over plain HTTP",
     ["Defensible only because of a network property nobody has stated as a control",
      "Stops being defensible on a namespace move"], YELLOW_FILL, accent=AMBER, size=9.5)
card(s, Inches(6.71), Inches(4.5), Inches(2.95), Inches(2.05), "The catalogue is not an inventory",
     ["A live corporate-ingress server carries ZERO tool records",
      "There is no automatic discovery — records are hand-entered"], YELLOW_FILL, accent=AMBER, size=9.5)
card(s, Inches(9.79), Inches(4.5), Inches(2.96), Inches(2.05), "Scanning gates are off estate-wide",
     ["Snyk and Checkmarx enforcement disabled in every ACP repository",
      "Platform library defaults are ENABLED"], RED_FILL, accent=RED, size=9.5)

# ------------------------------------------------------ 5 · solution arch ----
s = new("Solution Overview — The Governed Call")
lede(s, "Whatever the substrate, an MCP server is the same shape: a remote HTTP endpoint reachable only from a Luminate gateway, registered as a governed resource, and granted by access policy.", size=13)

yb = Inches(2.35)
bh = Inches(1.5)
add_box(s, Inches(0.55), yb, Inches(2.5), bh, fill=BLUE_FILL)
add_text(s, Inches(0.7), yb + Inches(0.12), Inches(2.2), bh - Inches(0.24),
         [("CALLING WORKLOAD", 8.5, GRAY, True), ("Agent / Application", 13, DARK, True),
          ("Registered, deployed,\nholds a machine credential", 9.5, DARK)], anchor=MSO_ANCHOR.MIDDLE, space_after=2)

add_box(s, Inches(3.75), Inches(1.95), Inches(5.05), Inches(3.5), fill=LIGHT, line=NAVY)
add_text(s, Inches(3.9), Inches(2.0), Inches(4.75), Inches(0.3), [("ACP · LUMINATE", 8.5, GRAY, True)])
add_box(s, Inches(3.95), Inches(2.35), Inches(4.65), Inches(1.5), fill=BLUE_FILL)
add_text(s, Inches(4.1), Inches(2.47), Inches(4.35), Inches(1.26),
         [("GATEWAY  /mcp/{endpoint}", 8.5, GRAY, True), ("Authenticate · Authorize · Guardrails", 12.5, DARK, True),
          ("Fail-closed. One route per server.\nNo policy cache.", 9.5, DARK)], anchor=MSO_ANCHOR.MIDDLE, space_after=2)
add_box(s, Inches(3.95), Inches(4.0), Inches(4.65), Inches(1.2), fill=PURPLE_FILL)
add_text(s, Inches(4.1), Inches(4.1), Inches(4.35), Inches(1.0),
         [("CONTROL PLANE", 8.5, GRAY, True), ("Portal · Keycloak", 12.5, DARK, True),
          ("Catalogue · access policy · token exchange · audit", 9.5, DARK)], anchor=MSO_ANCHOR.MIDDLE, space_after=2)

add_box(s, Inches(9.5), yb, Inches(3.25), bh, fill=GREEN_FILL)
add_text(s, Inches(9.65), yb + Inches(0.12), Inches(2.95), bh - Inches(0.24),
         [("YOUR TEAM'S PLATFORM", 8.5, GRAY, True), ("MCP server", 13, DARK, True),
          ("Streamable HTTP or SSE\nTools → systems of record", 9.5, DARK)], anchor=MSO_ANCHOR.MIDDLE, space_after=2)

arrow(s, Inches(3.12), yb + Inches(0.62), Inches(0.55), label="Bearer")
arrow(s, Inches(8.85), yb + Inches(0.62), Inches(0.55), label="forward")

add_text(s, Inches(0.55), Inches(5.75), Inches(12.2), Inches(1.1),
         [("Every call is authenticated, authorized centrally and fail-closed, content-scanned for PII and banned content on request and response, written to an append-only audit trail, and attributed to a caller, a server and a specific tool method.", 12.5, DARK, True),
          ("The whole design space is the last hop: what credential — if any — reaches your server, and therefore what your server has to validate.", 12, GRAY)])

# ------------------------------------------------------- 6 · the sequence ----
s = new("The Pattern — Four Steps, Two Owners")
lede(s, "Registration is a team action. Deployment and granting are platform-administrator actions and cannot be delegated today.", size=13.5)
chevrons(s, Inches(2.0), [
    ("STEP 1 · TEAM", "Register", "Catalogue resource:\nkey, transport, project, tools", BLUE_FILL),
    ("STEP 2 · PLATFORM", "Deploy", "Onto a gateway under one\nURL-safe endpoint name", PURPLE_FILL),
    ("STEP 3 · PLATFORM", "Grant", "AccessPolicy from a calling\nagent or application", YELLOW_FILL),
    ("STEP 4", "Serve", "Reachable at\n{gateway}/mcp/{endpoint}", GREEN_FILL),
], height=Inches(1.35))
add_text(s, Inches(0.55), Inches(3.65), Inches(12.2), Inches(0.4), [("What is true on every substrate", 14, DARK, True)])
table(s,
      ["Platform property", "Consequence for the server"],
      [["One route per server; the multiplexed shorthand is gone", "Your server owns its own path segment, addressed at /mcp/{endpoint}"],
       ["Authorization is per server — the tool name is not in the decision", "A grant covers every tool you expose, now and in future"],
       ["The control plane is on the request path, no cache, fail-closed", "A portal outage denies rather than fails open — design around it"],
       ["Configuration reaches gateways by push, not polling", "Registration and withdrawal propagate quickly — but must be measured, not quoted"],
       ["The platform never probes your server", "Health, restart and capacity are entirely the hosting platform's job"],
       ["stdio transport is refused at bundle build, silently", "A local-process server never becomes a served one — re-host behind HTTP first"]],
      [Inches(5.3), Inches(6.9)], y=Inches(4.1), size=11)

# ---------------------------------------------------------- 7 · substrates --
s = new("Hosting Substrates — Four Shapes, One Requirement")
lede(s, "The platform requirement is identical on all four: the gateway must reach your server, and nothing else should be able to. What differs is how each half is achieved.", size=13)
table(s,
      ["", "S1 · OpenShift", "S2 · EKS in-cluster", "S3 · Bedrock AgentCore", "S4 · Vendor-hosted"],
      [["Live today", "Yes — pharmacy-mcp-server", "Yes — claims / underwriting", "Partial", "NO — deferred"],
       ["Typical framework", "FastMCP behind corp ingress", "FastMCP / MCP SDK, ClusterIP", "AgentCore runtime or Gateway", "Vendor's own"],
       ["TLS to the backend", "Required · Sun Life PKI", "Optional — hop stays in the pod network", "Required · public CA", "Required · public CA"],
       ["Reachability control", "NetworkPolicy + route restriction", "NetworkPolicy — the entire boundary", "VPC endpoint / security group", "Vendor-side allowlist"],
       ["Typical identity mode", "delegated_exchange or gateway_identity", "gateway_identity", "token_forward or none", "NONE AVAILABLE"],
       ["Blocker", "None", "None", "Governed-route decision open", "Platform capability not implemented"]],
      [Inches(1.95), Inches(2.75), Inches(2.6), Inches(2.6), Inches(2.4)],
      y=Inches(2.1), size=10)
card(s, Inches(0.55), Inches(4.85), Inches(6.0), Inches(1.75), "The one that has cost real time — S1 TLS",
     ["Corporate ingress leaves are issued by Sun Life Financial Issuing CA3, which no public root store carries",
      "The gateway trust bundle must MERGE, never substitute — substituting trades public TLS (Bedrock) for internal TLS",
      "Symptom when missing: 500 upstream service error, naming neither TLS nor the certificate"], YELLOW_FILL, accent=AMBER, size=9.5)
card(s, Inches(6.75), Inches(4.85), Inches(6.0), Inches(1.75), "Why S4 is deferred rather than merely awkward",
     ["A vendor endpoint is fronted by the vendor's own authorization server, which cannot validate a Luminate token",
      "The two platform modes that would solve it are enum-only and send NO credential at all",
      "There is no safe local workaround — an out-of-band shared secret would be ungoverned"], RED_FILL, accent=RED, size=9.5)

# ------------------------------------------------------------- 8 · identity --
s = new("Identity — What Reaches Your Server")
lede(s, "The identity mode on the catalogue record decides what, if anything, your server receives — and therefore what it must validate. Two of the five modes are not implemented.", size=13)
table(s,
      ["Mode", "What your server receives", "Built", "What you must validate"],
      [["delegated_exchange  (platform default)", "A bearer token obtained by RFC 8693 exchange, minted for the invoking caller and audienced to YOUR deployment", "Yes", "Signature (portal JWKS), issuer, aud = your deployment, expiry"],
       ["token_forward", "The caller's own validated JWT, unchanged", "Yes", "Same issuer the gateway trusts, plus your own claim checks"],
       ["gateway_identity", "Nothing — the gateway strips Authorization and X-API-Key before the backend call", "Yes", "Nothing — you cannot. Network reachability is your only boundary"],
       ["injected_credential", "Intended: a stored per-deployment credential", "NO", "Served as gateway_identity — no credential sent"],
       ["external_exchange", "Intended: a token from your own authorization server", "NO", "Served as gateway_identity — no credential sent"]],
      [Inches(2.5), Inches(4.5), Inches(0.8), Inches(4.4)],
      y=Inches(2.1), size=10,
      emphasis={3: RED_FILL, 4: RED_FILL})
card(s, Inches(0.55), Inches(4.95), Inches(6.0), Inches(1.65), "The trap to state explicitly",
     ["Selecting an unimplemented mode produces NO error and does not disable the server",
      "It produces a server reached with no credential — a silent downgrade in the operator's mind, not in the code",
      "Today the entire estate sits on gateway_identity; MSR-9 makes the choice a recorded decision"], RED_FILL, accent=RED, size=9.5)
card(s, Inches(6.75), Inches(4.95), Inches(6.0), Inches(1.65), "Two safeguards worth crediting",
     ["The downstream token audience names the DEPLOYMENT, not the catalogue entry — a staging credential cannot be spent against production",
      "A delegated target the gateway cannot exchange for is WITHHELD entirely, never downgraded to the gateway's own identity"], GREEN_FILL, accent=GREEN, size=9.5)

# ------------------------------------------------ 9 · inbound eligibility ----
s = new("Identity — Which Caller Credentials Each Endpoint Accepts")
lede(s, "The gateway gates the inbound credential by the endpoint's mode. Every refusal below is an HTTP 403 and is indistinguishable from a policy denial from outside.", size=13)
table(s,
      ["Caller presents →", "token_exchange endpoint", "token_forward endpoint", "gateway_identity endpoint"],
      [["OIDC JWT — machine (client_credentials)", "ACCEPTED", "ACCEPTED", "ACCEPTED"],
       ["OIDC JWT — delegated, carries an actor", "ACCEPTED", "ACCEPTED", "ACCEPTED"],
       ["OIDC JWT — plain user, no actor", "403  not_exchangeable", "ACCEPTED", "ACCEPTED"],
       ["API key — X-API-Key or Bearer lum_…", "403  api_key_not_exchangeable", "403  platform_minted_not_forwardable", "ACCEPTED — key is stripped"],
       ["Delegated token — Bearer lud_at_…", "ACCEPTED", "403  platform_minted_not_forwardable", "ACCEPTED — token is stripped"]],
      [Inches(3.6), Inches(3.0), Inches(3.1), Inches(2.5)],
      y=Inches(2.15), size=10.5)
add_text(s, Inches(0.55), Inches(4.4), Inches(12.2), Inches(0.4), [("Two rules explain the whole table", 14, DARK, True)])
card(s, Inches(0.55), Inches(4.85), Inches(6.0), Inches(1.75), "token_exchange spends the credential",
     ["The caller's credential is the exchange SUBJECT, so only something the exchange can spend qualifies",
      "A platform API key is not an IdP token, so it can never be a subject",
      "Whether that identity may reach the target is the access policy's decision, made when the swapped token is minted"], BLUE_FILL, size=9.5)
card(s, Inches(6.75), Inches(4.85), Inches(6.0), Inches(1.75), "token_forward leaves the platform",
     ["Forward mode hands the caller's Authorization header to a backend the platform does not control",
      "A lum_ key or lud_at_ token is Luminate-issued AND Luminate-validated — your server cannot check either",
      "A replay of one acts as the caller, so only an IdP-signed JWT is forwardable"], GREEN_FILL, accent=GREEN, size=9.5)

# ------------------------------------------------------- 10 · authorization --
s = new("Authorization — The Boundary, Stated Plainly")
add_box(s, Inches(0.55), Inches(1.4), Inches(12.2), Inches(0.72), fill=RED_FILL)
add_text(s, Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.55),
         [("An access policy on an MCP server grants EVERY tool that server exposes — now and in future. The platform authorizes at server granularity, not tool granularity.", 15, DARK, True)],
         anchor=MSO_ANCHOR.MIDDLE)
table(s,
      ["Claim", "Evidence (Luminate origin/main @ 10d6ee89)"],
      [["No tool target type exists", "AccessPolicyTargetType = mcp_server, agent, model, location, environment. None is a tool"],
       ["allowed_tool_ids is inert", "The column exists and is serialized; NO runtime consumer in the gateway, the policy engine, or any Rego package"],
       ["The tool name is not in the decision", "The authorization request carries the endpoint name; the JSON-RPC method is parsed AFTER the decision, for telemetry"],
       ["MCPTool.access_level is documentation", "admin / read / write is a catalogue label — nothing refuses a write tool to a read-only grant"]],
      [Inches(3.5), Inches(8.7)], y=Inches(2.35), size=10.5)
add_text(s, Inches(0.55), Inches(4.05), Inches(12.2), Inches(0.4),
         [("The compensating architecture — this is the substance of DD-3", 14, DARK, True)])
card(s, Inches(0.55), Inches(4.5), Inches(6.0), Inches(2.1), "MSR-15 · One server per trust boundary  (preferred)",
     ["Design the endpoint the way you would design a database role",
      "Split on: read vs write · classification tier · system of record · anything you would withdraw independently in an incident",
      "Costs one catalogue entry and one deployment row; buys a real platform-enforced grant boundary",
      "Reversible in a way a shared endpoint is not — narrowing later is a migration"], GREEN_FILL, accent=GREEN, size=9.5)
card(s, Inches(6.75), Inches(4.5), Inches(6.0), Inches(2.1), "MSR-16 · Server-side tool authorization  (fallback)",
     ["Where the split cannot be made, the server authorizes per tool from the identity it receives",
      "Only possible in delegated_exchange or token_forward — a gateway_identity server has no identity to authorize",
      "That is the strongest practical argument against gateway_identity for anything with a write tool",
      "The control then sits on the server and is assessed there, not on ACP"], YELLOW_FILL, accent=AMBER, size=9.5)

# --------------------------------------------------------- 11 · controls -----
s = new("The ISRA Control Set — 25 Controls, Each With Evidence")
lede(s, "Every control has a type, an enforcement point, retrievable evidence and an owner. A control that cannot be evidenced is not a control.", size=13.5)
table(s,
      ["Group", "Controls", "Enforcement point", "Evidence an assessor retrieves"],
      [["Authentication & credential eligibility", "C-1, C-2", "Gateway (JWKS / portal)", "401 and 403 with the specific refusal reason on a negative test"],
       ["Authorization", "C-3, C-4, C-5", "Portal access decision; server-side or split endpoints", "The policy record; a per-tool negative test"],
       ["Network & transport", "C-6, C-7", "NetworkPolicy / SG / private endpoint; TLS", "Negative test from a non-gateway workload; CA count in the gateway pod"],
       ["Credential containment", "C-8, C-9, C-10", "Gateway refusal paths; portal token exchange", "403 platform_minted_not_forwardable; refusal of a foreign-deployment token"],
       ["Content control", "C-11, C-12", "Guardrails on mcp_server; server-side output bound", "Guardrail binding; a positive detection test"],
       ["Supply chain", "C-13 … C-17", "Checkmarx, Snyk, SonarQube, registry, Vault", "Scan id, SBOM, quality gate, digest match, secret source"],
       ["Inventory & change", "C-18, C-19", "Catalogue vs live tools/list; change process", "Release-time diff; change record"],
       ["Audit & attribution", "C-20, C-21, C-22", "Append-only audit trail; tracing headers", "Authorize + access event pair per call; a trace naming caller, server and method"],
       ["Withdrawal & governance", "C-23, C-24, C-25", "Status / policy / governance suspension", "MEASURED propagation time; recorded suspension preview; state and reason"]],
      [Inches(3.3), Inches(1.5), Inches(3.1), Inches(4.3)],
      y=Inches(2.0), size=10)

# ------------------------------------------------------- 12 · supply chain ---
s = new("Build & Supply Chain — And Why a Green Pipeline Is Not Evidence")
lede(s, "MCP servers build on the approved Jenkins JTE path. The library defaults are already correct; what has drifted is how the ACP estate configures them.", size=13)
table(s,
      ["Gate", "JTE step", "Library default", "ACP estate today", "Required for an MCP server"],
      [["SAST — Checkmarx", "code_analysis()", "enforce = TRUE, branches = [develop]", "enforce = false, everywhere", "enforce = true + branches set explicitly"],
       ["SCA — Snyk", "sca_scan()", "run = TRUE, enforce = TRUE, severity = high", "run = true, enforce = false", "enforce = true, SBOM retained, APM tag set"],
       ["Static analysis — SonarQube", "static_code_analysis()", "gate available", "varies", "gate enforced; exceptions owned and dated"],
       ["Image", "quay / ecr build", "pipeline-built image", "pipeline-built", "immutable digest, non-root, never :latest"]],
      [Inches(2.5), Inches(2.0), Inches(3.0), Inches(2.3), Inches(2.4)],
      y=Inches(2.05), size=10)
add_box(s, Inches(0.55), Inches(4.15), Inches(12.2), Inches(1.05), fill=RED_FILL)
add_text(s, Inches(0.8), Inches(4.25), Inches(11.7), Inches(0.9),
         [("The Checkmarx step does not run a scan.", 14, DARK, True),
          ("It resolves the repository's latest MERGED PULL REQUEST, reads the scan Checkmarx already performed for it, and reports the verdict. With no merged PR it logs “New repository PR does not exist. Checkmarx scan is skipped.” and continues. The default branch pattern is [develop], so a repository on main matches nothing and the whole stage is skipped.",
           11.5, DARK, False)])
add_text(s, Inches(0.55), Inches(5.4), Inches(12.2), Inches(1.2),
         [("Three ways to pass without being scanned: no merged PR · branch mismatch · gate disabled.", 12.5, DARK, True),
          ("MSR-20 therefore requires the scan id and gate evaluation on the build — not the stage colour. This is design decision DD-8, and it is the reason the supply-chain block of the control set is written around retrievable artefacts rather than pipeline status.",
           12, GRAY)])

# --------------------------------------------------------- 13 · threats ------
s = new("Threat Model — What an MCP Server Changes")
lede(s, "An MCP server is not an ordinary internal API. It is invoked by a non-deterministic caller, with arguments that caller composed, and its output re-enters that caller's reasoning.", size=13)
table(s,
      ["#", "Threat", "Control"],
      [["T1", "Confused deputy — an agent induced to call a tool it is entitled to, for a purpose it is not", "DD-3 split · MSR-16 server-side authorization · MSR-27 classification"],
       ["T2", "Excessive agency — a tool added later is covered by an existing grant, with no approval", "MSR-7 change control · MSR-6 catalogue diff at release"],
       ["T3", "Prompt injection via tool output — returned content instructs the model", "MSR-18 bounded non-instructional output · response guardrails · DD-10"],
       ["T4", "Tool poisoning — a tool description written to steer model behaviour", "MSR-8 review of names and descriptions"],
       ["T5", "Path bypass — a workload calls the backend directly, skipping the gateway", "MSR-10 negative test · DD-1. A bypass emits NO audit event, so absence is the signal"],
       ["T6", "Credential leakage — a platform-minted credential forwarded to an uncontrolled backend", "Enforced in the gateway; verified by negative test"],
       ["T7", "Cross-environment replay — a staging credential spent against production", "Token audience is scoped to the deployment; MSR-12 requires the server to check it"],
       ["T8", "Silent unauthenticated serving — a delegated endpoint degraded to gateway identity", "The gateway WITHHOLDS rather than downgrades"],
       ["T9", "Supply-chain compromise in a dependency or image", "MSR-19 to MSR-23, evidenced per DD-8"],
       ["T10", "Data exfiltration through tool arguments", "Request-direction PII guardrails · MSR-27 · MSR-28"],
       ["T11", "Inventory drift — the assessed tool set is not the served tool set", "MSR-6 · DD-6"],
       ["T12", "Unbounded blast radius on withdrawal", "Suspension preview names deployments and policies before commit"]],
      [Inches(0.55), Inches(6.15), Inches(5.5)],
      y=Inches(2.05), size=9.5, row_h=Inches(0.3))

# ------------------------------------------------------- 14 · decisions ------
s = new("Design Decisions")
table(s,
      ["#", "Decision", "Alternative rejected"],
      [["DD-1", "The gateway is the only path to a tool", "Publishing the server for direct use — creates an ungoverned path"],
       ["DD-2", "The server, not the tool, is the unit of authorization", "Relying on allowed_tool_ids or access_level — both inert at runtime"],
       ["DD-3", "One server per trust boundary — split read from write", "One large server with server-side authorization only — the control moves off the platform"],
       ["DD-4", "delegated_exchange is the target mode; gateway_identity needs a recorded rationale", "Leaving the estate default, which is where all four dev servers sit"],
       ["DD-5", "Third-party-fronted servers are not onboarded yet", "Injecting a shared static credential out-of-band"],
       ["DD-6", "Tool records are a release-time obligation", "Treating the catalogue as authoritative — it would make the ISRA inventory a fiction"],
       ["DD-7", "Scanning gates ship enabled on MCP server repositories", "Following the existing ACP repositories' configuration"],
       ["DD-8", "Evidence, not stage colour — a control is met when its artefact is retrievable", "Accepting build status as evidence"],
       ["DD-9", "Fail-closed availability is accepted — no local policy cache", "A cached allow is an unrevoked allow"],
       ["DD-10", "Tool output is untrusted input", "Trusting tool output because the tool is internal"]],
      [Inches(0.75), Inches(5.5), Inches(5.95)],
      y=Inches(1.55), size=10.5, row_h=Inches(0.33),
      emphasis={1: YELLOW_FILL, 2: YELLOW_FILL})

# ----------------------------------------------------------- 15 · residual ---
s = new("Residual Risks — For Explicit Acceptance")
lede(s, "None of these is mitigated by a control in the set. An assessment that does not name them is incomplete.", size=13.5)
table(s,
      ["#", "Residual risk", "Why it remains", "Compensating position"],
      [["R-1", "A grant covers every tool on the server, including tools added later", "Tool-granular authorization is not implemented in the platform", "DD-3 split · MSR-16 · MSR-7 change control. Consortium ask raised"],
       ["R-2", "The tool inventory is hand-maintained", "No discovery on origin/main", "MSR-6 release-time diff. Consortium ask raised"],
       ["R-3", "Prompt injection through tool output cannot be eliminated", "A property of putting model-readable content in a model's context", "Response guardrails, bounded output, least privilege on what the tool can do"],
       ["R-4", "The platform never probes server health", "Not implemented", "Hosting-platform probes + alerting on gateway 5xx per endpoint"],
       ["R-5", "Availability is bounded by the control plane", "Deliberate — no policy cache, so a portal outage denies", "Accepted per DD-9; gateway and portal redundancy"],
       ["R-6", "No per-server call quota or spend budget", "Quota dimensions stop at requests and tokens; the gateway consumes none", "Server-side rate limiting where a tool needs it"],
       ["R-7", "Third-party-fronted servers cannot be onboarded with a credential", "The two relevant modes are unimplemented", "DD-5 — not onboarded. Consortium ask raised"],
       ["R-8", "The governance axis is inert", "Rulesets deployed, zero applicability rules", "Tracked separately; not presented as an operating control yet"]],
      [Inches(0.7), Inches(3.4), Inches(3.6), Inches(4.5)],
      y=Inches(2.0), size=9.5, row_h=Inches(0.33),
      emphasis={0: YELLOW_FILL, 2: YELLOW_FILL})

# ------------------------------------------------------------- 16 · gaps -----
s = new("Gaps — And Who Owns Each")
lede(s, "Three of the ten are entirely ours. They are also the three that most directly weaken an assurance submission, and they need no consortium change.", size=13.5)
card(s, Inches(0.55), Inches(2.0), Inches(6.0), Inches(4.55), "Consortium — Luminate platform changes",
     ["G-1  Tool-granular authorization does not exist  (HIGH — compensated architecturally)",
      "G-2  No automatic tool discovery  (HIGH — compensated by process)",
      "G-3  injected_credential / external_exchange unimplemented  (HIGH — no workaround)",
      "G-5  No MCP server health probing  (Medium)",
      "G-8  Quotas modelled but not enforced at the gateway  (Medium)",
      "",
      "Each already has a stated compensating control, so none of these blocks approval — they are raised in parallel, not sequenced ahead of delivery."],
     BLUE_FILL, size=10.5)
card(s, Inches(6.75), Inches(2.0), Inches(6.0), Inches(4.55), "Sun Life — ours to close",
     ["G-6  Scanning gates disabled estate-wide  (HIGH)",
      "G-7  The Checkmarx gate passes without scanning  (HIGH)",
      "G-9  Governance rulesets deployed but inert — zero applicability rules  (Medium)",
      "G-4  Kill-switch propagation has never been measured  (shared with consortium)",
      "G-10  The AgentCore governed-route decision is open  (Medium)",
      "",
      "G-6 and G-7 are on the critical path into this submission: an ISRA cannot claim SAST and SCA coverage that the pipelines do not enforce."],
     RED_FILL, accent=RED, size=10.5)

# --------------------------------------------------------- 17 · delivery -----
s = new("Delivery Plan")
lede(s, "Five workstreams. W1 and W3 depend on nothing and start together; W3 is the critical path into the assurance work.", size=13.5)
chevrons(s, Inches(2.0), [
    ("W1", "Publish", "Profile, decision tree,\nsubstrate annex, reference server", BLUE_FILL),
    ("W2", "Fix the estate", "Assess the four servers,\nrecord modes, evidence controls", YELLOW_FILL),
    ("W3", "Supply chain", "Gates on, branches set,\nreal Checkmarx scans", RED_FILL),
    ("W4", "Assurance", "ETAB submission,\nISRA control set", GREEN_FILL),
    ("W5", "Asks", "Corrections and\nconsortium requests", PURPLE_FILL),
], height=Inches(1.3), size=12)
add_text(s, Inches(0.55), Inches(3.65), Inches(12.2), Inches(0.4), [("Sequencing and the critical path", 14, DARK, True)])
table(s,
      ["Workstream", "First tasks", "Depends on", "Note"],
      [["W1 · Publish the pattern", "T1 profile · T2 substrate annex · T6 reference MCP server", "Nothing", "Start immediately — unblocks every onboarding team"],
       ["W2 · Bring the estate up", "T8 assess four servers · T9 record identity modes · T10 evidence network control", "W1", "T13 measures kill-switch propagation and can start now"],
       ["W3 · Close the supply-chain gaps", "T15 gates on · T16 branches_to_scan · T17 real Checkmarx scans", "Nothing", "CRITICAL PATH — no external blocker, and W4 cannot claim coverage without it"],
       ["W4 · Assurance", "T21 ETAB submission · T22 ISRA control set · T23 residual-risk acceptance", "W1, W3", "This deck is T21"],
       ["W5 · Corrections and asks", "T25 capability-map correction · T27-T32 consortium asks", "Nothing", "Long-lead; raised in parallel, blocks nothing"]],
      [Inches(2.9), Inches(4.0), Inches(1.4), Inches(3.9)],
      y=Inches(4.1), size=10)

# -------------------------------------------------------------- 18 · close ---
N += 1
s = prs.slides.add_slide(BLANK)
bg(s, NAVY)
add_box(s, 0, Inches(1.15), W, Pt(4), fill=AMBER)
add_text(s, Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.6), [("WHAT WE ARE ASKING ETAB TO APPROVE", 15, AMBER, True)])
items = [
    ("1", "The pattern", "MCP servers are consumed only through a Luminate gateway, on the substrates in this brief, with vendor-hosted deferred."),
    ("2", "The conformance profile", "MSR-1 to MSR-30 as the bar for any MCP server that will be served, each with a stated verification method."),
    ("3", "The design decisions", "In particular DD-2 and DD-3 — conceding that authorization is server-granular, and making the endpoint boundary the compensating architecture."),
    ("4", "The residual risks", "Eight named risks accepted, with the consortium asks as the path to closing R-1, R-2, R-4 and R-7."),
]
y = Inches(1.75)
for num, title, sub in items:
    add_box(s, Inches(0.8), y, Inches(0.62), Inches(0.62), fill=AMBER)
    add_text(s, Inches(0.8), y + Inches(0.07), Inches(0.62), Inches(0.5), [(num, 19, NAVY, True)], align=PP_ALIGN.CENTER)
    add_text(s, Inches(1.65), y - Inches(0.02), Inches(10.9), Inches(0.85),
             [(title, 16, WHITE, True), (sub, 12, PALE)], space_after=2)
    y += Inches(1.12)
add_box(s, Inches(0.8), Inches(6.35), Inches(11.7), Pt(2), fill=GRAY)
add_text(s, Inches(0.8), Inches(6.55), Inches(11.7), Inches(0.6),
         [("Full spec, D0-D3: acp-product-specs / specs/pattern/mcp-server-patterns · Confluence T1KACP “MCP Server Patterns” · Jira EACPP-1176", 11, PALE)])

out = Path(__file__).resolve().parent / "MCP-Server-Patterns-ACP.pptx"
prs.save(out)
print(f"Wrote {out}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
