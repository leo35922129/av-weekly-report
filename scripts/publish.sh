#!/usr/bin/env bash
# Publish the site to GitHub Pages: https://leo35922129.github.io/av-weekly-report/
# Usage: scripts/publish.sh "commit message"
# Only ever touches the av-weekly-report repo (never drive-cgkhjethh2yxwgilcfmz).
set -euo pipefail
OWNER=leo35922129; REPO=av-weekly-report
[ "$REPO" = "drive-cgkhjethh2yxwgilcfmz" ] && { echo "refusing"; exit 1; }
cd "$(dirname "$0")/.."
touch .nojekyll
[ -d .git ] || { git init -q -b main; git remote add origin "https://github.com/$OWNER/$REPO.git"; }
gh repo view "$OWNER/$REPO" >/dev/null 2>&1 || gh repo create "$OWNER/$REPO" --public --description "Autonomy Weekly: AV, automotive AI & SDV report"
git add -A && git -c user.name="$OWNER" -c user.email="$OWNER@users.noreply.github.com" commit -qm "${1:-Weekly report update}" || true
gh auth setup-git >/dev/null 2>&1 || true
git push -q -u origin main
gh api "repos/$OWNER/$REPO/pages" >/dev/null 2>&1 || gh api -X POST "repos/$OWNER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null
echo "Live (may take ~1 min): https://$OWNER.github.io/$REPO/"
