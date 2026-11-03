#!/bin/sh
# Contamination check: overlap between migration outputs and later WordPress releases.
# Downloads three official WordPress releases into wp_releases/ (gitignored; data only, nothing in them is executed),
# then writes runs/contamination/{per_file.csv,summary.json}.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); W=$ROOT/wp_releases
S=$ROOT/pkg/PHP_Migration/UnitTest/wordPress/subjects; R=$ROOT/runs
mkdir -p "$W"
for v in 4.9.35 6.8.12 7.1.4; do
  [ -d "$W/$v/wordpress" ] && continue
  mkdir -p "$W/$v"; curl -sL "https://wordpress.org/wordpress-$v.tar.gz" | tar -xz -C "$W/$v"
done
python3 -I "$ROOT/harness/contamination.py" --originals "$S/original" --file-map "$S/../config/file-map.php" \
  --release 4.9.35="$W/4.9.35/wordpress" --release 6.8.12="$W/6.8.12/wordpress" --release 7.1.4="$W/7.1.4/wordpress" \
  --approach "opus55_agent=$R/opus55/out/{id}/migrated.php" \
  --approach "opus55_oneshot=$R/opus55_oneshot/out/{id}/migrated.php" \
  --approach "sonnet4=$S/migrated/claude_sonnet_4_20250514/{id}.php" \
  --approach "rector=$S/migrated/Rector_Baseline/{id}.php" \
  --approach "gpt5_codex=$S/migrated/gpt_5_codex/{id}.php" \
  --approach "gemini25pro=$S/migrated/gemini_2_5_pro/{id}.php" \
  --out "$R/contamination"
