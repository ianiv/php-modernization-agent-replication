#!/bin/bash
# run_one.sh <subject-id> <run-name>
# One Claude Code (Opus 5.5) agent session for one file. Writes runs/<run>/out/<id>/{result.json,agent.json,migrated.php}
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ID=$1; RUN=$2
OUT=$ROOT/runs/$RUN/out/$ID
mkdir -p "$OUT"
if [ -f "$OUT/agent.json" ]; then echo "skip $ID (done)"; exit 0; fi

WS=$("$ROOT/harness/make_ws.sh" "$ID" "$RUN") || { echo "ws failed $ID"; exit 1; }
. "$WS/tools/_env"
# WordPress path for the prompt. History: the first batch used an unanchored grep, which also matched the example
# comments in file-map.php and broke prompt construction for 003 and 008; it was anchored (below) before those two
# were re-run. Known bug, kept so the script regenerates the shipped prompts: from 013 on most file-map keys end in
# ".php" ('013_file.php') while subject IDs do not ('013_file'), so this exact-key match returns nothing and 85 of 100
# shipped prompts say "It is the WordPress file ``." A future run should also match "'$ID.php'".
WPPATH=$(grep -E "^[[:space:]]*'$ID'" "$WS/config/file-map.php" | head -1 | sed -E "s/.*=> '([^']+)'.*/\1/")
PROMPT=$(sed -e "s|{{TARGET}}|$TARGET|g" -e "s|{{TESTFILE}}|$TESTFILE|g" -e "s|{{WPPATH}}|$WPPATH|g" "$ROOT/harness/task_prompt.md")
echo "$PROMPT" > "$OUT/prompt.md"

START=$(date +%s)
( cd "$WS" && claude -p "$PROMPT" \
    --model claude-opus-5-5 \
    --setting-sources project \
    --strict-mcp-config \
    --no-session-persistence \
    --output-format json \
    --permission-mode dontAsk \
    --allowedTools "Read" "Edit" "Write" "Glob" "Grep" \
       "Bash(tools/*)" "Bash(./tools/*)" "Bash(ls *)" "Bash(cat *)" "Bash(diff *)" "Bash(grep *)" \
       "Bash(head *)" "Bash(tail *)" "Bash(wc *)" "Bash(sed -n *)" "Bash(mkdir scratch*)" \
    --disallowedTools "WebFetch" "WebSearch" "Bash(curl *)" "Bash(wget *)" \
  ) > "$OUT/agent.json.tmp" 2> "$OUT/agent.stderr"
RC=$?
END=$(date +%s)
mv "$OUT/agent.json.tmp" "$OUT/agent.json"
cp "$WS/subjects/migrated/$VARIANT/$TARGET" "$OUT/migrated.php"
# Record any edits the agent made outside its file (should be none).
diff -rq "$ROOT/pkg/PHP_Migration/UnitTest/wordPress/tests" "$WS/tests" > "$OUT/tamper.txt" 2>&1
diff -rq "$ROOT/pkg/PHP_Migration/UnitTest/wordPress/config" "$WS/config" >> "$OUT/tamper.txt" 2>&1
for f in "$ROOT"/pkg/PHP_Migration/UnitTest/wordPress/subjects/original/*.php; do
  b=$(basename "$f"); [ "$b" = "$TARGET" ] && continue
  cmp -s "$f" "$WS/subjects/migrated/$VARIANT/$b" || echo "other subject changed: $b" >> "$OUT/tamper.txt"
done
python3 -I -c "
import json,sys
d=json.load(open(sys.argv[1]))
print(json.dumps({'id':sys.argv[2],'rc':int(sys.argv[3]),'seconds':int(sys.argv[4]),'is_error':d.get('is_error'),
 'turns':d.get('num_turns'),'cost_usd':d.get('total_cost_usd'),'usage':d.get('usage')}))" "$OUT/agent.json" "$ID" "$RC" "$((END-START))" > "$OUT/result.json" 2>/dev/null \
  || echo "{\"id\":\"$ID\",\"rc\":$RC,\"parse_error\":true}" > "$OUT/result.json"
rm -rf "$WS/build/sandboxes"
echo "done $ID rc=$RC $(cat "$OUT/result.json")"
