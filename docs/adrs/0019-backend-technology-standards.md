---
parent: Decisions
nav_order: 19
title: ADR-0019 Backend Technology Standards
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0019: Backend Technology Standards

## Status

**Draft**

## Context and Problem Statement

ACP components require backend services. We need to standardize on a minimal tech stack that can scale with enterprise needs while remaining maintainable.

**Key principle**: Choose a small set of staple technologies and commit to them. Avoid tech stack sprawl as AI technologies evolve.

## Decision Drivers

* Enterprise scalability requirements (ADR-0021)
* Python GIL limitations for scaling
* AI/ML ecosystem is Python-heavy
* Team skills and hiring market
* Maintenance burden of multiple tech stacks

## Decision Outcome

**Status: Pending team discussion**

This ADR presents two options for the backend technology stack. The team should discuss and decide based on current priorities and constraints.

---

## Option A: Go Primary (with Rust Investment Path)

**Philosophy**: Ship fast now with Go, invest in Rust over time for hot paths.

| Use Case | Now | Future |
|----------|-----|--------|
| API Services | Go | Rust for high-throughput |
| Infrastructure Adapters | Go | Go |
| Message Consumers | Go | Rust |
| CLI Tools (distributed) | Go | Rust |
| gRPC Services | Go | Rust |
| AI Gateway / Proxy | Go | Rust |

**Pros:**
- Fast to learn for C# background (similar feel)
- Go compiles in seconds, Rust in minutes
- Strong hiring market for Go
- Simpler debugging in production
- Gradual learning curve for Rust

**Cons:**
- Learning curve for Python/Java/C# team
- Two languages to maintain long-term
- Migration cost later (Go → Rust)
- Go's GC can cause latency spikes under load

---

## Option B: Rust Primary (with Python for ML)

**Philosophy**: If Rust is the destination, start there. Invest upfront for long-term gains.

| Use Case | Language |
|----------|----------|
| All production services | Rust |
| ML/AI pipelines | Python |
| Internal dev tools | Python (Typer) |

**Pros:**
- Single production language (simpler ops)
- Maximum performance from day one
- Learning compounds over time
- No migration cost later
- Future-proof for AI compute scale

**Cons:**
- 6-12 month learning curve for Rust
- Steepest learning curve of all options
- Smaller hiring pool
- Longer compile times
- Harder debugging (ownership model)

---

## Option C: Python Primary (Leverage Team Strength)

**Philosophy**: Use what the team knows best. Scale horizontally. Optimize hot paths with Rust extensions when needed.

| Use Case | Language |
|----------|----------|
| API Services | Python (FastAPI) |
| Infrastructure Adapters | Python |
| Message Consumers | Python |
| Internal dev tools | Python (Typer) |
| ML/AI pipelines | Python |
| **Hot paths (if needed)** | **Rust via PyO3** |

**Pros:**
- Team knows Python — fastest initial velocity
- Rich AI/ML ecosystem native
- Python 3.14+ has free-threading (Oct 2025)
- Can call Rust via PyO3 for hot paths
- Easiest hiring (largest developer pool)

**Cons:**
- Higher memory per replica than Go/Rust
- Need async discipline (asyncio everywhere)
- Free-threading ecosystem still maturing
- May need Rust later for extreme scale

**When Python at Scale Works:**
- I/O-bound workloads (most API services)
- Asyncio for concurrent requests
- Horizontal scaling (more replicas)
- Caching layer in front (Redis)

**When to Drop Down to Rust:**
- >100K req/s sustained on single service
- Memory-constrained environments
- <10ms p99 latency requirements

---

## Decision Criteria

**Team Context**: Python/Java/C# background (Go is also new to learn)

| If Team Prioritizes... | Choose |
|------------------------|--------|
| **Fastest time-to-market** | **Option C (Python)** |
| Long-term max performance | Option B (Rust) |
| Balanced path forward | Option A (Go) |
| Leveraging team skills | Option C (Python) |
| Building new team from scratch | Option B (Rust) |
| Minimal ops complexity | Option B (Rust) |
| Rich AI/ML ecosystem | Option C (Python) |
| Lowest memory footprint | Option A or B |

**Learning Curve (for Python/Java/C# team):**
- Option A (Go): 2-3 months to productive
- Option B (Rust): 6-12 months to productive
- Option C (Python): Immediate productivity

---

## Rust — Why Consider It Seriously

**ACP routes significant AI compute. Rust offers substantial performance gains for this layer.**

Why Rust matters:
- **Zero-cost abstractions**: No GC pauses under load
- **Memory efficiency**: Lower resource cost per request
- **Predictable latency**: Critical for real-time AI routing
- **10-20% faster** than Go for compute-intensive paths
- **Growing AI ecosystem**: Rust ML libraries maturing

> See ADR-0022: Performance Over Developer Complexity for AI Infrastructure

---

### Python: Production-Viable with Proper Architecture

**If Option C is chosen**, Python becomes the primary backend language. The key is proper architecture:

**Production Python Requirements:**
- AsyncIO for I/O-bound workloads
- FastAPI or Starlette for HTTP
- SQLAlchemy or SQLModel for database
- Horizontal scaling (Kubernetes replicas)
- Caching layer (Redis) for hot paths

**When Python Needs Help:**
- CPU-bound hot paths → Rust extension (PyO3)
- >100K req/s → Consider Rust rewrite
- Memory-constrained → Consider Go/Rust

**Python Stack (Production):**

| Category | Technology |
|----------|------------|
| HTTP Framework | FastAPI |
| Async | asyncio (native) |
| Database | SQLAlchemy 2.0 / SQLModel |
| Package Management | Poetry |
| Typing | mypy (strict) |
| Linting | ruff |
| Testing | pytest + pytest-asyncio |
| Hot paths | PyO3 (Rust) |

---

### If Not Option C: Python for ML/Scripts Only

If Option A or B is chosen, Python scope is limited:

| Acceptable | Prefer Go/Rust Instead |
|------------|------------------------|
| AI/ML model training | Horizontally-scaled API services |
| Data analysis notebooks | High-throughput message consumers |
| **Internal CLI tools (Poetry/Typer)** | Infrastructure adapters |
| Internal scripts/automation | Services requiring >10 replicas |
| Prototyping and PoCs | — |
| Developer tooling | — |
| **Orchestration and glue code** | — |

> **Note on Python Scalability**
>
> Traditional GIL concerns are often overstated for many use cases:
> - Asyncio handles I/O-bound workloads efficiently even with GIL
> - Many production systems run Python at scale with proper architecture
> - Python 3.14+ now offers official free-threading support (PEP 779)
>
> The recommendation for Go in production services is about:
> - Simpler deployment (single binary)
> - Lower memory footprint per replica
> - Established patterns for horizontal scaling
> - Not needing to track Python free-threading ecosystem maturity
>
> Teams with strong Python expertise can prototype in Python and migrate to Go when scaling patterns are understood, or run Python at scale where the workload characteristics fit.

> **Discussion Point: Python GIL Removal (PEP 703 / PEP 779)**
> 
> Python 3.13 (Oct 2024) introduced experimental free-threaded builds.
> Python 3.14 (Oct 2025) made free-threading officially supported.
> 
> **Implications:**
> - Python is now viable for CPU-bound parallel workloads
> - Single-threaded overhead: ~5-10% (acceptable for many use cases)
> - Libraries like asyncio, ctypes have first-class free-threading support
> 
> **Revisit Trigger:**
> - When Python 3.15+ matures free-threading further
> - When team benchmarks show acceptable performance for our workloads
> - When majority of our ML dependencies confirm free-threading compatibility
> 
> Go remains the recommended default for production services, but this decision should be revisited annually as the Python ecosystem evolves. 
> For now, Go remains the primary choice for production services due to established ecosystem, team expertise, and zero GIL concerns. Revisit annually.

### CLI Tool Guidance

| Tool Type | Language | Rationale |
|-----------|----------|-----------|
| **Distributed to users** | Go | Single binary, cross-platform |
| **Internal dev tools** | Python (Typer) | Faster iteration, team familiarity |
| **Performance-critical** | Rust | Fastest execution |

Example: `acp` CLI for this repo → Python (Typer) is fine since it's internal dev tooling.

### Go Stack

| Category | Technology |
|----------|------------|
| HTTP Framework | Chi or Echo |
| Database | sqlc (type-safe SQL) |
| Configuration | Viper |
| Logging | zerolog or slog |
| Testing | testing + testify |
| Metrics | Prometheus client |
| Tracing | OpenTelemetry |

### Python Stack (when used for ML/scripts)

| Category | Technology |
|----------|------------|
| ML Framework | PyTorch, Transformers |
| Data Processing | Pandas, Polars |
| Package Management | Poetry |
| Typing | mypy (strict) |
| Linting | ruff |
| Testing | pytest |

### Common Standards

#### API Design

- OpenAPI 3.1 specification required
- REST for external APIs
- gRPC for internal service-to-service
- Versioning: `/api/v1/` prefix

#### Observability (All Services)

| Category | Tool |
|----------|------|
| Metrics | Prometheus |
| Tracing | OpenTelemetry |
| Logging | Structured JSON |

#### Security

- No secrets in code
- Input validation at API boundary
- SQL parameterization
- Rate limiting on public endpoints

## Consequences

**Good:**
* Minimal tech stack (Go + Python for ML)
* Clear separation: Go for scale, Python for research
* Reduced maintenance burden

**Bad:**
* Team may need Go training
* Some AI tooling requires Python wrappers

## More Information

* Related: ADR-0021 (Scalability Requirements)
* Related: ADR-0020 (Open Source Evaluation)
* Related: ADR-0017 (Testing Strategy)
