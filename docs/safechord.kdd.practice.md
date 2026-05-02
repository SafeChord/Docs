---
title: 'KDD 2.0: Dual-Track CLI & Headless Collaboration'
doc_id: safechord.kdd.practice
last_updated: '2026-05-02'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Methodology
summary: Defines the Three-Engine collaboration model for SafeChord v0.3.x. Details how the Settler (Gemini CLI) maintains architectural consistency across decoupled layers through cross-agent protocols, transforming KDD 2.0 into a high-efficiency productivity loop.
keywords:
  - Dual-Track CLI
  - Claude Code
  - Gemini CLI
  - Git Commit Protocol
  - Headless Development
  - Legacy Handoff
logical_path: SafeChord.KDD.Practice
related_docs:
  - safechord.kdd.introduction.md
parent_doc: safechord.kdd.introduction
doc_version: 0.3.5
archetype: script
---

# KDD 2.0 Practice: Three-Engine & Headless Development

In 2026, SafeChord development utilizes a **"Three-Engine"** model: Gemini WebChat for high-level strategic decisions, paired with dual-track CLI agents for headless development and knowledge solidification.

---

## 1. The Three-Engine Model

Tasks are categorized into three tiers based on AI model characteristics and context boundaries:

| Role | Entity | Core Responsibility | Focus |
| :--- | :--- | :--- | :--- |
| **🏛️ Architect** | **Gemini WebChat** | **Design & Trade-offs**: Defines tech stacks, architectural decisions, and long-term analysis. | Strategy (Why/How) |
| **🛡️ Pioneer** | **Claude Code** | **Implementation & Problem Solving**: Handles code implementation, technical spikes, and complex debugging. | Tactics (Spike & Code) |
| **🧠 Settler** | **Gemini CLI** | **Review & Solidification**: Planning tests, performing code reviews, and maintaining KDD documentation. | Execution (Structure) |

> **💡 Agent Roles Update**
> - **CLI as Strategic Assistant**: Since WebChat cannot directly access the local codebase, the Settler CLI agent uses its planning mode to organize context for the Architect.
> - **Workforce Partitioning**: Primary feature development is handled by **Claude Code (Pioneer)**, while the **Settler CLI** focuses on architecture governance and documentation reconciliation.

---

## 2. Communication Interface & Protocols

In a headless environment, standardized protocols are essential for information exchange between agents.

### 🟢 Basic Communication: Git Commit Protocol
For routine iterations without formal handoffs, the **Git Commit Message** is the bridge between agents and humans.
*   **Principle**: Messages must include "Intent" and "Architectural Impact."
*   **Format**: Strict adherence to [Conventional Commits](https://www.conventionalcommits.org/).
*   **Agent Obligation**: Settler must interpret the Pioneer's commit history to understand the implementation context before performing a review.

### 🔴 The Handoff Protocol (Legacy Notes)
When a task reaches a milestone, encounters a deadlock, or requires deep technical transfer, the handoff protocol is triggered.
*   **Medium**: Markdown files stored in `.ai-session-handoffs/`.
*   **Trigger Conditions**:
    - Pioneer completes a spike or phase of development.
    - Settler encounters errors outside its operational scope.
    - Human intervention requires a task handover.
*   **Required Content**:
    1.  **Status/Summary**: Date, direction (From/To), branch status, and progress.
    2.  **What Changed**: File paths and core structural changes.
    3.  **Verified Path**: What has been proven to work? (Crucial for deadlock handoffs).
    4.  **Next Actions**: Clear instructions and verification criteria for the next agent.

### ⚪ Design Drafts
For strategic decisions or complex refactoring, a **Design Draft** serves as the blueprint for the Pioneer.
*   **Medium**: Markdown files stored in `.ai-session-drafts/`.
*   **Required Content**: Background, Proposed Solution, Blueprint (mock code/schemas), Trade-offs, and Next Steps.

---

## 3. Dual-Track Workflow: The KDD Balance

SafeChord employs a label-based **Dual-Track Workflow** to balance "Docs-First" rigor with "Spike-First" agility.

### 🟢 Path A: `kdd:forward` (Order Mode)
Applied to optimizations of existing modules and known architecture extensions.
**Rule**: "Docs before Code"—no implementation without an updated blueprint.

1.  **Strategic Design**: Architect defines the "Why/What"; Settler updates the Markdown Knowledge Map (Blueprints/ADRs).
2.  **Implementation**: Pioneer implements code and tests strictly within the defined boundaries.
3.  **Completion**: Pioneer submits PR and generates a Legacy Note.
4.  **Solidification**: Settler performs a code review against the pre-defined docs, merges, and tags the version.

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

1.  **Strategic Design**: Architect discusses feasibility; Settler creates a Design Draft if codebase state is required.
2.  **Spike**: Pioneer implements a Demo/Spike without documentation constraints.
3.  **Completion**: Pioneer submits PR and generates a detailed Legacy Note.
4.  **Solidification**: **Critical Phase.** Settler performs the PR review and executes **Documentation Reconciliation**, reverse-engineering the spike results back into the SSOT in `Docs/`.

---

## 4. Headless Collaboration Rules

*   **Terminal as SSOT**: All development and testing are completed in the CLI. IDEs are for visual review only.
*   **Review is Documentation**: Settler's review approval implicitly signals that documentation reconciliation is synchronized.
*   **Context Efficiency**: Agents must leverage their massive context windows for cross-service impact analysis to prevent API contract breakage.

---

## 5. Operational Templates (Appendices)

### 🟢 Git Commit Template
```text
<type>(<scope>): <subject> (50 chars max)

[Body: Why was this change needed?]
Explain the motivation and logic. Focus on "Why" rather than "How."
Describe the impact on project architecture or long-term decisions.

Context: [Link to Blueprint or Issue ID]
Impact: [Specific impact on API contracts or infra]
Test: [Verification executed] (e.g., make test-data-ingestor)
Agent: [Gemini CLI / Claude Code]
Legacy: [Pending issues for the next agent]
```

### 🔴 Handoff Template (Legacy Note)
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Agent Name]
> **To**: [Agent Name]
> **Branch**: [Branch Name]
> **Action Required**: [Brief summary]

---

## Status / Summary
[Complete / Partially Complete / Deadlock]

## What Changed
[Structural changes or architectural adjustments]

## Verified Path (Optional)
- [x] What has been proven feasible?
- [ ] Known dead ends or blockers?

## Next Actions
1. [Specific Instruction 1]
2. [Specific Instruction 2]
```
