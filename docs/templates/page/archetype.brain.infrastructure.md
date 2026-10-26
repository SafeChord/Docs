---
title: "Policy: [Infrastructure Component Name]"
status: draft
archetype: brain
code_paths:
  - "Chorde/gitops/k3han/manifests/[component]"
---

# [Component Name] (Brain)

> **Type**: Brain (Infrastructure)
> **Focus**: The design constraints manifests must operate within, and the rationale behind them.
> **Constraint**: No manifest values: manifests express desired state and live under `code_paths`.
> A measured value appears only in Reference Snapshots, labelled with its date.

---

## 1. Design Constraints (Red Walls)
*(Required)*
Hard boundaries that all implementation (manifests, configs) must satisfy.
Express as targets or ceilings, not current values.

*   **[Constraint Category]**: [Constraint statement with threshold]
*   **[Constraint Category]**: [Constraint statement with threshold]

> Example: "Cross-border latency must remain below 100ms",
> "Monthly cost must not exceed NT$800"

## 2. Strategy / Policy Definition
*(Required)*
The architectural approach chosen to satisfy the constraints above.
Explain the **Why** and **How** at a design level.

### [Strategy Aspect A]
*   **Approach**: [What pattern or architecture was chosen]
*   **Rationale**: [Why this satisfies the constraints]

### [Strategy Aspect B]
*   **Approach**: [What pattern or architecture was chosen]
*   **Rationale**: [Why this satisfies the constraints]

## 3. Reference Snapshots
*(Optional — point-in-time observations, NOT SSOT)*
Measured values or configuration summaries that validated the design constraints
at a specific point in time. These will drift; always verify against the
codebase or monitoring tools for current state.

> Label clearly: "as of vX.Y", "verified YYYY-MM-DD"

| Observation | Value | Constraint Validated |
| :--- | :--- | :--- |
| [What was measured] | [Measured value] | [Which red wall this proves] |

> *Current values live in manifests under `code_paths`, or in monitoring dashboards.*

## 4. Trade-offs & Consequences
*(Recommended)*

| Pros | Cons | Mitigation |
| :--- | :--- | :--- |
| [Gain from this strategy] | [Cost or risk introduced] | [How we manage the downside] |

## 5. References
*(Optional)*
*   **Manifests**: `code_paths` in frontmatter
*   **Related Policies**: [Links to sibling infra docs]
*   **External**: [Vendor docs, architecture references]
