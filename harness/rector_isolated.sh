#!/bin/sh
# Usage (inside container): rector_isolated.sh <php-file> [<php-file>...]
# Runs Rector UP_TO_PHP_83 dry-run on each file in isolation (single-file condition, as in the paper)
# and prints one JSON line per file: {"file":..., "rules":[...Php* rules...], "error":...}
RECTOR=/work/pkg/PHP_Migration
for f in "$@"; do
  d=$(mktemp -d); cp "$f" "$d/"; b=$(basename "$f")
  # Rector's JSON goes through a file, not argv: very large diffs exceed the argument-length limit.
  (cd "$RECTOR" && php vendor/bin/rector process "$d/$b" --dry-run --config rector.php --output-format=json --no-progress-bar 2>/dev/null) > "$d/out.json"
  php -r '$f=$argv[1];$j=json_decode(file_get_contents($argv[2]),true);$r=[];$e=null;
    if(!$j){$e="rector_failed";}else{foreach(($j["file_diffs"]??[]) as $fd){foreach($fd["applied_rectors"] as $x){if(strpos($x,"Rector\\Php")===0)$r[$x]=1;}} if(!empty($j["errors"]))$e=$j["errors"][0]["message"]??"error";}
    echo json_encode(["file"=>$f,"rules"=>array_keys($r),"error"=>$e]),"\n";' "$f" "$d/out.json"
  rm -rf "$d"
done
