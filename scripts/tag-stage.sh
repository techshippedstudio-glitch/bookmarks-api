#!/usr/bin/env bash
# Commit everything and tag the current stage of the episode.
#
# Usage:   ./scripts/tag-stage.sh <stage>
# Example: ./scripts/tag-stage.sh constitution   ->  commit "ep01: constitution" + tag ep01-constitution
#
# Stages used in episode 1, in order:
#   start init constitution spec clarify plan tasks implement converged
#
# Re-tagging an existing stage needs FORCE=1, e.g. after re-recording a take:
#   FORCE=1 ./scripts/tag-stage.sh plan

set -euo pipefail

EPISODE="${EPISODE:-ep01}"
STAGES="start init constitution spec clarify plan tasks implement converged"

stage="${1:-}"
if [[ -z "$stage" ]]; then
  echo "Usage: $0 <stage>   (one of: $STAGES)" >&2
  exit 1
fi

if [[ " $STAGES " != *" $stage "* ]]; then
  echo "Unknown stage '$stage'. Expected one of: $STAGES" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository." >&2
  exit 1
fi

tag="${EPISODE}-${stage}"

if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
  if [[ "${FORCE:-0}" != "1" ]]; then
    echo "Tag ${tag} already exists. Re-run with FORCE=1 to move it." >&2
    exit 1
  fi
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit; tagging the current commit."
else
  git commit -m "${EPISODE}: ${stage}"
fi

if [[ "${FORCE:-0}" == "1" ]]; then
  git tag -f "${tag}"
else
  git tag "${tag}"
fi

echo "Tagged ${tag} at $(git rev-parse --short HEAD)."
echo "Push with: git push origin main --tags"
