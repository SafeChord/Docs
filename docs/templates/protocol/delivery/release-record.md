# Release Record Template

The release record ticket: where Development hands a release the checks it could not run before merge, because they need a release branch or a deployment ([Delivery §3](../../../safechord.kdd.practice.delivery.md#what-development-hands-over)). It is a [ticket](../ticket.md), with what differs below.

- **Title**: `chore(release): checks held for the vX.Y.Z release`, one per milestone, in the repository the work was done.
- **Opened by** the Settler of the first ticket that defers a check to the release, at its Solidification, if none exists.
- **Lifecycle**: open until each check has a result, passed or failed with a fix ticket linked; closed once the release has run its checks (SafeZone: E2). Its Done When carries no reconciliation item, which no gate before the release ends could satisfy.

Each check is one entry:

```markdown
**From #<ticket> (<what it did>, PR #<pr>)**: <the check>, <what passes>, <what to record>. <why it could not run before merge>.
```

- Beside the check, the entry says what it needs of an environment (whether it is invasive; observed once or over days) and the requirement it guards, which sets its lifetime: a blueprint promise is kept as a probe once it passes, a one-off change ends when it passes.
- A setting the deployment must align goes on it the same way, as a deployment note.
- The entry does not say where the check runs: the release run places it.
