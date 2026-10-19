#!/usr/bin/env python3
"""Generate the Agent Patterns architecture brief for ETAB / ATG / ISRA.

Content is derived from specs/pattern/agent-patterns/ (D0-D3). Every factual claim on these
slides is verified in the spec against luminate origin/main @ 1c4a0003, the live SLF
dev and prod estates, luminate-sunlife-deploy @ e7c9750 and acp-harness-sdk @ 4634fe2,
all read 2026-09-08.

Visual language deliberately matches specs/pattern/mcp-server-patterns/references/
build_mcp_patterns_deck.py so the two pattern submissions read as one series.

python-pptx is not in the repo's toolchain, so install it into a throwaway
environment rather than adding ~10 MB of packages to a tracked one::

    python3 -m venv /tmp/deckenv && /tmp/deckenv/bin/pip install python-pptx
    /tmp/deckenv/bin/python build_agent_patterns_deck.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# ---- palette (matches the MCP pattern and Luminate identity decks) ----
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

KICKER = "AGENTIC CONTROL PLANE · AGENT PATTERNS"
FOOT = "Agent Patterns — building, hosting, registering and invoking an agent · ETAB / ATG / ISRA submission · EACPP-1290"


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


# ------------------------------------------------------------------ slides ----

# 1 — title
s = new()
bg(s, NAVY)
add_box(s, 0, Inches(3.05), W, Pt(5), fill=AMBER)
add_text(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(0.4), [("AGENTIC CONTROL PLANE", 13, AMBER, True)])
add_text(s, Inches(0.9), Inches(1.95), Inches(11.5), Inches(1.1),
         [("Agent Patterns", 44, WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.9), Inches(3.3), Inches(11.5), Inches(0.6),
         [("Building, hosting, registering and invoking an agent on ACP / Luminate", 17, PALE, False)])
add_text(s, Inches(0.9), Inches(4.15), Inches(11.5), Inches(1.6),
         [("An MCP server is only ever called. An agent is both a caller and a callee —", 13, PALE, False),
          ("and those are two registrations with two requirement sets.", 13, WHITE, True)], space_after=6)
add_text(s, Inches(0.9), Inches(6.2), Inches(11.5), Inches(0.9),
         [("ETAB / ATG / ISRA submission  ·  EACPP-1290  ·  Sun Life ACP Product Team", 11, PALE, False),
          ("Verified against luminate origin/main 1c4a0003 and the live SLF dev + prod estates, 2026-09-08", 9.5, GRAY, False)],
         space_after=3)

# 2 — the distinction
s = new("Egress and ingress are two registrations")
lede(s, "Registering an agent and granting it a model makes it a governed caller. It does not make it callable.")
card(s, Inches(0.55), Inches(2.1), Inches(6.05), Inches(2.5), "EGRESS — the agent as caller",
     ["Agent record + Deployment + credential",
      "AccessPolicy: source_agent → model | mcp_server | agent",
      "Calls /llm, /mcp/{ep}, /a2a/{ep}",
      "Production-proven; the majority of the estate"],
     BLUE_FILL, accent=BLUE)
card(s, Inches(6.85), Inches(2.1), Inches(6.05), Inches(2.5), "INGRESS — the agent as callee",
     ["Everything above, PLUS an AgentDeployment",
      "endpoint_name + backend_endpoint — this is what emits a route",
      "AccessPolicy: source → target_agent",
      "Served at /a2a/{endpoint_name}"],
     GREEN_FILL, accent=GREEN)
add_box(s, Inches(0.55), Inches(4.9), Inches(12.35), Inches(1.75), fill=RED_FILL)
add_box(s, Inches(0.55), Inches(4.9), Inches(12.35), Pt(6), fill=RED)
add_text(s, Inches(0.85), Inches(5.1), Inches(11.8), Inches(1.4),
         [("What that costs today, in the live dev estate", 13, DARK, True),
          ("8 of 10 registered agents have no A2A endpoint and are not callable by anything — with no record that this was a decision.", 11.5, DARK, False),
          ("One of them, claims-adjudicator, is already the target of an ACTIVE access policy. The call authorizes, then fails at the proxy hop. Nothing reconciles the two.", 11.5, RED, True)],
         space_after=5)

# 3 — architecture
s = new("The architecture, as submitted")
lede(s, "No agent reaches anything, and is reached by nothing, except through a gateway that authenticates, authorizes and records the call.")
y = Inches(2.25)
card(s, Inches(0.55), y, Inches(2.7), Inches(2.2), "Agent A", ["Any substrate", "Registered · deployed", "Holds a machine credential"], BLUE_FILL, accent=BLUE)
card(s, Inches(3.55), y, Inches(3.1), Inches(2.2), "Luminate gateway", ["authn · authz · guardrails", "/llm · /mcp/{ep} · /a2a/{ep}", "RFC 8693 exchange on A2A"], YELLOW_FILL, accent=AMBER)
card(s, Inches(6.95), y, Inches(2.8), Inches(2.2), "Control plane", ["Catalogue · access policy", "CheckAccess — fail closed", "Audit · usage ledger"], PURPLE_FILL, accent=BLUE)
card(s, Inches(10.05), y, Inches(2.85), Inches(2.2), "Targets", ["Model · MCP server", "Agent B (A2A JSON-RPC)", "Systems of record"], GREEN_FILL, accent=GREEN)
arrow(s, Inches(3.28), Inches(3.15), Inches(0.24))
arrow(s, Inches(6.68), Inches(3.15), Inches(0.24))
arrow(s, Inches(9.78), Inches(3.15), Inches(0.24))
add_box(s, Inches(0.55), Inches(4.75), Inches(12.35), Inches(1.9), fill=LIGHT)
add_text(s, Inches(0.85), Inches(4.92), Inches(11.8), Inches(1.6),
         [("What the architecture deliberately does NOT assert", 13, DARK, True),
          ("Content is scanned on the A2A lane  —  no guardrail can bind to an agent as a callee", 11.5, RED, False),
          ("Deactivating an agent contains it  —  it stops ingress only", 11.5, RED, False),
          ("governance_state gates anything  —  zero runtime consumers, in the platform's own words", 11.5, RED, False),
          ("Call volume or spend is bounded  —  the gateway holds no quota references at all", 11.5, RED, False)],
         space_after=4)

# 4 — pick your shape
s = new("Pick your shape — four questions, in order")
chevrons(s, Inches(1.95), [
    ("QUESTION 1", "Callable?", "Will another agent invoke yours?\nIf not — egress only. Record it.", BLUE_FILL),
    ("QUESTION 2", "A2A capable?", "Remote HTTP service speaking\nA2A JSON-RPC at a stable URL?", YELLOW_FILL),
    ("QUESTION 3", "Substrate?", "OpenShift · EKS in-cluster ·\nBedrock AgentCore · Lambda", GREEN_FILL),
    ("QUESTION 4", "Exchange?", "Can the gateway run the\non-behalf-of exchange?", PURPLE_FILL),
], height=Inches(1.5))
table(s, ["", "S1 OpenShift", "S2 EKS in-cluster", "S3 Bedrock AgentCore", "S4 AWS Lambda"], [
    ["Ingress capable", "Unproven", "Yes", "Yes (dev)", "Needs a stable URL"],
    ["TLS on the hop", "SLF PKI — merged bundle", "usually none (plain HTTP)", "public roots", "public roots"],
    ["ASR-5 control", "NetworkPolicy + route", "NetworkPolicy", "resource + VPCe policy", "private API GW"],
    ["Inbound authorizer", "the agent's own", "the agent's own", "custom JWT authorizer", "the function's own"],
    ["Cold-start token risk", "none", "none", "low", "HIGH — rate-limited mint"],
    ["Live example", "—", "policy-assistant", "fdes-pharmacy-agent", "—"],
], [Inches(2.0), Inches(2.6), Inches(2.5), Inches(2.7), Inches(2.4)], y=Inches(3.85), row_h=Inches(0.36), size=10)
add_text(s, Inches(0.55), Inches(6.55), Inches(12.2), Inches(0.4),
         [("Three further platforms carry a recorded verdict: Microsoft Copilot and AWS Quick Suite agents are out of scope as governed agents (no interposition point); developer / laptop agents are permanently out.", 10.5, GRAY, False)])

# 5 — identity
s = new("Ingress identity: delegated, or degraded")
lede(s, "There is no agent identity mode. Every routable agent deployment is a delegated target — the only alternative is a degrade that sends nothing.")
card(s, Inches(0.55), Inches(2.15), Inches(3.95), Inches(2.5), "DELEGATED — conformant",
     ["backendAuth.oauthTokenExchange on the route",
      "aud = agent-{agentUUID}-{deploymentUUID}",
      "Deployment-scoped, so a staging token cannot be spent in prod",
      "The callee learns who called"],
     GREEN_FILL, accent=GREEN)
card(s, Inches(4.75), Inches(2.15), Inches(3.95), Inches(2.5), "WITHHELD — safe refusal",
     ["The gateway cannot run the exchange",
      "Route dropped from the config",
      "503 endpoint_withheld at the gate",
      "RFC 9728 discovery 404s — the tell"],
     YELLOW_FILL, accent=AMBER)
card(s, Inches(8.95), Inches(2.15), Inches(3.95), Inches(2.5), "DEGRADED — not conformant",
     ["No backendAuth on the route",
      "The caller's own credential is forwarded, unchanged",
      "Safe only if the upstream is the platform's own",
      "All four PROD routes are here today"],
     RED_FILL, accent=RED)
add_box(s, Inches(0.55), Inches(4.95), Inches(12.35), Inches(1.65), fill=LIGHT)
add_text(s, Inches(0.85), Inches(5.12), Inches(11.8), Inches(1.35),
         [("Dev and prod disagree, and the difference is 49 commits", 13, DARK, True),
          ("DEV   inlinePolicies: [a2a, backendTLS, backendAuth.oauthTokenExchange → aud agent-01a01b8b-…]     ← conformant", 11, GREEN, True),
          ("PROD  inlinePolicies: [a2a, backendTLS]                                                            ← no credential reaches the agent", 11, RED, True),
          ("Not exploitable today only because prod holds ZERO target_type=agent policies. The control holding the line is the absence of a grant.", 11, DARK, False)],
         space_after=4)

# 6 — the kill switch
s = new("The stop control is asymmetric — and it runs the wrong way")
lede(s, "Setting an agent inactive stops other agents calling it. It does not stop it calling anything.")
card(s, Inches(0.55), Inches(2.2), Inches(6.05), Inches(2.15), "INGRESS — stopped",
     ["authz.rego: allowed_agents requires agent.status == \"active\"",
      "_collect_agents() selects ACTIVE only",
      "An inactive agent drops out of the fact bundle",
      "Every A2A call to it denies"],
     GREEN_FILL, accent=GREEN)
card(s, Inches(6.85), Inches(2.2), Inches(6.05), Inches(2.15), "EGRESS — unaffected",
     ["_source_matches(policy) if { policy.source_id == input.jwt.sub }",
      "One line. It never consults input.agents",
      "_collect_policies filters on policy status, not source status",
      "verify_api_key never reads owner_agent.status"],
     RED_FILL, accent=RED)
add_box(s, Inches(0.55), Inches(4.65), Inches(12.35), Inches(1.95), fill=YELLOW_FILL)
add_box(s, Inches(0.55), Inches(4.65), Inches(12.35), Pt(6), fill=AMBER)
add_text(s, Inches(0.85), Inches(4.85), Inches(11.8), Inches(1.65),
         [("What the runbook must actually say (ASR-32 · DD-7)", 13, DARK, True),
          ("To stop EGRESS:  1 · revoke the OAuthCredential   2 · revoke or expire any APIKey   3 · revoke the source AccessPolicy rows", 11.5, DARK, True),
          ("Revocation has a tail — a token minted a second before revocation lives to expiry. Revoking the POLICIES closes that, because the policy is consulted on every request.", 11, DARK, False),
          ("governance_state = suspended records, previews the cascade, audits it — and refuses nothing. \"The state is real and the denial is not.\" — the platform's own docstring.", 11, RED, False)],
         space_after=4)

# 7 — guardrails
s = new("Content control on the A2A lane is caller-side only")
lede(s, "GuardrailTargetType has an AGENT member. It covers the agent as CALLER. There is no way to bind a guardrail to an agent as a callee.")
table(s, ["Attachment scope", "Fires on", "Available for agents?"], [
    ["organization / project", "anything under it", "Yes"],
    ["api_key", "the credential presented", "Yes"],
    ["agent", "requests MADE BY that agent", "Yes — source side"],
    ["application / mcp_server", "requests made by that entity", "Yes"],
    ["target_model", "every request TO that model", "Yes"],
    ["target_mcp_server", "every request TO that MCP server", "Yes"],
    ["target_agent", "every request TO that agent", "DOES NOT EXIST"],
], [Inches(3.4), Inches(5.2), Inches(3.6)], y=Inches(2.2), row_h=Inches(0.36),
   emphasis={6: RED_FILL})
add_box(s, Inches(0.55), Inches(5.05), Inches(12.35), Inches(1.55), fill=LIGHT)
add_text(s, Inches(0.85), Inches(5.22), Inches(11.8), Inches(1.3),
         [("Proved twice over, and the platform states the reason itself", 13, DARK, True),
          ("grep -rn \"target_agent\" backend/app/guardrails/  →  0", 11, RED, True),
          ("_TARGET_SCOPED_FLOWS = frozenset({\"model\", \"mcp_server\"})   \"authz.rego has a model branch and an mcp_server branch and no agent branch\"", 11, DARK, False),
          ("Interim (ASR-22): every caller granted the endpoint carries a source-scoped guardrail, and the callee records the requirement. Guardrail attachments in SLF dev today: ZERO.", 11, DARK, True)],
         space_after=4)

# 8 — conformance profile
s = new("The conformance profile — ASR-1 to ASR-34")
lede(s, "Every requirement carries a direction, an enforcement point and a verification method. A requirement that cannot be evidenced is not a requirement.")
table(s, ["Group", "IDs", "What it covers", "The one that catches people"], [
    ["A · Direction and addressability", "ASR-1 – 7", "declare direction; A2A JSON-RPC; endpoint hygiene; reachability", "ASR-6 — the registered query string is DISCARDED"],
    ["B · Catalogue and lifecycle", "ASR-8 – 12", "vocabulary; one runtime per env; governance; no grant without a route", "ASR-11 — a grant can exist with no route"],
    ["C · Identity and credentials", "ASR-13 – 19", "served only with the exchange; validate the deployment audience", "ASR-17 — an API key is refused on /a2a"],
    ["D · Authorization and content", "ASR-20 – 24", "least privilege; untrusted input; caller-side guardrails; bound yourself", "ASR-22 — you cannot scan your own ingress"],
    ["E · Build and supply chain", "ASR-25 – 28", "JTE path; Checkmarx; Snyk; SonarQube; image provenance", "ASR-26 — a green stage is not a scan"],
    ["F · Runtime and secrets", "ASR-29 – 30", "non-root; requests AND limits incl. init; Vault / Secrets Manager", "ASR-29 — Gatekeeper denies silently"],
    ["G · Observability and lifecycle", "ASR-31 – 34", "delegated-cost decision; the stop path; run correlation; classification", "ASR-32 — deactivation is not containment"],
], [Inches(3.3), Inches(1.25), Inches(4.3), Inches(3.55)], y=Inches(2.2), row_h=Inches(0.46), size=10)
add_text(s, Inches(0.55), Inches(6.05), Inches(12.2), Inches(0.7),
         [("Numbered ASR- so it can be cited alongside the MCP profile's MSR-1 to MSR-30 without collision. 35 ISRA controls (C-1 to C-35), 12 design decisions, a 16-item threat model and 11 residual risks are in the D2 assurance page.", 11, GRAY, False)])

# 9 — gaps
s = new("Gaps, split by owner")
lede(s, "Three of the four high-severity gaps are consortium-owned, and all three are the same shape: a governance surface that is visible, modelled, and does not act.")
table(s, ["#", "Gap", "Owner", "Sev", "Interim"], [
    ["G-1", "Kill switch does not stop egress", "Consortium", "High", "Revoke credential + policies; drill it"],
    ["G-2", "No guardrail can target an agent", "Consortium", "High", "Caller-side guardrails, recorded on the callee"],
    ["G-3", "Governance state enforces nothing", "Consortium", "High", "Record only; declared as residual risk R-3"],
    ["G-4", "No reachability or health probe", "Consortium", "Med", "Post-registration call; alert on gateway 5xx"],
    ["G-5", "No agent card through the gateway", "Consortium", "Med", "Catalogue record is the inventory"],
    ["G-6", "No GenAI operation name on the lane", "Consortium", "Med", "Forward the delegated token for cost"],
    ["G-7", "Registered query string discarded", "Consortium", "Low", "Use the default qualifier"],
    ["G-9", "Prod predates the A2A exchange", "Sun Life", "High", "No prod A2A grant until the uplift ships"],
    ["G-10", "Harness SDK cannot reach the lane", "Sun Life", "High", "— (four defects, four tests)"],
    ["G-11", "Estate does not match its own grants", "Sun Life", "Med", "Standing reconciliation queries"],
    ["G-12", "Scanning gates disabled estate-wide", "Sun Life", "Med", "— (enable and evidence)"],
    ["G-13", "OpenShift and Lambda unexercised", "Sun Life", "Med", "— (prove one agent on each)"],
], [Inches(0.7), Inches(4.0), Inches(1.5), Inches(0.8), Inches(5.2)], y=Inches(2.2), row_h=Inches(0.33), size=10,
   emphasis={0: RED_FILL, 1: RED_FILL, 2: RED_FILL, 7: RED_FILL, 8: RED_FILL})

# 10 — what ETAB is asked to approve
s = new("What ETAB is being asked to approve")
lede(s, "Five things, and two of them are concessions rather than claims.")
card(s, Inches(0.55), Inches(2.15), Inches(6.05), Inches(2.15), "The pattern and the direction model",
     ["An agent reaches, and is reached, only through a gateway",
      "Four substrates + three recorded out-of-scope verdicts",
      "Egress and ingress are two registrations (DD-1) — the change that stops agents being registered and unreachable"],
     BLUE_FILL, accent=BLUE)
card(s, Inches(6.85), Inches(2.15), Inches(6.05), Inches(2.15), "The conformance profile",
     ["ASR-1 to ASR-34, each with an enforcement point and a verification method",
      "35 ISRA controls, evidenced once per substrate and reused",
      "A control is met when its artefact is retrievable — not when a stage is green"],
     GREEN_FILL, accent=GREEN)
add_box(s, Inches(0.55), Inches(4.6), Inches(12.35), Inches(2.0), fill=YELLOW_FILL)
add_box(s, Inches(0.55), Inches(4.6), Inches(12.35), Pt(6), fill=AMBER)
add_text(s, Inches(0.85), Inches(4.82), Inches(11.8), Inches(1.7),
         [("The three decisions that concede a platform limitation, and name the compensating architecture", 13, DARK, True),
          ("DD-5   An ingress endpoint is served only where the on-behalf-of exchange runs — otherwise withhold it", 11.5, DARK, False),
          ("DD-7   The stop control is credential and policy revocation, NOT deactivation", 11.5, DARK, False),
          ("DD-8   Content control on A2A ingress is a caller-side obligation recorded on the callee", 11.5, DARK, False),
          ("…and eleven residual risks, accepted explicitly rather than assumed away.", 11.5, RED, True)],
         space_after=4)

# 11 — close
s = new()
bg(s, NAVY)
add_box(s, 0, Inches(2.5), W, Pt(5), fill=AMBER)
add_text(s, Inches(0.9), Inches(1.5), Inches(11.5), Inches(0.9),
         [("The one rule to take away", 30, WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)
add_text(s, Inches(0.9), Inches(2.9), Inches(11.5), Inches(1.8),
         [("Claim only controls that run.", 24, AMBER, True),
          ("A field, a serializer and an admin page are not a control. Where the platform records rather than", 14, PALE, False),
          ("enforces, this pattern says so, names the compensating measure, and raises it with its owner.", 14, PALE, False)],
         space_after=8)
add_text(s, Inches(0.9), Inches(5.4), Inches(11.5), Inches(1.4),
         [("specs/pattern/agent-patterns/ — D0 · D1 · D2 (9 pages) · D3 · pattern.md", 12, WHITE, True),
          ("EDAEACP/acp-product-specs  ·  EACPP-1290  ·  Sun Life ACP Product Team", 11, PALE, False),
          ("Every claim carries a source and a revision. Every absence is a search that returned nothing.", 10.5, GRAY, False)],
         space_after=5)

out = Path(__file__).resolve().parent / "Agent-Patterns-ACP.pptx"
prs.save(out)
print(f"Wrote {out} ({N} slides)")
