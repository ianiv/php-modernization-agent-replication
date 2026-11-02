#!/bin/bash
# run_all.sh <run-name> [parallelism]  — runs every subject not yet done
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN=$1; P=${2:-6}
ls "$ROOT"/pkg/PHP_Migration/UnitTest/wordPress/subjects/original/*.php | xargs -n1 basename | sed 's/\.php$//' | \
  xargs -P "$P" -I{} "$ROOT/harness/run_one.sh" {} "$RUN"
echo ALL_DONE
