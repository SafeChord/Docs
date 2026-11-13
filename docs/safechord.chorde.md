---
title: 'Map: Chorde Platform Framework'
status: active
archetype: map
code_paths:
  - Chorde/cluster
  - Chorde/gitops
---

# 🛠️ Chorde Platform Map

> **Type**: Map (Infrastructure Command Center)
> **Context**: Manages heterogeneous clusters, implements GitOps v2 delivery, and maintains hybrid-cloud security perimeters.

---

## 1. Platform Vision

**Chorde** (Cluster + Horde) aims to establish a "decentralized yet highly coordinated" infrastructure tribe. As of v0.3.0, the platform has transitioned from simple IaC scripts to an **Operator-managed** modern architecture, realizing the KDD loop of "Code as Environment, Docs as Source."

---

## 2. Repository Structure

Chorde utilizes a **Recursive GitOps v2** architecture, enabling automated orchestration through a single entry point (`root.yaml`).

```text
Chorde/
├── cluster/                 # [Physical] Hardware & OS-level definitions
│   └── k3han/               
│       ├── ansible/         # Record of Actions: Node initialization & OS hardening
│       └── k3s/             # Node Descriptors: K3s configuration backups
│
├── gitops/                  # [State] GitOps Desired State (SSOT)
│   └── k3han/               
│       ├── root.yaml        # Entry Point: The Root Application
│       ├── stages/          # [Layer 0: Orchestrator] Stage-based ApplicationSets
│       │   ├── 00-bootstrap.yaml  # Core: ArgoCD, SealedSecrets, Ingress
│       │   ├── 01-platform.yaml   # Ops: Monitoring, Logging, Operators
│       │   └── 02-components.yaml # App: DB, MQ
│       │
│       ├── manifests/       # [Content] Declarative Resources, one directory per service
│       │   ├── alloy/       # Its Application, pointing at charts/alloy/
│       │   ├── cnpg-*/      # CloudNativePG Operator & Clusters
│       │   └── ...          # 20+ Platform services
│       │
│       ├── charts/          # Wrapped upstream charts: version, overlay, defaults (§4, item 1)
│       └── kustomize/       # Chorde's own kustomizations (§4, item 2)
│
├── scripts/                 # [Lifecycle] Operational & Validation Tools
│   ├── ops/                 # bootstrap-cluster.sh, seal.sh
│   └── test/                # Cross-region connectivity & health checks
│
└── legacy/                  # [Archive] Historical configurations (v0.1.x / v0.2.x)
```

**Argo CD deploys itself from the bootstrap stage** (Chorde#68). `00-bootstrap.yaml` lists `argocd`, at wave 2, after sealed-secrets, whose CRD its SealedSecrets need. The generated `bootstrap-argocd` syncs `manifests/argocd/` with the stage's prune and self-heal: the `argocd` Application, whose one source is the wrapper `charts/argocd/` (§4, item 1), and the SealedSecrets holding Argo CD's repository credentials. A merged change to either directory reaches K3han with no hand step.

- **`argocd` never leaves the bootstrap list.** `bootstrap-argocd` carries the ApplicationSet's resources finalizer and its stage prunes, so taking `argocd` out deletes the `argocd` Application and the SealedSecrets, and with them the repository Secrets.
- **The `argocd` Application carries no resources finalizer.** Deleted with one, it would take Argo CD down with it; deleted without, it leaves Argo CD running.
- A script in `scripts/test/` checks both.
- The stage sets no progressive sync, so the waves of its generated Applications order nothing. Not tested: whether, on a fresh cluster, `bootstrap-argocd` syncs on its own once the sealed-secrets CRD exists, if its first sync ran before it.

**A from-scratch bootstrap** starts Argo CD by hand and leaves the rest to `root.yaml`:

1. Install Argo CD from the wrapper, as a Helm release named `argocd` in the namespace `argocd`, the names the `argocd` Application renders with.
2. Create the AppProjects the Applications use (`chorde`, `safezone`): they are not in Git.
3. Give the sealed-secrets controller K3han's sealing keys before it starts, or no SealedSecret in Chorde decrypts. Not established: where the keys' backup lives.
4. Run `scripts/ops/bootstrap-cluster.sh k3han`: it waits for `argocd-server` and applies `root.yaml`. `bootstrap-argocd` then applies the `argocd` Application, which takes over the resources the Helm release installed, and the repository Secrets.

Not tested end to end on a fresh cluster.

---

## 3. Core Component Navigation

### 3.1 Runtime Clusters
*   [**K3han (Hybrid K3s)**](safechord.chorde.k3han.md) ⭐:
    *   **Context**: Highly asymmetric Taiwan-Japan hybrid cloud.
    *   **Status**: Running K3s v1.34+, utilizing Tailscale SDN to mask geographic latency.

---

## 4. Engineering Practices (v2)

Chorde strictly adheres to the following SRE principles:

1.  **Wrapped Upstream Charts**: Abandoned local `helm-charts/` copies. Each upstream Helm chart Chorde deploys is wrapped in `gitops/<env>/charts/<service>/`: a `Chart.yaml` naming the upstream chart as its one dependency, at an exact version, and a `values.yaml` holding Chorde's overlay under the dependency's name, with Helm's `global` beside it where a chart reads one: Helm passes any other top-level key to no chart. The service's `Application` has that directory as its one source and carries no values of its own, so the chart version and the overlay reach Argo CD at one git revision and are never rendered apart. An `Application` that names the upstream chart itself and reads its overlay from Chorde through a `ref` source renders them apart: the overlay moves with `main` as soon as the application refreshes, the version only once its parent syncs the `Application`, and in between the new overlay renders on the old chart (Chorde#77). Inlining the overlay into the `Application` as `helm.valuesObject` also keeps the two together, since the parent writes both in one update, and was set aside: it mixes how a service is deployed (destination, sync policy, wave) with what it deploys (chart version and values), which the wrapper keeps apart. No `Chart.lock` and no `charts/` is committed: Argo CD builds the dependency from `Chart.yaml`, the one place the version is written. Beside the overlay sits the chart's default values for the pinned version, as `upstream-values.yaml`, regenerated in the commit that moves the version, so a chart bump shows in its diff which defaults moved. Every image Chorde deploys is pinned as `tag@digest`: an upstream tag can be rebuilt or moved, and the digest is what the node runs and the scanner reports. An image a manifest sets is pinned in that manifest; an image a chart picks is pinned in its overlay, at the key the chart's default values show, and moves with the chart version. An operand image that an operator picks per operand version, such as the Kafka image Strimzi maps from the Kafka resource's `version`, and the Kafka exporter and Cruise Control images Strimzi defaults from the same map, is left to the operator, by tag: a digest in the operand's resource ties the operand image to the operator release, and the two sync as separate applications in no fixed order; a chart key such as Strimzi's `kafka.image.tag` maps every operand version to one image. An image that runs only now and then, such as the one a drain job uses, a hook job or a chart's test pod, or that a chart hands an operator and nothing on the cluster runs, such as Strimzi's Kafka Bridge image, takes the digest its tag resolves to when it is pinned; a k3s-upgrade Plan's image stays name-only, its `version` being the pin. A script in `scripts/test/` checks these rules, rendering each wrapper to find every image it deploys, and fails on one without a digest or on a pin whose tag is not the one the chart's version renders by default.
2.  **ApplicationSet Pattern**: Replaced monolithic `Application` manifests with `ApplicationSet` for automated service discovery and tiered synchronization (Sync Waves). A stage renders each service directory as plain manifests and nothing else: a service that a tool renders, a chart or a kustomization, keeps only its `Application` in that directory, pointing at its source, and named after the service. A kustomization of Chorde's own lives in `gitops/<env>/kustomize/<service>/`, a wrapped chart in `gitops/<env>/charts/<service>/` (item 1). A stage that sets any `directory` option on its Applications makes Argo CD render every one of them as plain manifests, a kustomization included. A script in `scripts/test/` checks that no stage directory holds a tool's source.
3.  **Operator-First**: Foundation services (DB, Kafka, Postgres) are entirely **Operator-managed**, ensuring self-healing and zero-downtime upgrades.
4.  **Availability Tiers**: Leverages Taints (`PreferNoSchedule`) to establish availability zones between on-prem and cloud nodes, preventing critical workloads from landing on non-HA nodes.
5.  **Test-Driven Ops**: Major configuration changes must be validated via scripts in `scripts/test/` to satisfy the "Test is the Law" policy.

---

## 5. Quick Access

*   **Cluster Map**: [K3han Hybrid Cluster Map](safechord.chorde.k3han.md)
*   **Scheduling Logic**: [K3han Scheduling Brain](safechord.chorde.k3han.scheduling.md)
*   **Source Code**: [SafeChord/Chorde (GitHub)](https://github.com/SafeChord/Chorde)
