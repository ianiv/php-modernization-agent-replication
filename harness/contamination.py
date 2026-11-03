#!/usr/bin/env python3
"""Training-data contamination check for WordPress 4.0 -> PHP 8.x migration outputs.

Question: do migration outputs contain code that WordPress itself later wrote
(i.e. lines that exist in a later upstream release but not in the 4.0 original)?

For each subject file and each approach:
  added      = output lines (normalized, filtered) whose normalized form does not
               occur anywhere in the normalized original
  hit        = added lines whose normalized form occurs in the upstream file(s)
  overlap    = hit / added                      ("share of added lines found upstream")
  recall     = |distinct(added) & U| / |U|, U = distinct upstream lines not in original
  sim_out    = difflib ratio(output lines, upstream lines)
  sim_orig   = difflib ratio(original lines, upstream lines);  sim_gain = sim_out - sim_orig

Two normalizations are computed:
  ws   : strip + collapse runs of whitespace to one space
  nows : remove all whitespace (robust to WordPress Coding Standards reformatting,
         e.g. `foo( $a )` vs `foo($a)`); this is the primary metric.
Filter (applied to output, original and upstream alike): drop blank lines,
lines whose nows form is < MIN_LEN chars, and comment-only lines
(starting with //, #, /*, *, */). Matching is set membership per file.

Usage (all paths are arguments; downloads are only read, never executed):
  python3 -I contamination.py --originals DIR --file-map FILE \
     --release 4.9.35=DIR/wordpress --release 6.8.12=DIR/wordpress \
     --approach opus55_agent=/path/out/{id}/migrated.php \
     --approach rector=/path/Rector_Baseline/{id}.php  --out OUTDIR
"""
import argparse
import csv
import difflib
import json
import os
import re
import statistics
import sys

MIN_LEN = 15

# Files that WordPress moved/split after 4.0. Each entry is a list of
# candidate file groups; the first group whose files all exist in a release is
# used (concatenated in this order, which follows the class order of the 4.0
# file). If none exists the mapped path from file-map.php is used.
IXR = ["value", "message", "server", "request", "client", "error", "date",
       "base64", "introspectionserver", "clientmulticall"]
RELOCATIONS = {
    "004_class-IXR": [["wp-includes/IXR/class-IXR-%s.php" % c for c in IXR]],
    "003_wp-db": [["wp-includes/class-wpdb.php"]],
    "025_widgets": [["wp-admin/widgets.php", "wp-admin/widgets-form.php"]],
    "038_class.wp-styles": [["wp-includes/class-wp-styles.php"]],
    "061_class.wp-scripts": [["wp-includes/class-wp-scripts.php"]],
    "050_class-oembed": [["wp-includes/class-wp-oembed.php"]],
    "066_class.wp-dependencies": [["wp-includes/class-wp-dependencies.php",
                                   "wp-includes/class-wp-dependency.php"]],
    "064_wp-diff": [["wp-includes/class-wp-text-diff-renderer-table.php",
                     "wp-includes/class-wp-text-diff-renderer-inline.php"]],
    "039_class-wp-upgrader-skins": [[
        "wp-admin/includes/class-%s.php" % c for c in [
            "wp-upgrader-skin", "plugin-upgrader-skin", "theme-upgrader-skin",
            "bulk-upgrader-skin", "bulk-plugin-upgrader-skin",
            "bulk-theme-upgrader-skin", "plugin-installer-skin",
            "theme-installer-skin", "language-pack-upgrader-skin",
            "automatic-upgrader-skin", "wp-ajax-upgrader-skin"]]],
}
# Upstream files that became deprecation stubs / plugin redirects: treat as missing.
REMOVED = {"017_press-this": "moved to Press This plugin in 4.9; core file is a stub",
           "078_media": "replaced by a redirect stub (deprecated) in 5.x+"}
STUB_FRACTION = 0.25  # upstream (after relocation) smaller than this * original => stub


def simplepie_reloc(path):
    m = re.match(r"wp-includes/SimplePie/(\w+)\.php$", path)
    return [["wp-includes/SimplePie/src/%s.php" % m.group(1)]] if m else []


COMMENT_RE = re.compile(r"^(//|#|/\*|\*/|\*)")


def norm_ws(line):
    return " ".join(line.split())


def norm_nows(line):
    return "".join(line.split())


def lines_of(text, mode):
    out = []
    for raw in text.splitlines():
        s = norm_ws(raw)
        if not s or COMMENT_RE.match(s):
            continue
        key = norm_nows(s)
        if len(key) < MIN_LEN:
            continue
        out.append(key if mode == "nows" else s)
    return out


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_file_map(path):
    text = read(path)
    m = {}
    for line in text.splitlines():
        if line.strip().startswith("//"):
            continue
        mm = re.match(r"\s*'([^']+)'\s*=>\s*'([^']+)'", line)
        if mm:
            m[re.sub(r"\.php$", "", mm.group(1))] = mm.group(2)
    return m


def resolve_upstream(sid, mapped, root, orig_len):
    """Return (list_of_paths, status)."""
    if sid in REMOVED:
        p = os.path.join(root, mapped)
        if not os.path.isfile(p) or len(read(p).splitlines()) < STUB_FRACTION * orig_len:
            return [], "removed"
    groups = RELOCATIONS.get(sid, []) + simplepie_reloc(mapped)
    for g in groups:
        ps = [os.path.join(root, x) for x in g]
        if all(os.path.isfile(p) for p in ps):
            same = (len(g) == 1 and g[0] == mapped)
            return ps, ("same_path" if same else "relocated")
    p = os.path.join(root, mapped)
    if os.path.isfile(p):
        if len(read(p).splitlines()) < STUB_FRACTION * orig_len:
            return [p], "stub"
        return [p], "same_path"
    return [], "missing"


def reduce_trivial(key, mode):
    """Strip edits that WPCS/upstream style forces and that are not code reuse:
    leading visibility/static/final/var modifiers and a trailing '{' (brace added
    to a brace-less if/else/foreach, or brace moved onto the declaration line)."""
    k = key if mode == "nows" else norm_nows(key)
    k = re.sub(r"^(?:(?:final|abstract|public|private|protected|static|var)(?=[$a-z&]))+", "", k)
    if k.endswith("{"):
        k = k[:-1]
    return k


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def analyse(out_text, orig_text, up_text, mode):
    o = lines_of(out_text, mode)
    g = lines_of(orig_text, mode)
    u = lines_of(up_text, mode)
    gs, us = set(g), set(u)
    added = [x for x in o if x not in gs]
    hits = [x for x in added if x in us]
    U = us - gs
    rec = len(set(added) & U) / len(U) if U else None
    gred = {reduce_trivial(x, mode) for x in g}
    resid = [x for x in hits if reduce_trivial(x, mode) not in gred]
    return {
        "added": len(added), "hits": len(hits),
        "overlap": (len(hits) / len(added)) if added else None,
        "upstream_new": len(U), "recall": rec,
        "resid_hits": len(resid),
        "resid_overlap": (len(resid) / len(added)) if added else None,
        "sim_out": ratio(o, u), "sim_orig": ratio(g, u),
    }, set(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", required=True)
    ap.add_argument("--file-map", required=True)
    ap.add_argument("--release", action="append", required=True, help="NAME=DIR")
    ap.add_argument("--approach", action="append", required=True,
                    help="NAME=PATTERN with {id} (id = original filename stem)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--modes", default="nows,ws")
    a = ap.parse_args()

    fmap = parse_file_map(a.file_map)
    releases = [r.split("=", 1) for r in a.release]
    approaches = [x.split("=", 1) for x in a.approach]
    modes = a.modes.split(",")
    ids = sorted(f[:-4] for f in os.listdir(a.originals) if f.endswith(".php"))

    rows, hitsets = [], {}
    for sid in ids:
        orig = read(os.path.join(a.originals, sid + ".php"))
        mapped = fmap.get(sid)
        for rel, root in releases:
            paths, status = resolve_upstream(sid, mapped, root, len(orig.splitlines())) if mapped else ([], "unmapped")
            up = "\n".join(read(p) for p in paths) if status in ("same_path", "relocated") else None
            for name, pat in approaches:
                op = pat.replace("{id}", sid)
                base = {"id": sid, "release": rel, "approach": name, "status": status,
                        "upstream": ";".join(os.path.relpath(p, root) for p in paths)}
                if up is None or not os.path.isfile(op):
                    base["note"] = "no upstream" if up is None else "no output"
                    rows.append(base)
                    continue
                outt = read(op)
                for mode in modes:
                    r, hs = analyse(outt, orig, up, mode)
                    hitsets[(sid, rel, name, mode)] = hs
                    for k, v in r.items():
                        base["%s_%s" % (mode, k)] = v
                    base["%s_sim_gain" % mode] = r["sim_out"] - r["sim_orig"]
                rows.append(base)

    os.makedirs(a.out, exist_ok=True)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(a.out, "per_file.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    summary = {"params": {"min_len": MIN_LEN, "modes": modes,
                          "releases": dict(releases), "approaches": dict(approaches)},
               "coverage": {}, "aggregate": {}, "notable": {}}
    for rel, _ in releases:
        st = {}
        for r in rows:
            if r["release"] == rel and r["approach"] == approaches[0][0]:
                st[r["status"]] = st.get(r["status"], 0) + 1
        summary["coverage"][rel] = st
    for mode in modes:
        for rel, _ in releases:
            for name, _ in approaches:
                rs = [r for r in rows if r["release"] == rel and r["approach"] == name
                      and ("%s_added" % mode) in r]
                ad = sum(r["%s_added" % mode] for r in rs)
                ht = sum(r["%s_hits" % mode] for r in rs)
                rh = sum(r["%s_resid_hits" % mode] for r in rs)
                ro = [r["%s_resid_overlap" % mode] for r in rs if r["%s_resid_overlap" % mode] is not None]
                ov = [r["%s_overlap" % mode] for r in rs if r["%s_overlap" % mode] is not None]
                rc = [r["%s_recall" % mode] for r in rs if r["%s_recall" % mode] is not None]
                gain = [r["%s_sim_gain" % mode] for r in rs]
                so = [r["%s_sim_out" % mode] for r in rs]
                sg = [r["%s_sim_orig" % mode] for r in rs]
                summary["aggregate"]["%s|%s|%s" % (mode, rel, name)] = {
                    "files": len(rs), "added": ad, "hits": ht,
                    "micro_overlap": ht / ad if ad else None,
                    "median_overlap": statistics.median(ov) if ov else None,
                    "mean_overlap": statistics.mean(ov) if ov else None,
                    "resid_hits": rh, "micro_resid_overlap": rh / ad if ad else None,
                    "median_resid_overlap": statistics.median(ro) if ro else None,
                    "median_recall": statistics.median(rc) if rc else None,
                    "mean_sim_out": statistics.mean(so) if so else None,
                    "mean_sim_orig": statistics.mean(sg) if sg else None,
                    "median_sim_gain": statistics.median(gain) if gain else None,
                }
    # Notable files: Opus residual overlap minus the best of the controls.
    names = [n for n, _ in approaches]
    controls = [n for n in names if n in ("rector", "sonnet4")]
    tests = [n for n in names if n.startswith("opus")]
    idx = {(r["id"], r["release"], r["approach"]): r for r in rows if "nows_added" in r}
    for rel, _ in releases:
        lst = []
        for sid in ids:
            ctl = [idx[(sid, rel, c)]["nows_resid_overlap"] or 0.0 for c in controls if (sid, rel, c) in idx]
            for t in tests:
                r = idx.get((sid, rel, t))
                if not r or r["nows_added"] < 5 or not ctl:
                    continue
                lst.append({"id": sid, "approach": t, "added": r["nows_added"],
                            "resid_hits": r["nows_resid_hits"],
                            "resid_overlap": r["nows_resid_overlap"],
                            "max_control_resid_overlap": max(ctl),
                            "excess": (r["nows_resid_overlap"] or 0.0) - max(ctl)})
        lst.sort(key=lambda x: -x["excess"])
        summary["notable"][rel] = lst[:15]
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print("wrote", len(rows), "rows")


if __name__ == "__main__":
    sys.exit(main())
