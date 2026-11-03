"""Render each agent session's final report and run metadata as readable Markdown.

Note: the agent runs used `claude -p --output-format json --no-session-persistence`, which records only the
session's final report and statistics (cost, turns, tokens, permission denials), not the turn-by-turn
conversation. These pages present exactly that record.

Usage: python3 -I harness/render_reports.py [run-name]   (default: opus55)
Writes runs/<run>/reports/<id>.md and runs/<run>/reports/README.md (index).
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = sys.argv[1] if len(sys.argv) > 1 else "opus55"
OUT = os.path.join(ROOT, "runs", RUN, "out")
REP = os.path.join(ROOT, "runs", RUN, "reports")
SCORE = os.path.join(ROOT, "runs", RUN, "score", "per_file.csv")
os.makedirs(REP, exist_ok=True)

scores = {}
if os.path.exists(SCORE):
    for r in csv.DictReader(open(SCORE)):
        scores[r["file"]] = r


def fmt_cmd(d):
    ti = d.get("tool_input") or {}
    cmd = ti.get("command") or ti.get("file_path") or json.dumps(ti)[:300]
    return cmd.strip()


rows = []
for fid in sorted(os.listdir(OUT)):
    d = os.path.join(OUT, fid)
    aj = os.path.join(d, "agent.json")
    if not os.path.exists(aj):
        continue
    a = json.load(open(aj))
    res = json.load(open(os.path.join(d, "result.json")))
    tamper = open(os.path.join(d, "tamper.txt")).read().strip() if os.path.exists(os.path.join(d, "tamper.txt")) else ""
    s = scores.get(fid[:3], {})
    u = a.get("usage") or {}
    out_tok = u.get("output_tokens", 0)
    think = (u.get("output_tokens_details") or {}).get("thinking_tokens", 0)
    denials = a.get("permission_denials") or []
    checks = f"{s.get('new_pass', '?')}/{s.get('checks', '?')}" if s else "?"
    orig = f"{s.get('orig_pass', '?')}/{s.get('checks', '?')}" if s else "?"
    remaining = s.get("rector_remaining", "") if s else ""
    rows.append((fid, checks, orig, s.get("rector_orig", "?"), s.get("rector_resolved", "?"),
                 remaining, res.get("turns"), res.get("seconds"), res.get("cost_usd") or 0, len(denials)))

    lines = [f"# {fid}", "",
             f"Agent session for `subjects/original/{fid}.php` (Claude Opus 5.5 in Claude Code, headless).", "",
             "| | |", "|---|---|",
             f"| Checks passing (scored on pristine harness) | {checks} (original: {orig}) |",
             f"| Rector PHP-version findings | {s.get('rector_orig', '?')} originally, {s.get('rector_resolved', '?')} resolved, "
             f"{s.get('rector_introduced', '?')} introduced |",
             f"| Remaining Rector rules | {remaining.replace(';', ', ') or 'none'} |",
             f"| Turns | {res.get('turns')} |",
             f"| Wall-clock | {res.get('seconds')} s |",
             f"| Cost | ${res.get('cost_usd') or 0:.2f} |",
             f"| Output tokens | {out_tok:,} (of which thinking {think:,}) |",
             f"| Permission denials | {len(denials)} |",
             f"| Edits outside the target file | {'none' if not tamper else 'see below'} |",
             f"| Session id | `{a.get('session_id')}` |",
             "", "## Agent's final report", "", (a.get("result") or "").strip(), ""]
    if denials:
        lines += ["## Permission denials", "",
                  "Commands the harness allowlist rejected; the agent continued with other tools.", ""]
        for i, dn in enumerate(denials, 1):
            lines += [f"{i}. `{dn.get('tool_name')}`", "", "   ```", *("   " + l for l in fmt_cmd(dn).splitlines()[:12]), "   ```", ""]
    if tamper:
        lines += ["## Workspace changes outside the target", "", "```", tamper, "```", ""]
    lines += ["## Files", "",
              f"- Task prompt: [`../out/{fid}/prompt.md`](../out/{fid}/prompt.md)",
              f"- Migrated file: [`../out/{fid}/migrated.php`](../out/{fid}/migrated.php)",
              f"- Raw record: [`../out/{fid}/agent.json`](../out/{fid}/agent.json)", ""]
    open(os.path.join(REP, f"{fid}.md"), "w").write("\n".join(lines))

tot_cost = sum(r[8] for r in rows)
idx = ["# Agent session reports", "",
       f"{len(rows)} sessions, total cost ${tot_cost:.2f}. Each page shows the agent's final report and run statistics.",
       "The runs recorded only the final report per session (`claude -p --output-format json`), not the turn-by-turn",
       "conversation. Checks and Rector figures come from scoring on a pristine copy of the harness.", "",
       "| File | Checks | Original | Rector found | Resolved | Remaining rules | Turns | Seconds | Cost | Denials |",
       "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|"]
for r in rows:
    idx.append(f"| [{r[0]}]({r[0]}.md) | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5].replace(';', ', ')} | {r[6]} | {r[7]} | ${r[8]:.2f} | {r[9]} |")
open(os.path.join(REP, "README.md"), "w").write("\n".join(idx) + "\n")
print(f"wrote {len(rows)} reports + index to {REP}")
