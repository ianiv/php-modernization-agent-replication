#!/bin/bash
# score.sh <run-name>
# Scores runs/<run>/out/*/migrated.php against a PRISTINE copy of the paper's harness
# (agent edits to tests/stubs are never used). Files without an output fall back to the original.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN=$1
SRC=$ROOT/pkg/PHP_Migration/UnitTest/wordPress
SC=$ROOT/runs/$RUN/score
rm -rf "$SC"; mkdir -p "$SC"
mkdir -p "$SC/harness"; for e in "$SRC"/* "$SRC"/.[!.]*; do [ "$(basename "$e")" = build ] || cp -c -R "$e" "$SC/harness/"; done
rm -rf "$SC/harness/build"; mkdir -p "$SC/harness/build"
M=$SC/harness/subjects/migrated/opus_5_5
rm -rf "$M"; mkdir -p "$M"
cp "$SRC"/subjects/original/*.php "$M/"
n=0
for d in "$ROOT"/runs/$RUN/out/*/; do
  id=$(basename "$d"); [ -f "$d/migrated.php" ] || continue
  cp "$d/migrated.php" "$M/$id.php"; n=$((n+1))
done
echo "scoring $n agent outputs"
C=/work/runs/$RUN/score/harness
container exec -w "$C" php83 env SUBJECT_ROOT=subjects/migrated/opus_5_5 SANDBOX_ROOT=build/sandboxes/opus_5_5 \
  timeout 3600 php vendor/bin/phpunit -c phpunit.xml --log-junit build/junit.xml --testdox-text build/testdox.txt > "$SC/phpunit.log" 2>&1 || true
tail -1 "$SC/phpunit.log"
container exec php83 sh -c "sh /work/harness/rector_isolated.sh $C/subjects/migrated/opus_5_5/*.php" > "$SC/rector.jsonl"
python3 -I "$ROOT/harness/metrics.py" \
  --orig-testdox "$ROOT/pkg/OriginalTestResults.txt" \
  --junit "$SC/harness/build/junit.xml" \
  --orig-rector "$ROOT/pkg/PHP_Migration/dataset/wordpress/rector_reports_selected_100_files/metadata.json" \
  --rector "$SC/rector.jsonl" \
  --paper-summary "$ROOT/pkg/results_summary/runtime/analysis/summary.csv" \
  --out "$SC"

rm -rf "$SC/harness/build/sandboxes"
