# Release Issue Template

SafeZone's release issue: the record of one release on staging, in `SafeZone-Deploy`, opened by `issueops` once `release.yml` has promoted the tag's images (C3). Phases D and E post their evidence on it ([SafeZone Delivery](../../../safechord.safezone.delivery.md)). It is not a ticket: it carries none of the ticket's sections, and it is not the [release record](release-record.md).

- **Title**: `release: v<VERSION>`.
- **Labels**: `release` when opened; `soaking` added by `/validate-release` on the human's yes (D8), which starts the soak.
- **Closed by** the archive PR's `Closes #<n>` (E4), or by hand as `superseded-by v0.X.(Y+1)` when a patch release replaces it during the soak.

```markdown
Images `:<VERSION>` promoted from `<VERSION>-<sha7>`, digest-identical. Run: <release.yml run URL>
Release record: SafeChord/SafeZone#<n>
```

- **Release record** is written as on the [freight issue](freight.md); `/validate-release` runs its entries placed on `staging` (D6), `/validate-soak` those on `soak` (E1).
- Each check's evidence is a comment: `/validate-release` posts staging's (D8), `/validate-soak` the soak's (E1). The soak starts when the `soaking` label is added; `/validate-soak` reads the window from it.
