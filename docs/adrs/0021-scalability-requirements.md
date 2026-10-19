---
parent: Decisions
nav_order: 21
title: ADR-0021 Scalability Requirements
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0021: Scalability Requirements

## Status

**Draft**

## Context and Problem Statement

ACP components must scale to enterprise workloads. As AI/ML technology evolves, our tech stack will expand. We need to:

1. Choose a small set of **staple technologies** and commit to them
2. Avoid technologies with known scaling limitations in production paths
3. Stay adaptable as the technology landscape evolves

**Key concern**: Python's GIL (Global Interpreter Lock) causes scaling issues. Python should not be used in production services that require horizontal scaling.

## Decision Drivers

* Enterprise scale requirements
* Technology stack minimization (reduce maintenance burden)
* Python GIL limitations for concurrent workloads
* AI/ML ecosystem is Python-heavy (tension with scaling)
* Rapid evolution of AI technologies

## Decision Outcome

### Staple Technologies (Primary Choices)

| Category | Primary | Alternative | Notes |
|----------|---------|-------------|-------|
| **Services/APIs** | Go | Rust | Rust for max performance |
| **Frontend** | Next.js (React) | — | |
| **CLI Tools (distributed)** | Go | Rust | Single binary |
| **CLI Tools (internal)** | Python (Typer) | Go | Dev tooling, faster iteration |
| **Scripts/Automation** | Python | — | Internal only |
| **AI/ML Pipelines** | Python | — | Training, preprocessing |
| **AI/ML Serving** | Go wrapper + Python inference | Rust wrapper | Production serving |

### Python Limitations — Where NOT to Use

**Avoid Python for:**
- High-throughput API services
- Infrastructure adapters (AWS, K8s, Snowflake)
- Message queue consumers at scale
- Any service requiring horizontal scaling
- Long-running services with concurrent requests

**Python acceptable for:**
- AI/ML model development and training
- Data analysis and notebooks
- Internal scripts and automation
- CLI tools for developers (non-distributed)
- Prototyping (with expectation to rewrite for production)

### AI/ML Serving Pattern

When AI/ML models need to serve production traffic:

```
                    ┌─────────────────┐
                    │   Go API Layer  │  ← Handles scale, routing
                    └────────┬────────┘
                             │ gRPC/HTTP
                    ┌────────▼────────┐
                    │  Python Model   │  ← Stateless inference
                    │  (containerized)│
                    └─────────────────┘
```

- Go handles HTTP routing, auth, rate limiting, load balancing
- Python runs stateless model inference in containers
- Kubernetes manages Python container scaling
- Keep Python containers single-purpose, stateless

### Horizontal Scaling Requirements

All production services must support:

| Requirement | Implementation |
|-------------|----------------|
| **Stateless** | No in-memory state |
| **Health checks** | `/health` endpoint |
| **Graceful shutdown** | Handle SIGTERM |
| **Connection pooling** | Pool DB/cache connections |
| **Idempotency** | All writes idempotent |

### Technology Evolution Guidance

As AI technology evolves:

1. **Evaluate carefully**: New tools must pass ADR-0020 (Open Source Evaluation)
2. **Prefer extensions**: Extend existing staple tech over adding new languages
3. **Isolate experiments**: Prototypes in Python; production rewrites in Go
4. **Review annually**: Tech stack review to prune unused technologies

## Consequences

**Good:**
* Clear guidance: Go for services, Python for ML research
* Reduced tech stack sprawl
* Avoids Python scaling pitfalls

**Bad:**
* Team may need Go training
* Some AI tooling is Python-only (requires wrappers)

## More Information

* Related: ADR-0019 (Backend Technology Standards)
* Related: ADR-0020 (Open Source Evaluation)
* See: [The Twelve-Factor App](https://12factor.net/)
