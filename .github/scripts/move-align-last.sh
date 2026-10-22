#!/usr/bin/env bash
# Move align/last after an incremental alignment PR merges.
#
#   move-align-last.sh <head branch>
#
# The incremental alignment skill names a default-range run's branch docs/align-<S>, S being the
# commit the run started from; a run over a range given by hand is docs/align-range-<S> and moves
# nothing. The tag goes to S, not to the merge commit: commits that reached main while the PR was
# open have not been checked. A tag already at or past S stays where it is.
# Run in a full clone (fetch-depth: 0) whose origin it can push to.

set -euo pipefail

BRANCH="${1:?usage: move-align-last.sh <head branch>}"

if [[ ! "$BRANCH" =~ ^docs/align-([0-9a-f]{7,40})$ ]]; then
  echo "$BRANCH is not a default-range alignment branch; align/last stays."
  exit 0
fi
S="$(git rev-parse --verify "${BASH_REMATCH[1]}^{commit}")"

if git rev-parse -q --verify refs/tags/align/last >/dev/null &&
   git merge-base --is-ancestor "$S" refs/tags/align/last; then
  echo "align/last ($(git rev-parse --short refs/tags/align/last)) is already at or past $S; it stays."
  exit 0
fi

git tag -f align/last "$S"
git push --force origin refs/tags/align/last
echo "align/last moved to $S."
