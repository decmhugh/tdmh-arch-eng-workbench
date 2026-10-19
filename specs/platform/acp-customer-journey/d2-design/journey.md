# The journey — steps 1.1 to 1.9

The authoritative sequence is `customer-journey.mmd`. The block below is **generated from it** by
`scripts/sync_mermaid_embeds.py` and must never be edited in place; CI fails the build if the two
disagree.

<!-- BEGIN GENERATED: journey (source: ../customer-journey.mmd) -->
```mermaid
sequenceDiagram
    participant EU as End User [EU]
    participant ACP as ACP Product Team [ACP]
    participant EA as ACP Enterprise Architect [ACP EA]
    participant CT as Consortium Team [CT]
    participant RA as Regional BG Architects [RA]
    participant DA as Domain Architects [DA]

    Note over EU,DA: Phase 1 - Awareness, Education & Intake

    Note over EU,ACP: Entry gate before Phase 1 - the business provides a completed GbyD GenAI Risk Triage Form and a ready MRM MBCT ID. ACP manually verifies both prerequisites and records the verification; ACP does not perform risk triage or model-risk assessment.

    EU->>ACP: [EU] Submit completed GbyD GenAI Risk Triage Form and ready MRM MBCT ID
    ACP->>ACP: [ACP] Manually verify prerequisites and record verification

    alt Entry prerequisites verified
        ACP-->>EU: [ACP] Confirm onboarding may start
    else Entry prerequisite missing
        ACP-->>EU: [ACP] Pause onboarding pending the missing prerequisite
    end

    EU->>RA: [EU] 1.1 Engage Regional BG Architect for Business Internal Assessment
    RA-->>EU: [RA] Architecture Guidance and Recommendations

    RA->>RA: [RA] 1.2 Assess Fit Against the Pattern Catalogues

    Note over RA,EA: The RA consults integration-patterns and, for agent solutions, the agent-patterns shape catalogue. Screen Agent vs Application, egress vs ingress, and applicable substrates against SUB-E/SUB-I. S1-S4 are examples, not a closed list. Record open criteria; an open or unexercised criterion is not by itself a refusal or a new-pattern finding.

    alt Phase 1.2a - Exact Match to an Existing Pattern

        RA-->>ACP: [RA] 1.2a-1 Confirm Fit to Existing Pattern Shape(s) - No New Pattern Required

        Note over RA,ACP: The engagement runs 1.3 to 1.6 and closes at 1.9. Phases 1.7 and 1.8 are skipped entirely - there is no pattern to assess and nothing to build.

    else Phase 1.2b - New Pattern Required

        RA->>RA: [RA] 1.2b-1 Initiate Governance Approval for the New Pattern (ATG / ISRA / PIA as applicable)
        RA-->>ACP: [RA] 1.2b-2 Confirm New Pattern Required and Approval Request Initiated

        Note over RA,ACP: The long-lead approval may complete after discovery and design start. The engagement may proceed through 1.3-1.7, but approval must be confirmed before 1.8 implementation or upstream delivery. A conditional approval returns to 1.2b-1 for rework; outright refusal is out of scope and tracked as D0 R-9.

    end

    par 1.3 ACP Awareness & Discovery Session
        ACP->>EU: [ACP] ACP Overview & Mandatory Baseline Capability Review (Capability Map, Section 3)
        ACP->>EU: [ACP] Facilitate Use Case Discovery
        EU-->>ACP: [EU] Present Business Use Case & Requirements
    and Regional and Domain Architecture Assessment
        ACP->>RA: [ACP] Engage Regional BG Architect for Assessment
        RA-->>ACP: [RA] Align on Business Use Case & Requirements
        ACP->>DA: [ACP] Consult Domain Architects on the Domains the Use Case Touches
        DA-->>ACP: [DA] Provide Early Domain Architecture Input
    end

    Note over EU,ACP: Output = d0-discovery.md<br/>- Business objectives<br/>- Capability requirements<br/>- Architecture considerations<br/>- Gap assessment

    ACP->>ACP: [ACP] 1.4 Generate Requirements Specification

    Note over ACP: Output = d1-requirements.md<br/>- Functional requirements<br/>- Non-functional requirements<br/>- User stories<br/>- Acceptance criteria<br/>- Governance requirements

    ACP->>ACP: [ACP] 1.5 Create Solution Architecture

    Note over ACP: Output = d2-design.md<br/>- Solution architecture<br/>- ACP pattern selection<br/>- Integration design<br/>- Security and governance controls<br/>- Deployment approach<br/>- Open questions and assumptions

    ACP->>EU: [ACP] 1.6 Present Solution Architecture for Design Review

    alt Phase 1.6a - Changes Requested

        EU-->>ACP: [EU] 1.6a-1 Request Changes
        ACP->>ACP: [ACP] 1.6a-2 Revise d2-design.md and Return to 1.5

        Note over ACP,EU: The design returns to 1.5, is redrafted, and is re-presented at 1.6. It does not proceed until the end user confirms alignment.

    else Phase 1.6b - Design Confirmed

        EU-->>ACP: [EU] 1.6b-1 Confirm Design Alignment

        Note over ACP,EU: Output = Reviewed d2-design.md<br/>- End user confirms the solution meets the business need<br/>- Ready for pattern assessment, or for closing communication on an exact-match engagement

    end

    alt New Pattern Required - from 1.2b

        ACP->>EA: [ACP] 1.7 Architecture Review and Pattern Assessment

        Note over ACP,EA: Existing-versus-new was already ruled by the Regional Architect at 1.2. 1.7 defines the new pattern and names its delivery owner; it is not a second fit decision and it has no reject outcome.

        ACP->>EA: [ACP] 1.7-1 Submit d2-design.md for Review
        EA->>DA: [ACP EA] 1.7-2 Engage Domain Architects for Architecture Review
        DA-->>EA: [DA] 1.7-3 Provide Domain Architecture Guidance
        EA->>RA: [ACP EA] 1.7-4 Consult the Regional Architect on the 1.2b Finding
        RA-->>EA: [RA] 1.7-5 Confirm Regional Context
        EA-->>ACP: [ACP EA] 1.7-6 Provide Architecture Assessment and Pattern Recommendation
        EA->>EA: [ACP EA] 1.7-7 Define the New Pattern
        DA-->>EA: [DA] 1.7-8 Support New Pattern Definition
        EA-->>ACP: [ACP EA] 1.7-9 Confirm New Pattern and Delivery Owner

        RA-->>ACP: [RA] 1.7-10 Confirm Platform Governance Approval Status

        Note over RA,ACP: 1.8 cannot start until the required PIA / ISRA / ATG approval is confirmed. If approval is still pending, the engagement pauses before implementation or consortium delivery; discovery and design may proceed before this gate.

        Note over ACP,CT: Delivery owner follows the delineation rule.<br/>Yes = Component Change (Consortium).<br/>No = Integration Pattern (ACP).

        alt Phase 1.8a - Integration Pattern, ACP Product Team Delivers

            ACP->>ACP: [ACP] 1.8a-1 Create d3-tasks.md

            Note over ACP: Output = d3-tasks.md<br/>- Epics and User Stories<br/>- Implementation Tasks<br/>- Dependencies<br/>- Delivery Plan

            ACP->>ACP: [ACP] 1.8a-2 Implement and Deploy New Pattern

            ACP->>ACP: [ACP] 1.8a-3 Create d4-verification.md

            Note over ACP: Output = d4-verification.md<br/>- Test Results<br/>- Validation Evidence<br/>- Architecture Verification<br/>- Deployment Verification

            ACP->>EA: [ACP] 1.8a-4 Update Request Status: New Pattern Ready

            opt Integration Turns Out to Require a Luminate Change
                ACP->>ACP: [ACP] 1.8a-5 Re-classify as Component Change and Re-enter Consortium Track
            end

        else Phase 1.8b - Component Change, Consortium Delivers

            ACP->>ACP: [ACP] 1.8b-1 Register Ask on Sun Life Board Linked to the Spec Epic
            ACP->>ACP: [ACP] 1.8b-2 Write Delta Spec in acp-consortium-specs

            Note over ACP,CT: Output = Delta Spec<br/>- What Luminate Does Today<br/>- What Is Missing<br/>- What Should Change<br/>- What the Sun Life MVP Already Proved

            ACP->>CT: [ACP] 1.8b-3 Raise Through Consortium Idea Stewards
            CT->>CT: [CT] 1.8b-4 Prioritise, Vote and Deliver Upstream
            CT-->>ACP: [CT] 1.8b-5 Accepted Work Lands Upstream

            ACP->>ACP: [ACP] 1.8b-6 Re-verify and Update Capability Map
            ACP->>ACP: [ACP] 1.8b-7 Close Sun Life Ticket Referencing Consortium Ticket
            ACP->>EA: [ACP] 1.8b-8 Update Request Status: New Pattern Ready

            Note over ACP,CT: ACP confirms hand-back and readiness.

            opt Ask Not Yet Accepted or Still Upstream
                ACP->>EU: [ACP] Provide a Documented Temporary Interim Measure
            end

        end

    else Exact Match - from 1.2a

        Note over ACP,EA: No new pattern is required, so 1.7 and 1.8 are skipped entirely. The engagement goes straight from the confirmed design to the closing communication.

    end

    ACP->>EU: [ACP] 1.9 Communicate Final Delivery and Readiness to Register

    Note over EU,DA: 1.9 also informs ACP EA, CT, RA and DA. It is the only step at which the End User is contacted during and after delivery, and ACP is both responsible and accountable for it.

    Note over EU,DA: Phase 1 Complete - Use Case Ready to Register an Agent
```
<!-- END GENERATED: journey -->

## Reading it

- **1.2 is the fork the whole journey turns on**, and the **Regional Architect** owns it — not the
  ACP Enterprise Architect. An exact match (1.2a) runs 1.3–1.6 and closes at 1.9. Anything else
  (1.2b) needs the applicable governance approval request initiated before specification starts;
  approval is confirmed before 1.8, and the path adds 1.7 and 1.8 (DD-17).
- **`par` at 1.3** — the ACP discovery session, the regional architecture assessment and the
  domain-architect consultation run in parallel, not in sequence. A common misreading is that RA
  engagement waits for ACP.
- **There is no go/no-go step after 1.3.** A business group that has entered the journey has already
  decided to onboard, so the diagram does not model a proceed decision (DD-14).
- **1.6 is a design review with the End User**, run immediately after `d2-design.md` is drafted. The
  business group confirms the solution meets its need, or asks for changes, while the design is
  still cheap to change (DD-15).
- **1.6a is the only loop in Phase 1.** Requested changes return the design to 1.5 to be redrafted
  and re-presented at 1.6, so the loop can run more than once. It is a rework path, not an exit —
  the engagement does not terminate.
- **1.7 is not a second fit decision.** Existing-versus-new was ruled at 1.2. 1.7 defines the new
  pattern, engages the Domain Architects, and names the delivery owner. It has no reject outcome
  (DD-11).
- **1.7 and 1.8 are reached only from 1.2b.** An exact match closes no capability gap, so there is
  nothing to assess and nothing to build.
- **The `Note over` blocks** name the artefact each step produces. They are the same list as the
  artefact model, kept in the diagram so the flow is readable on its own.
- **1.9 is the only step that contacts the End User during or after delivery.** EU is deliberately
  not informed step-by-step through 1.8; the closing communication carries the outcome to every
  party at once (DD-18).
