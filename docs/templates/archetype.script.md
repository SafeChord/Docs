---
title: "[Workflow Name] Script"
doc_id: safechord.[layer].workflow.[name]
doc_version: [Document Version]
app_version: [Target Application Version]
last_updated: "YYYY-MM-DD"
status: draft
authors:
  - [Author Name]
context_scope: "[Repository Name]"
summary: "[One sentence description of the process goal and trigger.]"
keywords:
  - [Tag1]
  - [Tag2]
logical_path: "SafeChord.[Layer].Workflow.[Name]"
related_docs:
  - "[Related Blueprint Doc]"
parent_doc: "[Parent Doc ID]"
archetype: script
code_paths:
  - "[Script/Workflow Root Path]"
---

# [Workflow Name] (Script)

> **Type**: Script (Standard Operating Procedure / Dynamic Workflow)
> **Focus**: Step-by-step execution, actors, order of operations, and verification.
> **KDD Rule**: Implementation (scripts/commands) should ideally live in the codebase.

---

## 1. Objective & Scope
*(Required)*
*   What does this workflow achieve?
*   **Trigger**: When or why is this process executed?
*   **Prerequisites**:
    *   Required permissions.
    *   Environmental state (e.g., "Must be run in Staging").

## 2. Actors & Tools
*(Recommended)*

| Actor / Tool | Responsibility | Type |
| :--- | :--- | :--- |
| **Developer** | Initiates PR | Human |
| **GitHub Actions** | Executes test suite | Automation |

## 3. Standard Operating Procedure (SOP)
*(Required)*
Detailed execution steps.

### Phase 1: Preparation
1.  Step 1...

### Phase 2: Execution
1.  **Key Action**: Describe the core operation.
    *   *Example Command*: `make deploy`
2.  **Expected Response**: What should the system do?

### Phase 3: Verification
1.  How do we confirm success? (e.g., check logs, verify endpoint).

## 4. State Transitions
*(Recommended)*
Describe how entities change state (e.g., `Draft` -> `Review` -> `Merged`).

## 5. Convergence & Resilience
*   **Failure Handling**: What to do if a step fails? (Rollback/Retry).
*   **Automation Boundary**: Which parts of this script are fully automated vs. manual?
