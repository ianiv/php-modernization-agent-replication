"""Compute the paper's behavioural + resolution metrics for one scored run."""
import argparse, csv, json, os, re, sys, xml.etree.ElementTree as ET
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--orig-junit", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "original_baseline", "junit.xml"))
ap.add_argument("--orig-testdox")
ap.add_argument("--junit", required=True)
ap.add_argument("--orig-rector", required=True)
ap.add_argument("--rector", required=True)
ap.add_argument("--paper-summary")
ap.add_argument("--out", required=True)
a = ap.parse_args()


def load_junit(path):
    res = {}
    for tc in ET.parse(path).iter("testcase"):
        f = os.path.basename(tc.get("file", ""))
        m = re.match(r"(\d{3})_", f)
        fid = m.group(1) if m else "smoke"
        ok = not any(ch.tag in ("failure", "error", "skipped") for ch in tc)
        res[(fid, tc.get("class"), tc.get("name"))] = ok
    return res


orig = load_junit(a.orig_junit)
new = load_junit(a.junit)
keys = [k for k in orig if k[0] != "smoke"]
missing = [k for k in keys if k not in new]

trans = defaultdict(int)
per_file = defaultdict(lambda: {"checks": 0, "orig_pass": 0, "new_pass": 0, "regress": 0, "repair": 0})
for k in keys:
    o, n = orig[k], new.get(k, False)
    pf = per_file[k[0]]
    pf["checks"] += 1; pf["orig_pass"] += o; pf["new_pass"] += n
    if o and n: trans["preserved"] += 1
    elif o and not n: trans["regression"] += 1; pf["regress"] += 1
    elif not o and n: trans["repair"] += 1; pf["repair"] += 1
    else: trans["unrepaired"] += 1

orig_pass = sum(orig[k] for k in keys)
orig_fail = len(keys) - orig_pass
new_pass = sum(new.get(k, False) for k in keys)
compat = sum(1 for p in per_file.values() if p["new_pass"] == p["checks"])
orig_compat = sum(1 for p in per_file.values() if p["orig_pass"] == p["checks"])
broken = sum(1 for p in per_file.values() if p["orig_pass"] == p["checks"] and p["new_pass"] < p["checks"])
fixed = sum(1 for p in per_file.values() if p["orig_pass"] < p["checks"] and p["new_pass"] == p["checks"])

# Rector resolution (single-file isolation, Rector\Php* rules only, as in the paper)
meta = json.load(open(a.orig_rector))
orig_rules = {f["filename"][:3]: {x for x in f["rector_analysis"]["rules_triggered"] if x.startswith("Rector\\Php")} for f in meta["files"]}
new_rules, rector_err = {}, {}
for line in open(a.rector):
    j = json.loads(line)
    fid = os.path.basename(j["file"])[:3]
    new_rules[fid] = set(j["rules"]); rector_err[fid] = j["error"]
findings = sum(map(len, orig_rules.values()))
resolved = introduced = 0
rows = []
for fid in sorted(per_file):
    o = orig_rules.get(fid, set()); n = new_rules.get(fid, set())
    if fid not in new_rules:  # no Rector result for this file => treat like unparseable, nothing resolved
        print(f"warning: no Rector result for file {fid}; counting none of its {len(o)} findings as resolved", file=sys.stderr)
        r, intro, remaining = 0, 0, sorted(o)
    elif rector_err.get(fid):  # unparseable => nothing counts as resolved
        r, intro, remaining = 0, 0, sorted(o)
    else:
        r, intro, remaining = len(o - n), len(n - o), sorted(n)
    resolved += r; introduced += intro
    p = per_file[fid]
    rows.append({"file": fid, **p, "compatible": p["new_pass"] == p["checks"],
                 "rector_orig": len(o), "rector_resolved": r, "rector_introduced": intro,
                 "rector_remaining": ";".join(x.split("\\")[-1] for x in remaining),
                 "rector_error": rector_err.get(fid) or ""})

summary = {
    "checks_total": len(keys), "checks_missing_from_run": len(missing),
    "checks_passed": new_pass, "orig_checks_passed": orig_pass,
    "compatible_files": compat, "orig_compatible_files": orig_compat,
    "broken_files": broken, "fixed_files": fixed,
    "preserved": trans["preserved"], "regressions": trans["regression"],
    "repairs": trans["repair"], "unrepaired": trans["unrepaired"],
    "preservation_rate": round(100 * trans["preserved"] / orig_pass, 1),
    "repair_rate": round(100 * trans["repair"] / orig_fail, 1),
    "rector_findings": findings, "rector_resolved": resolved,
    "rector_resolution_rate": round(100 * resolved / findings, 1),
    "rector_introduced": introduced,
    "files_fully_done": sum(1 for r in rows if r["compatible"] and not r["rector_remaining"]),
}
os.makedirs(a.out, exist_ok=True)
json.dump(summary, open(os.path.join(a.out, "summary.json"), "w"), indent=2)
with open(os.path.join(a.out, "per_file.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(json.dumps(summary, indent=2))
