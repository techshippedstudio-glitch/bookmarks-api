# Bookmarks API Constitution

## Core Principles

### I. Typed API Contracts

Every endpoint MUST declare an explicit request model (when it accepts a body or query
parameters beyond simple path IDs) and an explicit response model. Untyped dictionaries MUST NOT
cross the HTTP boundary in either direction. The published API description (OpenAPI) MUST be
generated from these models, so the contract and the code cannot drift apart.

Rationale: typed models are the contract with API consumers; they make validation automatic and
keep documentation truthful.

### II. Real-Database Testing (NON-NEGOTIABLE)

Tests that touch persistence MUST run against a real PostgreSQL database dedicated to tests. Mocks,
fakes or in-memory substitutes for the database MUST NOT be used to verify persistence behavior,
including constraints, ordering and filtering. Each test MUST start from a known database state.

Rationale: constraints, transactions and query behavior are where persistence bugs live; only the
real database exercises them.

### III. Consistent Error Shape

Every error response, including validation errors, not-found and conflicts, MUST use one JSON
shape with a stable machine-readable `code` and a human-readable `message`, plus optional
`details`. HTTP status codes MUST match the error class (400/422 invalid input, 404 not found, 409
conflict). Internal details such as stack traces or SQL MUST NOT appear in responses.

Rationale: clients handle one shape instead of special-casing every endpoint.

### IV. Minimal Dependencies

A new third-party dependency MUST be justified in the plan by a need the standard library or an
existing dependency cannot meet with reasonable effort. Dependencies MUST be pinned to a compatible
version range. Each dependency is a maintenance and security cost and MUST earn its place.

Rationale: fewer dependencies mean fewer upgrades, fewer vulnerabilities and a codebase viewers can
read end to end.

### V. Tests Ship With Every Feature

A feature is not complete until automated tests cover each of its acceptance scenarios, including
the error paths. Tests MUST be committed in the same change as the behavior they verify, and the
full test suite MUST pass before a feature is considered done.

Rationale: untested behavior is unverified behavior; shipping tests with the feature keeps the spec,
code and tests aligned.

## Quality Gates

- The full test suite MUST pass against the test database before a feature is considered done.
- Every acceptance scenario in a feature spec MUST map to at least one automated test.
- Every new dependency MUST appear in the plan with its justification (Principle IV).
- Every endpoint MUST appear in the generated OpenAPI document with request and response models
  (Principle I).

## Development Workflow

- Features follow the Spec Kit flow: specify, clarify, plan, tasks, implement, converge.
- Specifications describe what and why; technology choices belong in the plan.
- Plans MUST pass a constitution check before tasks are generated; any violation MUST be recorded
  with its justification in the plan's complexity tracking.
- A feature is complete when `/speckit-converge` reports Converged and the test suite passes.

## Governance

This constitution supersedes other project practices. Amendments are made with
`/speckit-constitution`, recorded in version control, and versioned semantically: MAJOR for removing
or redefining a principle, MINOR for adding a principle or materially expanding guidance, PATCH for
clarifications. Every plan and review MUST verify compliance with these principles; deviations
require written justification in the plan.

**Version**: 1.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
