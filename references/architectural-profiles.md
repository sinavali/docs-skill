# Enterprise Architectural Profiles

Every project in the monorepo must be assigned to one of four architectural profiles in its `AGENT.md`. This document establishes the concrete rules, folder layouts, allowed dependencies, and forbidden patterns for each profile.

---

## Profile A: Backend & Core Services (DDD + Hexagonal Architecture)

Profile A governs backend microservices, monolithic cores, background workers, and CLI applications (e.g., Go, C# / .NET, Rust, Node.js/TypeScript, PHP/Laravel, Python).

### 1. Architectural Model: Ports and Adapters
All application logic is organized into three concentric rings:

```text
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure Layer (Primary & Secondary Adapters)         │
│  HTTP Controllers, gRPC Servers, DB Repositories, Kafka/AMQP│
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Application / Use-Case Layer                         │  │
│  │  Command Handlers, Query Handlers, Ports (Interfaces) │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Domain Layer (Pure Core)                       │  │  │
│  │  │  Entities, Value Objects, Domain Events, Rules  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Dependency Inversion Rules
- **The Domain Rule**: The Domain Layer has **zero dependencies** on outer layers, external frameworks, ORMs, HTTP libraries, or cloud SDKs.
- **The Application Rule**: Depends only on Domain. Declares Primary Ports (inbound interfaces) and Secondary Ports (outbound interfaces for persistence, messaging, clock).
- **The Infrastructure Rule**: Implements Secondary Ports (e.g., `PostgresUserRepository` implements `UserRepositoryPort`) and triggers Primary Ports (e.g., `ExpressUserController` invokes `CreateUserUseCase`).

### 3. Canonical Directory Layout
```text
services/<service-name>/
├── project.json                      # Nx project configuration
├── AGENT.md                          # Profile A manifest
├── src/
│   ├── domain/                       # Pure Domain Layer
│   │   ├── entities/                 # Aggregate roots, entities with private state & invariants
│   │   ├── value-objects/            # Immutable value objects with validation
│   │   ├── events/                   # Pure domain event definitions
│   │   └── exceptions/               # Domain-specific business rule exceptions
│   ├── application/                  # Application Layer
│   │   ├── ports/
│   │   │   ├── inbound/              # Use-case interfaces (commands/queries)
│   │   │   └── outbound/             # Repository, event-publisher, clock interfaces
│   │   ├── use-cases/                # Orchestrators of domain models
│   │   └── dto/                      # Input/Output DTOs for use cases
│   └── infrastructure/               # Infrastructure Layer
│       ├── adapters/
│       │   ├── primary/              # Web controllers, CLI handlers, message consumers
│       │   │   ├── http/
│       │   │   └── grpc/
│       │   └── secondary/            # Database implementations, external API clients, clock
│       │       ├── persistence/
│       │       └── messaging/
│       └── config/                   # Dependency injection, environment parsing
└── tests/
    ├── unit/                         # Pure domain & use-case unit tests (Fast, no I/O)
    ├── integration/                  # Ephemeral container tests (PostgreSQL/Redis/Kafka)
    └── contract/                     # Pact or schema verification tests
```

### 4. Forbidden Patterns in Profile A
- **Anemic Domain Models**: Entities acting as plain property bags with external procedural logic modifying state directly. Invariants must be guarded inside entities.
- **Leaking ORM Entities into Domain**: Exposing Hibernate/Prisma/Entity Framework/Eloquent models as domain models. Persistence models must map to domain entities.
- **In-Memory SQL Mocks in Integration Tests**: Using SQLite in place of PostgreSQL/MySQL in tests. Must use Testcontainers or Podman.
- **Ambient Time Calls**: Calling `DateTime.Now`, `time.Now()`, `Date.now()` inside domain or use-cases. Must inject a `ClockPort`.
- **Framework Attributes/Annotations on Domain Types**: ORM annotations (`@Table`, `@Column`, `[Table]`) inside domain models.

---

## Profile B: Frontend & Web Apps (Next.js, Nuxt, SvelteKit)

Profile B governs server-side rendered (SSR), static, and client-rendered enterprise web applications.

### 1. Architectural Model: Clean Component & State Layering
Web applications decouple presentation, state machines, and data access into distinct layers:

```text
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (Atomic / Composable UI Components)     │
│  Pure renderers, zero business logic, WCAG 2.2 compliant    │
├─────────────────────────────────────────────────────────────┤
│  Feature & State Layer (Custom Hooks / Stores / Machines)   │
│  State transitions, optimistic updates, view-models         │
├─────────────────────────────────────────────────────────────┤
│  Domain & Contract Client Layer (Typed API Clients, DTOs)   │
│  Zod / Valibot schema validation, OpenAPI clients           │
└─────────────────────────────────────────────────────────────┘
```

### 2. Canonical Directory Layout
```text
apps/<web-app-name>/
├── project.json
├── AGENT.md                          # Profile B manifest
├── src/
│   ├── app/                          # Routing & layouts (Next.js App Router / Nuxt pages)
│   ├── components/                   # UI Components
│   │   ├── ui/                       # Primitive design system components (buttons, dialogs)
│   │   └── feedback/                 # Error boundaries, loading states, empty states
│   ├── features/                     # Feature slices
│   │   └── <feature-name>/
│   │       ├── components/           # Feature-specific composition widgets
│   │       ├── hooks/                # Feature state logic & mutations
│   │       └── state/                # Store slices / state machines
│   ├── contracts/                    # Auto-generated API client & Zod response validators
│   └── lib/                          # Framework utilities, telemetry, auth session
└── tests/
    ├── unit/                         # Component and hook unit tests (Vitest / Jest)
    ├── e2e/                          # Critical user journey tests (Playwright)
    └── a11y/                         # Automated accessibility test suite (Axe-core)
```

### 3. Non-Negotiable Mandates
- **SSR Hydration Safety**: No window/document access during SSR execution. No hydration mismatch bugs.
- **Accessibility (WCAG 2.2 AA)**: Interactive elements must have accessible labels, keyboard navigation, and appropriate ARIA attributes.
- **Bundle Budgets**: Project `project.json` must enforce maximum initial JS bundle size ($\le 180 \text{ KB}$ gzipped).
- **Zero-Trust Web Security**: Strict Content Security Policy (CSP), sanitized outputs against XSS, HTTP-only secure cookies for tokens, CSRF tokens on mutating requests.

### 4. Forbidden Patterns in Profile B
- **Direct API Fetches inside Presentation Components**: Components must receive data through feature hooks or props.
- **Missing Loading/Error/Empty States**: Every dynamic view must implement explicit visual states for Loading, Empty, Success, and Error.
- **Unvalidated External Data**: Parsing API responses using `any` or untyped casts without runtime schema validation (e.g. Zod).
- **Inline Styles & Ad-Hoc CSS**: Arbitrary inline color hexes and margins bypassing design tokens.

---

## Profile C: Mobile Clients (Flutter)

Profile C governs mobile applications built with Flutter targeting iOS, Android, and desktop platforms.

### 1. Architectural Model: Clean Architecture + BLoC State Machines
Separation of UI widgets from reactive state machines and encrypted persistence:

```text
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (Flutter Widgets, Pages, Theme)         │
│  Zero business calculations; binds strictly to BLoC states  │
├─────────────────────────────────────────────────────────────┤
│  BLoC / State Layer (Events -> State Machine -> Transitions)│
│  Handles state machines, offline-first queuing, concurrency │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer (Entities, Use Cases, Repository Contracts)   │
│  Pure Dart, zero Flutter framework dependencies            │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (Repositories, SQLCipher, REST/gRPC Clients)    │
│  Hardware encryption, offline synchronization, caching     │
└─────────────────────────────────────────────────────────────┘
```

### 2. Canonical Directory Layout
```text
apps/<mobile-app-name>/
├── project.json
├── AGENT.md                          # Profile C manifest
├── pubspec.yaml
├── lib/
│   ├── core/                         # Network clients, encrypted storage, error handling
│   │   ├── error/
│   │   ├── network/
│   │   └── storage/                  # SQLCipher / secure storage wrapper
│   ├── features/
│   │   └── <feature-name>/
│   │       ├── data/
│   │       │   ├── datasources/      # Remote (REST/gRPC) & Local (SQLCipher)
│   │       │   ├── models/           # Serialization models (freezed/json_serializable)
│   │       │   └── repositories/     # Repository implementations
│   │       ├── domain/
│   │       │   ├── entities/         # Pure Dart business models
│   │       │   ├── repositories/     # Repository interfaces
│   │       │   └── usecases/         # Callable business use cases
│   │       └── presentation/
│   │           ├── bloc/             # Events, States, BLoC logic
│   │           ├── pages/            # Top-level screen widgets
│   │           └── widgets/          # Reusable leaf widgets
│   └── main.dart
└── test/
    ├── unit/                         # Use case & BLoC state transition tests
    ├── widget/                       # Golden tests & widget interaction tests
    └── integration/                  # MockWebServer / containerized backend tests
```

### 3. Non-Negotiable Mandates
- **Encrypted Local Storage**: Sensitive data, tokens, and offline databases must be encrypted using SQLCipher / Keystore / Keychain.
- **Offline-First Synchronization**: Mutating operations must queue securely when offline with idempotent conflict resolution.
- **Battery & Lifecycle Awareness**: Timers, GPS listeners, and background sync streams must pause on app backgrounding and resume cleanly.

### 4. Forbidden Patterns in Profile C
- **Business Logic in `StatefulWidget`**: Mutating state directly inside `setState` for complex domain workflows.
- **Raw Unencrypted SQLite**: Using unencrypted databases for enterprise user data.
- **Importing `package:flutter` into Domain Layer**: Domain entities and use cases must be pure Dart.
- **Hardcoded Screen Dimensions**: Bypassing responsive layouts (`LayoutBuilder`, `MediaQuery`).

---

## Profile D: Shared Contracts & Core Libraries

Profile D governs shared API schemas, client SDKs, common domain utilities, and serialization protocols.

### 1. Architectural Model: Contract-First & Zero Side-Effects
All contracts originate from machine-readable specifications and generate typed code for Profiles A, B, and C:

```text
┌─────────────────────────────────────────────────────────────┐
│  Schema Authority (OpenAPI 3.1 YAML / Protobuf v3 / JSON-S) │
│  Single source of truth for all cross-service communication │
├─────────────────────────────────────────────────────────────┤
│  Generated Code (Go, TypeScript, Dart, C# models & clients) │
│  Strict SemVer compliance, zero manual editing             │
├─────────────────────────────────────────────────────────────┤
│  Pure Validation & Utilities                                │
│  Zero ambient side-effects, deterministic input/output      │
└─────────────────────────────────────────────────────────────┘
```

### 2. Canonical Directory Layout
```text
libs/<library-name>/
├── project.json
├── AGENT.md                          # Profile D manifest
├── schemas/
│   ├── openapi/                      # OpenAPI specification files
│   └── proto/                        # Protocol buffer definitions
├── src/
│   ├── generated/                    # Code generated via buf / openapi-generator
│   └── validators/                   # Contract conformance validators
└── tests/
    ├── compatibility/                # Backward compatibility & schema breaking tests
    └── unit/                         # Serialization & roundtrip validation tests
```

### 3. Non-Negotiable Mandates
- **Semantic Versioning (SemVer)**: Strictly enforce SemVer: MAJOR (breaking changes), MINOR (backwards-compatible additions), PATCH (fixes).
- **Zero Ambient Side-Effects**: Shared libraries must not read environment variables, open network connections, or write to disk upon module import.
- **Schema Drift Gate**: CI must verify that generated code matches schemas exactly (`nx run <contract>:lint-contracts`).
- **Purity**: Pure functional transformations and deterministic validation only.

### 4. Forbidden Patterns in Profile D
- **Breaking Schema Changes without Version Bump**: Removing fields or altering types without deprecation cycles and major version changes.
- **Embedding Environment Secrets**: Hardcoding API keys, URLs, or configuration parameters inside shared libraries.
- **Heavy Framework Dependencies**: Pulling React, Flutter, or ASP.NET into contract packages. Must remain pure and lightweight.
