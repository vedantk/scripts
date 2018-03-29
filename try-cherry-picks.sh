#!/bin/sh

abort_cherry_pick() {
  HASH=$1
  SUMMARY=$(git show $HASH --format="%h %s (Committer: %cn)" | head -n1)
  echo "Skipping $SUMMARY"
  git cherry-pick --abort || exit 1
}

for HASH in $*; do
  git cherry-pick -x $HASH &>/dev/null || abort_cherry_pick $HASH
done
