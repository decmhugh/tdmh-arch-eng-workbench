---
parent: Decisions
nav_order: 22
title: ADR-0022 Performance Over Developer Complexity for AI Infrastructure
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0022: Performance Over Developer Complexity for AI Infrastructure

## Status

**Draft**

## Context and Problem Statement

AI infrastructure operates at a different scale than traditional enterprise software. As AI workloads grow, the cost of inefficiency compounds — every millisecond of latency, every megabyte of memory, every watt of power multiplies across millions of requests.

Traditional enterprise development often prioritizes developer experience over raw performance. This makes sense for CRUD applications with modest traffic. **For AI infrastructure routing massive compute, this tradeoff inverts.**

## Decision Drivers

* ACP routes significant AI compute through its gateway layer
* Cloud costs scale with inefficiency
* AI model serving has strict latency requirements
* Carbon footprint considerations
* Long-term operational cost vs short-term development cost

## Considered Options

1. **Optimize for Developer Experience** — Use familiar languages (Python, Node.js), prioritize time-to-market
2. **Optimize for Performance** — Use high-performance languages (Rust, Go), invest in learning curve
3. **Hybrid approach** — Performance-first for hot paths, developer experience for everything else

## Decision Outcome

**Chosen option: Hybrid approach with performance bias**

For AI infrastructure specifically, we bias toward performance even when it increases developer complexity.

### Principle: Performance-First for AI Hot Paths

```
When building components that:
  - Route AI inference requests
  - Process high-volume message streams  
  - Sit in the critical path of AI workloads

Then:
  - Performance concerns outweigh developer complexity
  - Invest in learning curves for high-performance tools
  - Measure twice, build once
```

### Why This Matters for AI

| Factor | Traditional App | AI Infrastructure |
|--------|-----------------|-------------------|
| Request volume | Thousands/day | Millions/day |
| Latency sensitivity | 100s of ms OK | <10ms required |
| Memory per request | Abundant | Constrained (GPU competition) |
| Cost multiplier | Linear | Exponential (compute costs) |
| Carbon impact | Modest | Significant |

### Practical Implications

**Acceptable complexity for performance gains:**

| Tradeoff | Accept If |
|----------|-----------|
| Rust learning curve | Component handles >50K req/s |
| Manual memory management | Latency P99 <5ms required |
| Async complexity | I/O-bound with high concurrency |
| Build time increase | Hot path in production |

**Not worth the complexity:**

| Tradeoff | Avoid When |
|----------|------------|
| Premature optimization | No production traffic data |
| Exotic languages | Team has no path to learn |
| Custom allocators | Standard allocators sufficient |
| Assembly/SIMD | Library solutions exist |

### Technology Stack Alignment

This ADR reinforces ADR-0019 (Backend Technology Standards):

| Component Type | Language | Rationale |
|----------------|----------|-----------|
| AI Gateway | Rust (future) | Highest throughput, lowest latency |
| Adapters | Go | Good performance, faster development |
| Control Plane | Go | Moderate load, simpler ops |
| ML Pipelines | Python | Ecosystem requirements |
| Internal Tools | Python | Developer velocity |

### Measurement First

Before investing in performance complexity:

1. **Establish baselines** — Measure current performance
2. **Identify bottlenecks** — Profile before optimizing
3. **Quantify gains** — Calculate expected improvement
4. **Calculate ROI** — Compare dev cost vs cloud cost savings

### Long-Term View

As AI workloads grow:
- Today's "premature optimization" becomes tomorrow's necessity
- Investing in high-performance skills pays compound returns
- Architecture decisions are harder to change than code

> **Guiding question**: Will this component still be fast enough when AI traffic 10x?

## Consequences

### Positive

* Lower operational costs at scale
* Better latency for AI workloads
* Reduced carbon footprint
* Team builds high-performance skills
* Architecture ready for growth

### Negative

* Longer initial development time
* Higher learning curve for some languages
* More complex debugging
* Smaller hiring pool for some skills

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Over-engineering low-traffic components | Apply only to identified hot paths |
| Team burnout from complexity | Gradual adoption, training investment |
| Rust expertise shortage | Start with Go, migrate hot paths |
| Analysis paralysis on language choice | Clear decision criteria in ADR-0019 |

## Related ADRs

* ADR-0019: Backend Technology Standards
* ADR-0021: Scalability Requirements

## References

* [The Cost of Cloud Computing](https://www.oreilly.com/library/view/cloud-finops/9781492054610/)
* [Sustainable Software Engineering](https://principles.green/)
* [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
