#!/bin/bash
# make_ws.sh <subject-id e.g. 004_class-IXR> <run-name>
# Creates an isolated, APFS-cloned workspace for one agent session.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC=$ROOT/pkg/PHP_Migration/UnitTest/wordPress
ID=$1; RUN=$2
NUM=${ID%%_*}
WS=$ROOT/runs/$RUN/ws/$ID
CWS=/work/runs/$RUN/ws/$ID          # same path inside the php83 container
VARIANT=opus_5_5

rm -rf "$WS"; mkdir -p "$(dirname "$WS")"
mkdir -p "$WS"; for e in "$SRC"/* "$SRC"/.[!.]*; do [ "$(basename "$e")" = build ] || cp -c -R "$e" "$WS/"; done
# Remove anything that would leak other models' outputs or paper results.
rm -rf "$WS/subjects/migrated" "$WS/build" "$WS/tools" "$WS/HARNESS.md" "$WS/collect_stats.py" \
       "$WS/rank_without_runtime.py" "$WS/scripts" "$WS/.vscode"
mkdir -p "$WS/subjects/migrated/$VARIANT" "$WS/build"
cp "$SRC"/subjects/original/*.php "$WS/subjects/migrated/$VARIANT/"

TARGET=$(cd "$WS/subjects/original" && ls ${NUM}_*.php)
TESTFILE=$(cd "$WS/tests/files" && ls ${NUM}_*Test.php)
TESTCLASS=$(grep -m1 -oE '^(final )?class [A-Za-z0-9_]+' "$WS/tests/files/$TESTFILE" | awk '{print $NF}')

mkdir -p "$WS/tools"
cat > "$WS/tools/_env" <<EOF
CWS=$CWS
TARGET=$TARGET
TESTFILE=$TESTFILE
TESTCLASS=$TESTCLASS
VARIANT=$VARIANT
EOF

cat > "$WS/tools/test" <<'EOF'
#!/bin/bash
# Run this file's PHPUnit checks against your migrated file under PHP 8.3 (E_ALL; deprecations fail).
# Extra args are passed to phpunit, e.g. tools/test --filter some_test_name
. "$(dirname "$0")/_env"
exec container exec -w "$CWS" php83 env SUBJECT_ROOT=subjects/migrated/$VARIANT SANDBOX_ROOT=build/sandboxes/agent \
  timeout 600 php vendor/bin/phpunit -c phpunit.xml --testdox --filter "/^$TESTCLASS::/" "$@"
EOF

cat > "$WS/tools/test-original" <<'EOF'
#!/bin/bash
# Run the same checks against the ORIGINAL unmodified WordPress 4.0 file (for reference).
. "$(dirname "$0")/_env"
exec container exec -w "$CWS" php83 env SUBJECT_ROOT=subjects/original SANDBOX_ROOT=build/sandboxes/original \
  timeout 600 php vendor/bin/phpunit -c phpunit.xml --testdox --filter "/^$TESTCLASS::/" "$@"
EOF

cat > "$WS/tools/lint" <<'EOF'
#!/bin/bash
# php -l on your migrated file under PHP 8.3.
. "$(dirname "$0")/_env"
exec container exec -w "$CWS" php83 php -l "subjects/migrated/$VARIANT/$TARGET"
EOF

cat > "$WS/tools/rector" <<'EOF'
#!/bin/bash
# Rector UP_TO_PHP_83 dry-run on your migrated file in isolation.
# Prints remaining PHP-version findings (Rector\Php* rules) and the diff Rector would apply.
. "$(dirname "$0")/_env"
F="$CWS/subjects/migrated/$VARIANT/$TARGET"
container exec php83 sh /work/harness/rector_isolated.sh "$F" | \
  container exec -i php83 php -r '$j=json_decode(stream_get_contents(STDIN),true);
   echo "Remaining PHP-version findings: ",count($j["rules"]),"\n"; foreach($j["rules"] as $r) echo "  - $r\n";
   if($j["error"]) echo "Rector error: ",$j["error"],"\n";'
if [ "${1:-}" = "--diff" ]; then
  container exec php83 sh -c "d=\$(mktemp -d); cp '$F' \$d/; cd /work/pkg/PHP_Migration && php vendor/bin/rector process \$d/$TARGET --dry-run --config rector.php --no-progress-bar 2>/dev/null"
fi
EOF

cat > "$WS/tools/php" <<'EOF'
#!/bin/bash
# Run PHP 8.3 CLI inside the container, with the workspace as cwd. e.g. tools/php scratch/check.php
. "$(dirname "$0")/_env"
exec container exec -w "$CWS" php83 timeout 300 php -d error_reporting=E_ALL "$@"
EOF
chmod +x "$WS"/tools/*
echo "$WS"
