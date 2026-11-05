---
title: SafeChord Knowledge Tree
status: active
archetype: tree
---

# SafeChord Knowledge Tree

> **Type**: Tree
> **Focus**: Which pages to read first for each kind of work, then every page under `docs/`, nested by layer and by parent page, with what each covers.
> **Constraint**: One line per page. What a page covers beyond its line is on the page, and its archetype is in its frontmatter.

## Read First {#read-first}

| Work | Read first |
| :--- | :--- |
| Choosing a mode, or writing a ticket, commit, handoff or draft | [Practice](safechord.kdd.practice.md), then the mode page it names |
| Changing a SafeZone service | [App map](safechord.safezone.md), [service standards](safechord.safezone.service.standards.md), then the service's blueprint |
| Changing the SZCLI or the time server | Its toolkit blueprint; the [command reference](safechord.safezone.toolkit.cli.reference.md) for SZCLI commands |
| Finding why SafeZone is built a certain way | [Decision log](safechord.safezone.decisions.md) |
| Changing charts or values in SafeZone-Deploy | [Deployment](safechord.safezone.deployment.md), [environments](safechord.environment.md) |
| Cutting, validating or promoting a release | [Delivery mode](safechord.kdd.practice.delivery.md), [SafeZone delivery](safechord.safezone.delivery.md) |
| Changing the K3han platform in Chorde | [Chorde](safechord.chorde.md), [K3han](safechord.chorde.k3han.md), then the page for the subject |
| Secrets, access control or the supply chain | [Security](safechord.security.md) |
| Detecting and triaging trouble on the live platform | [K3han operations](safechord.chorde.k3han.operations.md), [monitoring](safechord.chorde.k3han.monitoring.md) |
| Editing a page under `docs/` | `Docs/.ai-rules.md` |

## Tree {#tree}

*   **SafeChord Ecosystem**
    *   [index.md](index.md): system overview: tiers, tech stack, design philosophy and strategic evolution
    *   [safechord.knowledgetree.md](safechord.knowledgetree.md): this page
    *   [safechord.security.md](safechord.security.md): security architecture and SecretOps governance
    *   [safechord.environment.md](safechord.environment.md): tiered environments, from local Compose to platform staging

    *   **Knowledge Layer (repo: Docs)**: KDD methodology, standards, SSOT
        *   [safechord.kdd.introduction.md](safechord.kdd.introduction.md): KDD philosophy
        *   [safechord.kdd.practice.md](safechord.kdd.practice.md): modes, layers, protocols
            *   [safechord.kdd.practice.development.md](safechord.kdd.practice.development.md): the two-engine model, dual-track flow and review
            *   [safechord.kdd.practice.delivery.md](safechord.kdd.practice.delivery.md): gates, floor and focus, what Development hands over
            *   [safechord.kdd.practice.operations.md](safechord.kdd.practice.operations.md): operations mode (draft)
        *   [safechord.kdd.alignment.md](safechord.kdd.alignment.md): standing task: internal alignment of `Docs/`
        *   [safechord.kdd.discovery.md](safechord.kdd.discovery.md): standing task: discovery of where the process leaks
        *   [safechord.kdd.changelog.md](safechord.kdd.changelog.md): collaboration model history and superseded designs

    *   **Application Layer (repo: SafeZone)**: source code, business logic, AsyncIO dataflow
        *   **Core architecture**
            *   [safechord.safezone.md](safechord.safezone.md): app map: async dataflow and event-driven design
            *   [safechord.safezone.service.standards.md](safechord.safezone.service.standards.md): cross-service standards and the index of shared contracts
            *   [safechord.safezone.decisions.md](safechord.safezone.decisions.md): decision log, append-only
            *   [SafeZone `CHANGELOG.md`](https://github.com/SafeChord/SafeZone/blob/main/CHANGELOG.md): application version history, kept in the SafeZone repository
        *   **Microservices**
            *   [safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md): simulator: AsyncIO data source
            *   [safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md): ingestor: Kafka producer gateway
            *   [safechord.safezone.service.worker.md](safechord.safezone.service.worker.md): worker: Go / franz-go consumer
            *   [safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md): API: aggregator and response cache
            *   [safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md): UI: time-aware visualization (legacy)
            *   [safechord.safezone.service.dashboard-v2.md](safechord.safezone.service.dashboard-v2.md): UI: React SPA and time travel
        *   **Toolkit**
            *   [safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md): time server: virtual clock controller
            *   [safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md): SZCLI: operations tooling and CLI relay
                *   [safechord.safezone.toolkit.cli.reference.md](safechord.safezone.toolkit.cli.reference.md): SZCLI command reference: commands, output envelope, runbooks

    *   **Deployment Layer (repo: SafeZone-Deploy)**: configuration, Helm, GitOps CD
        *   [safechord.safezone.deployment.md](safechord.safezone.deployment.md): deployment architecture
        *   [safechord.safezone.delivery.md](safechord.safezone.delivery.md): SafeZone delivery: release phases, routes, IssueOps

    *   **Infrastructure Layer (repo: Chorde)**: Kubernetes, platform operators, scheduling
        *   [safechord.chorde.md](safechord.chorde.md): Chorde overview: platform framework and repo structure
        *   [safechord.chorde.k3han.md](safechord.chorde.k3han.md): K3han: hybrid-cloud cluster navigation
            *   [safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md): physical topology, latency matrix and Tailscale SDN
            *   [safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md): ingress perimeter: dual-channel isolation
            *   [safechord.chorde.k3han.network.md](safechord.chorde.k3han.network.md): pod data path: flannel as CNI, Tailscale as transport
            *   [safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md): reliability tiers and taints policy
            *   [safechord.chorde.k3han.storage.md](safechord.chorde.k3han.storage.md): persistent storage: node-local volumes and durability
            *   [safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md): observability: Loki and Prometheus Operator
            *   [safechord.chorde.k3han.operations.md](safechord.chorde.k3han.operations.md): operations: detection and triage (draft)
            *   [safechord.chorde.k3han.changelog.md](safechord.chorde.k3han.changelog.md): platform version history
