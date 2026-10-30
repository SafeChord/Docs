# Freight Issue Template

SafeZone's freight issue: the record of one release candidate, in `SafeZone-Deploy`, opened by `issueops` once the candidate's images are published (A3), one per candidate sha. Preview validates the candidate against it, and the release gate reads its sign-off ([SafeZone Delivery](../../../safechord.safezone.delivery.md)). It is not a ticket: it carries none of the ticket's sections.

- **Title**: `freight: <VERSION>-<sha7>`, the candidate's image tag. `release.yml` matches it exactly, never parsed.
- **Labels**: `freight` when opened; `validated` added by `/validate-freight` on the human's sign-off (B7). The release gate requires both.
- **Closed by** `release.yml` when it promotes the candidate (C2), or by `publish-candidate.yml` when a newer candidate supersedes it before it is validated. A validated candidate superseded before tagging is closed by hand.

```markdown
Candidate `<VERSION>-<sha7>` published. Run: <publish-candidate run URL>
Release record: SafeChord/SafeZone#<n>

## Changes in <VERSION>
<the version's section of SafeZone/CHANGELOG.md>
```

- **Release record** links the version's [release record](release-record.md); `/validate-freight` runs its entries placed on `preview` (B5). It reads `Release record: none` when the version has none.
- **Changes** is what B1 triages: whether the release only fills the deployment's parameters or changes its shape. It is the version's `CHANGELOG.md` section without its heading line, each bare `#<n>` written as `SafeChord/SafeZone#<n>` so that it does not link to this repository's issue of that number. A version with no section gets no freight issue until it has one.
- Each check's evidence is a comment: `init-deploy.yml` posts the automated result (B4), `/validate-freight` the sign-off (B7).
