"""Re-analysis requested in peer review: resolution by necessity, required/no-required file split,
the original study's two sensitivity analyses, and exact McNemar tests with bootstrap intervals.

The original package does not ship its rule-to-necessity mapping (its TeX notes it as incomplete), so
NECESSITY below is reconstructed from the paper's definitions (Sec. III-D). It reproduces the published
group sizes (37 / 85 / 389) exactly; the script also prints Table IV for the five original models as a check.

Usage: python3 -I harness/reanalysis.py   (needs pkg/ from setup.sh and runs/necessity_validation/)
Writes runs/reanalysis/{summary.json,necessity_mapping.csv}.
"""
import csv, json, math, os, random, re, xml.etree.ElementTree as ET
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "pkg", "PHP_Migration")
WP = os.path.join(PKG, "UnitTest", "wordPress")
VAL = os.path.join(ROOT, "runs", "necessity_validation")
OUT = os.path.join(ROOT, "runs", "reanalysis")
os.makedirs(OUT, exist_ok=True)

# Required: construct fails or changes behaviour under PHP 8.3. Deprecated: runs but raises a notice/warning.
REQUIRED = {"CurlyToSquareBracketArrayStringRector", "Php4ConstructorRector", "EregToPregMatchRector",
            "CreateFunctionToAnonymousFunctionRector", "WhileEachToForeachRector",
            "BreakNotInLoopOrSwitchToReturnRector", "StringifyStrNeedlesRector", "AssignArrayToStringRector",
            "WrapVariableVariableNameInCurlyBracesRector", "StringsAssertNakedRector",
            "SensitiveConstantNameRector", "StringifyDefineRector", "RemoveExtraParametersRector"}
DEPRECATED = {"NullToStrictStringFuncCallArgRector", "Utf8DecodeEncodeToMbConvertEncodingRector",
              "FinalPrivateToPrivateVisibilityRector"}


def group(rule):
    r = rule.split("\\")[-1]
    return "required" if r in REQUIRED else "deprecated" if r in DEPRECATED else "optional"


def fid_of(path):
    m = re.match(r"(\d{3})_", re.split(r"[\\/]", path or "")[-1])
    return m.group(1) if m else None


meta = json.load(open(os.path.join(PKG, "dataset/wordpress/rector_reports_selected_100_files/metadata.json")))
ORIG = {f["filename"][:3]: {x for x in f["rector_analysis"]["rules_triggered"] if x.startswith("Rector\\Php")}
        for f in meta["files"]}
N = Counter(group(r) for s in ORIG.values() for r in s)
with open(os.path.join(OUT, "necessity_mapping.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["rule", "group", "findings"])
    for r, c in Counter(r for s in ORIG.values() for r in s).most_common():
        w.writerow([r, group(r), c])


def load_rector(path):
    rules, err = {}, {}
    for line in open(path):
        j = json.loads(line); f = fid_of(j["file"])
        rules[f] = set(j["rules"]); err[f] = j["error"]
    return rules, err


def load_junit(path):
    res = {}
    for tc in ET.parse(path).iter("testcase"):
        f = fid_of(tc.get("file", ""))
        if f is None: continue
        res[(f, tc.get("class"), tc.get("name"))] = not any(ch.tag in ("failure", "error", "skipped") for ch in tc)
    return res


def lint_fail(path):
    return {fid_of(l.split()[0]) for l in open(path) if l.split()[-1] == "FAIL"}


orig_j = load_junit(os.path.join(ROOT, "runs/original_baseline/junit.xml"))
KEYS = sorted(orig_j)
assert len(KEYS) == 630, len(KEYS)
FP = {k for k in KEYS if "semantic" in k[2].lower() or "fingerprint" in k[2].lower()}
FILES = sorted({k[0] for k in KEYS})
HAS_REQ = {f for f in FILES if any(group(r) == "required" for r in ORIG.get(f, ()))}

A = os.path.join(WP, "tools", "archive")
APPROACHES = {
    "Claude Sonnet 4": (f"{A}/claude_sonnet_4_20250514/junit.xml", f"{ROOT}/runs/sonnet_replay/score/rector.jsonl", "claude_sonnet_4_20250514"),
    "Gemini 2.5 Flash": (f"{A}/gemini_2_5_flash/junit.xml", f"{VAL}/gemini_2_5_flash.jsonl", "gemini_2_5_flash"),
    "Gemini 2.5 Pro": (f"{A}/gemini_2_5_pro/junit.xml", f"{VAL}/gemini_2_5_pro.jsonl", "gemini_2_5_pro"),
    "GPT-5 Codex": (f"{A}/gpt_5_codex/junit.xml", f"{VAL}/gpt_5_codex.jsonl", "gpt_5_codex"),
    "Llama 3.3 70B": (f"{A}/meta_llama_llama_3_3_70b_instruct/junit.xml", f"{VAL}/meta_llama_llama_3_3_70b_instruct.jsonl", "meta_llama_llama_3_3_70b_instruct"),
    "Rector": (f"{ROOT}/runs/rector_replay/score/junit.xml", None, "Rector_Baseline"),  # archived Rector junit is stale; re-scored
    "Opus 5.5 single-shot": (f"{ROOT}/runs/opus55_oneshot/score/junit.xml", f"{ROOT}/runs/opus55_oneshot/score/rector.jsonl", "opus55_oneshot"),
    "Opus 5.5 single-shot (strict)": (f"{ROOT}/runs/opus55_oneshot/score/junit.xml", f"{ROOT}/runs/opus55_oneshot/score/rector.jsonl", "opus55_oneshot"),
    "Opus 5.5 agent": (f"{ROOT}/runs/opus55/score/junit.xml", f"{ROOT}/runs/opus55/score/rector.jsonl", "opus55"),
}


def compatible(res, keys=KEYS):
    by = defaultdict(list)
    for k in keys: by[k[0]].append(res.get(k, False))
    return {f: all(v) for f, v in by.items()}


ORIG_C = compatible(orig_j)
ORIG_C_NOFP = compatible(orig_j, [k for k in KEYS if k not in FP])


def exact_mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def boot_ci(x, y, reps=10000, seed=42):
    rng = random.Random(seed); n = len(FILES); d = []
    for _ in range(reps):
        s = [FILES[rng.randrange(n)] for _ in range(n)]
        d.append(sum(x[f] for f in s) - sum(y[f] for f in s))
    d.sort()
    return d[int(0.025 * reps)], d[int(0.975 * reps) - 1]


out = {"group_sizes": dict(N), "fingerprint_checks": len(FP), "files_with_required": len(HAS_REQ),
       "files_with_required_compatible_unchanged": sum(ORIG_C[f] for f in HAS_REQ), "approaches": {}}
COMPAT = {"Unchanged originals": ORIG_C}
for name, (junit, rector, lintkey) in APPROACHES.items():
    j = load_junit(junit)
    if name.endswith("(strict)"):  # file 014's response exceeded the study's 64k-token/600 s limits: count it as failed
        j = {k: (False if k[0] == "014" else v) for k, v in j.items()}
    c = compatible(j)
    COMPAT[name] = c
    nofp = compatible(j, [k for k in KEYS if k not in FP])
    lf = lint_fail(os.path.join(VAL, "lint", f"{lintkey}.txt"))
    fb = {k: (orig_j[k] if k[0] in lf else j.get(k, False)) for k in KEYS}
    row = {"compatible": sum(c.values()), "compatible_no_fp": sum(nofp.values()),
           "compatible_lint_fallback": sum(compatible(fb).values()), "lint_failures": len(lf)}
    for lbl, fs in (("req", HAS_REQ), ("noreq", set(FILES) - HAS_REQ)):
        row[f"broken_{lbl}"] = sum(1 for f in fs if ORIG_C[f] and not c[f])
        row[f"fixed_{lbl}"] = sum(1 for f in fs if not ORIG_C[f] and c[f])
    if rector:
        rules, err = load_rector(rector)
        res = Counter(); intro = 0
        for f, o in ORIG.items():
            if f not in rules or err.get(f) or (name.endswith("(strict)") and f == "014"):
                continue  # unparseable or not analysed: nothing resolved
            for r in o - rules[f]: res[group(r)] += 1
            intro += len(rules[f] - o)
        row["checks_passed"] = sum(j.get(k, False) for k in KEYS)
        row["resolution_by_group"] = {g: round(100 * res[g] / N[g], 1) for g in N}
        row["resolved_by_group"] = dict(res)
        row["introduced"] = intro
        row["resolved_total"] = sum(res.values())
        row["optional_share_of_resolved"] = round(100 * res["optional"] / max(1, sum(res.values())), 1)
    out["approaches"][name] = row

PAIRS = [("Opus 5.5 single-shot", "Unchanged originals"), ("Opus 5.5 single-shot (strict)", "Unchanged originals"),
         ("Opus 5.5 agent", "Opus 5.5 single-shot (strict)"), ("Opus 5.5 single-shot (strict)", "Claude Sonnet 4"),
         ("Opus 5.5 single-shot (strict)", "Rector"), ("Opus 5.5 agent", "Unchanged originals"),
         ("Opus 5.5 agent", "Opus 5.5 single-shot"), ("Opus 5.5 single-shot", "Claude Sonnet 4"),
         ("Opus 5.5 agent", "Claude Sonnet 4"), ("Opus 5.5 single-shot", "Rector"), ("Opus 5.5 agent", "Rector")]
tests = []
for a, b in PAIRS:
    x, y = COMPAT[a], COMPAT[b]
    only_a = sum(1 for f in FILES if x[f] and not y[f]); only_b = sum(1 for f in FILES if y[f] and not x[f])
    lo, hi = boot_ci(x, y)
    tests.append({"a": a, "b": b, "a_only": only_a, "b_only": only_b, "diff": only_a - only_b,
                  "ci95": [lo, hi], "p": exact_mcnemar(only_a, only_b)})
# Holm-Bonferroni over this family of comparisons
order = sorted(range(len(tests)), key=lambda i: tests[i]["p"])
m, running = len(tests), 0.0
for rank, i in enumerate(order):
    running = max(running, min(1.0, (m - rank) * tests[i]["p"]))
    tests[i]["p_holm"] = running
out["mcnemar"] = tests
json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
