# Release Record Template

The release record ticket: where Development hands a release the checks it could not run before merge, because they need a release branch or a deployment ([Delivery §3](../../../safechord.kdd.practice.delivery.md#what-development-hands-over)). It is a [ticket](../ticket.md), with what differs below.

- **Title**: `chore(release): checks held for the vX.Y.Z release`, one per milestone, in the repository the work was done (SafeZone: one per App version, in `SafeZone`, which holds a Deploy ticket's checks too).
- **Opened by** the Settler of the first ticket that defers a check to the release, at its Solidification, if none exists.
- **Lifecycle**: open until each check has a result, passed or failed with a fix ticket linked; closed once the release has run its checks (SafeZone: E2). Its Done When carries no reconciliation item, which no gate before the release ends could satisfy.

Each check is one entry in Done When:

```markdown
- [ ] **H<n> <title>** (from #<ticket>). Held: <why it could not run before merge>.
  <the check: what to do, what passes, what to record>
```

- **`H<n>`** numbers the entries in the order they are added, from `H1`. A number is never changed or reused: a dropped check is struck through, not removed. An evidence comment names an entry by it.
- **The check** is written for whoever runs it, who has the release's environments but not the ticket's context.
- A setting the deployment must align is an entry too, its check saying what to set or confirm.

The release adds two lines under an entry; neither is written when the entry is:

```markdown
  - Placed: <environment>
  - Result: passed | failed, <date>, <link to the evidence>[, fix #<ticket>]
```

- **Placed** is the one environment the entry's check runs in, written when the release places its held checks (SafeZone: `issueops`, A3). SafeZone's are `preview`, `staging` and `soak`, whose checks `/validate-freight`, `/validate-release` and `/validate-soak` run. A check the candidate's build already shows (SafeZone: A2) is not placed; its Result is written when the others are placed.
- **Result** is written by the step that ran the check, which ticks the entry with it.
