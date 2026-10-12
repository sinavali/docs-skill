# Enterprise Core Directives & Master Rulebook

This specification defines the foundational laws of the `enterprise-product` engineering operating system. All AI agents, contributors, and automated pipelines are bound by these directives.

---

## 1. Prime Directives (P1 – P8)

### P1: Single Monorepo Orchestration
Every enterprise product is strictly contained within a single monorepo governed at the root by **Nx**. Cross-boundary dependencies, project boundaries, and CI/CD task graphs must be declared deterministically. No rogue repositories or detached poly-repo pipelines are permitted.

### P2: Hierarchical Governance via `AGENT.md`
Governance cascades strictly from the repository root to project subdirectories:
$$\text{Enterprise Inviolables} \implies \text{Root AGENT.md} \implies \text{Subproject AGENT.md}$$
Subproject manifests configure local toolchains, build targets, and domain profiles, but can never dilute or override Tier 1 directives.

### P3: Strict Architectural Boundary Isolation
Every codebase component must declare and adhere to an approved **Architectural Profile** (Profile A: DDD/Hexagonal, Profile B: Web Clean/SSR, Profile C: Mobile Clean/BLoC, Profile D: Shared Contracts). Domain logic must remain pure, isolated from frameworks, databases, and UI presentation concerns.

### P4: Value-Driven & Real-World Testing
Happy-path-only testing is strictly prohibited. Integration and adapter tests must execute against **real ephemeral containers (Testcontainers/Podman)**; in-memory SQL emulators (e.g., SQLite replacing PostgreSQL/MySQL) are banned. Boundary invariants, race conditions, resilience timeouts, and error paths must be tested.

### P5: Impact Before Implementation (Change Surface)
No non-trivial modification to code, configuration, or contracts may begin without an approved and mechanically validated **Change Surface** artifact (`CHANGE_SURFACE.md`). Agents must discover the blast radius before altering files.

### P6: 2-Pass PR Self-Audit & Zero-Drift Gates
Every Pull Request must undergo a mandatory 2-Pass Self-Audit against the 10-Dimension Enterprise Audit Suite before merge eligibility. Automated squash-merging (`gh pr merge --squash`) is permitted only when 0 blocking defects remain and CI is fully green; otherwise, immediate escalation occurs.

### P7: Complete Documentation & NC Transparency
Ambiguities and missing domain knowledge must not be guessed or invented. They must be registered immediately as formal **`NEED_CLARIFICATION` (NC)** items. Unresolved NC items older than 14 days mechanically block PR merges. Architectural decisions must be preserved as Architecture Decision Records (ADRs).

### P8: Sovereign & Zero-Trust Infrastructure
Systems prioritize self-hosted, vendor-agnostic infrastructure (Podman, Docker, Kubernetes, PostgreSQL, Redis, MinIO). All data storage, event streaming, and API wire formats must strictly enforce the **UTC Storage Convention** and zero-trust security postures.

---

## 2. The Tiering Map

All architectural and engineering rules are categorized into three hierarchical tiers:

```text
┌────────────────────────────────────────────────────────┐
│  Tier 1: Enterprise Inviolables (Zero-Overridable)     │
│  - Nx Root Monorepo       - Podman/Testcontainers Only │
│  - Pure Domain (DDD)      - 2-Pass PR Self-Audit       │
│  - UTC Storage Convention - 14-Day NC Merge Block      │
├────────────────────────────────────────────────────────┤
│  Tier 2: Strong Defaults (ADR & AGENT.md Justified)    │
│  - Coverage Targets (≥95% Domain, ≥80% Adapters)       │
│  - Port-Adapter Separation & Hexagonal Interfaces      │
│  - OpenAPI / Protobuf Contract Generation              │
├────────────────────────────────────────────────────────┤
│  Tier 3: Context-Dependent / Advisory (Local Ergonomics)│
│  - Framework UI component styling / UI state nuance    │
│  - Internal utility helper structuring                 │
│  - Local dev caching / tooling ergonomics              │
└────────────────────────────────────────────────────────┘
```

### Tier 1: Enterprise Inviolables (Non-Negotiable)
These rules cannot be relaxed, bypassed, or overridden by any project, developer, or agent:
1. **Single Monorepo via Nx**: Root orchestration must manage `lint`, `test`, `build`, and `audit` across all packages.
2. **Pure Domain Logic**: Domain entities, value objects, and domain services must have zero imports from frameworks, ORMs, transport layers, or external third-party SDKs.
3. **No In-Memory SQL Emulators**: All relational database queries, transactions, and migration tests must execute against real database engines running in ephemeral Podman/Docker containers.
4. **Mandatory Change Surface**: No non-trivial implementation without an approved `CHANGE_SURFACE.md`.
5. **UTC Storage Convention**: All database timestamps, queue messages, events, and API payloads must be persisted and exchanged in UTC (ISO 8601 with `Z` or UTC timestamp).
6. **14-Day NC Merge Block**: Any open `NEED_CLARIFICATION` item older than 14 calendar days mechanically halts automated merges and triggers review escalation.
7. **2-Pass PR Self-Audit Protocol**: The agent must audit its own diff across both passes and achieve 0 blocking findings before merging.

### Tier 2: Strong Defaults (Requires ADR & `AGENT.md` Override)
These are standard enterprise requirements. Deviations are permitted only with an accepted Architecture Decision Record (ADR) and explicit declaration in the subproject's `AGENT.md`:
1. **Coverage Thresholds**: $\ge 95\%$ Line/Branch coverage for domain packages; $\ge 80\%$ Line coverage for adapters and HTTP handlers. If a project deviates, an ADR must justify the alternative threshold and rationale.
2. **Contract-First APIs**: External APIs must derive from OpenAPI or Protobuf schemas.
3. **Strict Hexagonal Isolation**: Use cases access external services through interface ports. (See YAGNI carve-out below).

### Tier 3: Context-Dependent / Advisory
Ergonomic guidelines determined by project teams:
1. Internal folder structure for UI widgets within component libraries.
2. Selection of client-side cache utilities (React Query vs SWR) within Profile B applications.
3. Local development seed script syntax.

---

## 3. Operational Protocols & Carve-Outs

### 3.1 Self-Hosted Infrastructure Preference
Enterprise products must remain deployable on sovereign infrastructure without proprietary vendor cloud lock-in:
- **Compute**: Standard container images (OCI compliant) orchestratable via Kubernetes, Docker Compose, or Podman quadlets.
- **Data Persistence**: Standard open-source datastores (PostgreSQL, Redis, ClickHouse, MinIO S3-compatible storage).
- **Vendor SDK Ban in Domain**: Proprietary cloud SDKs (AWS SDK, Azure SDK, Firebase) must be completely encapsulated behind secondary adapters. Domain logic must never reference cloud vendor symbols.

### 3.2 The Hexagonal Port YAGNI Carve-Out
While Profile A mandates Hexagonal Architecture (Ports and Adapters), premature interface bloat violates simplicity:
- **Port Required**: Whenever a dependency crosses an external boundary (Databases, Third-Party APIs, Message Brokers, Email Services, Clock/Time, Filesystem, Authentication providers).
- **YAGNI Carve-Out (Direct Dependency Allowed)**: Internal pure domain utilities, mathematical functions, string parsers, and in-process stateless value objects do **not** require an abstract interface/port if there is only ever one in-memory implementation. Do not create an `IStringManipulator` for standard library utilities.

### 3.3 The UTC Storage Convention
Timezone mishandling is a critical class of enterprise defects:
1. **At Rest**: Every timestamp column in PostgreSQL/MySQL must use `TIMESTAMP WITH TIME ZONE` (PostgreSQL) or UTC `DATETIME`/`BIGINT` milliseconds. Storing local timezone offsets or string representations like `EST` is forbidden.
2. **In Motion**: All JSON/REST and Protobuf contracts must serialize timestamps in ISO 8601 UTC format: `YYYY-MM-DDTHH:mm:ss.sssZ` or Unix epoch milliseconds UTC.
3. **In Logic**: Domain calculations must utilize UTC clock ports (`Clock.UtcNow()`). The local timezone of the running server or container is irrelevant and must be treated as `UTC`.
4. **Presentation**: Conversion to user-local timezone occurs strictly at the edge UI display layer (Profile B or Profile C).
