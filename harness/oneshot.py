"""One-shot arm: replicates the paper's single-call condition with Opus 5.5.

Paper: one user message = BASIC_PROMPT_TEMPLATE.format(code=<file>), no system prompt, no tools,
temperature 0.2, max_tokens 64000; first complete response kept; incomplete responses regenerated.
Here: same template and extractor; called via `claude -p` with all tools disabled and a minimal
system prompt (temperature is not settable through the CLI).
Usage: python3 -I oneshot.py <run-name> [parallelism] [id ...]
"""
import concurrent.futures as cf, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = f"{ROOT}/pkg/PHP_Migration/UnitTest/wordPress/subjects/original"

# Verbatim from pkg/prompts.py (BASIC_PROMPT_TEMPLATE)
TEMPLATE = """You are a senior PHP developer with expertise in legacy code modernization.
Your task is to migrate this legacy PHP code up to PHP 8.3 standards while preserving functional equivalence. Preserve observable behavior,
including inputs, outputs, side effects, and call compatibility.


Please migrate the following PHP code up to PHP 8.3 standards:

{code}

Your response should follow this EXACT format:

// MIGRATION_START
[your migrated PHP code here]
// MIGRATION_END

CRITICAL FORMATTING REQUIREMENT:
- Place the MIGRATION_START marker BEFORE the opening <?php tag
- Place the MIGRATION_END marker AFTER the closing PHP code
- Do NOT place these markers inside the PHP code itself

Provide only the migrated PHP code with the markers placed correctly outside the PHP code block, no additional commentary."""


def extract(resp):  # verbatim logic of pkg/.../core/parser.py extract_migrated_code
    s = re.search(r'//\s*MIGRATION_START\s*\n', resp, re.IGNORECASE)
    e = re.search(r'\n//\s*MIGRATION_END', resp, re.IGNORECASE)
    if s and e:
        return resp[s.end():e.start()].strip(), True
    if s and not e:
        lines = resp[s.end():].strip().split('\n')
        if lines and len(lines[-1].strip()) < 10 and not lines[-1].strip().endswith((';', '}', '?>')):
            lines = lines[:-1]
        return '\n'.join(lines).strip(), False
    return "", False


def run(fid, run_name, attempts=3):
    out = f"{ROOT}/runs/{run_name}/out/{fid}"
    os.makedirs(out, exist_ok=True)
    if os.path.exists(f"{out}/migrated.php"):
        return fid, "skip"
    prompt = TEMPLATE.format(code=open(f"{ORIG}/{fid}.php", encoding="utf-8", errors="ignore").read())
    env = dict(os.environ, CLAUDE_CODE_MAX_OUTPUT_TOKENS="64000")
    log = []
    for n in range(1, attempts + 1):
        t0 = time.time()
        p = subprocess.run(
            ["claude", "-p", "--model", "claude-opus-5-5", "--tools", "", "--setting-sources", "project",
             "--strict-mcp-config", "--no-session-persistence", "--output-format", "stream-json", "--verbose",
             "--system-prompt", "You are a helpful assistant."],
            input=prompt, capture_output=True, text=True, cwd=f"{ROOT}/runs", env=env, timeout=1200)
        # Join text from ALL assistant turns: claude -p auto-continues past the per-turn output cap,
        # and the final `result` field alone would hold only the last chunk.
        d, chunks = {"is_error": True}, []
        for line in p.stdout.splitlines():
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") == "assistant":
                chunks += [b.get("text", "") for b in ev.get("message", {}).get("content", []) if b.get("type") == "text"]
            elif ev.get("type") == "result":
                d = ev
        d["assistant_turns_with_text"] = len(chunks)
        resp = "".join(chunks)
        code, complete = extract(resp)
        log.append({"attempt": n, "seconds": round(time.time() - t0), "rc": p.returncode,
                    "is_error": d.get("is_error"), "cost_usd": d.get("total_cost_usd"),
                    "usage": d.get("usage"), "text_turns": d.get("assistant_turns_with_text"), "complete": complete, "extracted_chars": len(code)})
        open(f"{out}/response_{n}.txt", "w").write(resp)
        if code and complete and not d.get("is_error"):
            break
    open(f"{out}/migrated.php", "w").write(code + ("\n" if code else ""))
    json.dump({"id": fid, "attempts": log, "cost_usd": sum(a["cost_usd"] or 0 for a in log),
               "complete": log[-1]["complete"]}, open(f"{out}/result.json", "w"), indent=1)
    return fid, f"attempts={len(log)} complete={log[-1]['complete']} cost=${sum(a['cost_usd'] or 0 for a in log):.2f}"


if __name__ == "__main__":
    run_name = sys.argv[1]
    par = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    ids = sys.argv[3:] or sorted(f[:-4] for f in os.listdir(ORIG) if f.endswith(".php"))
    with cf.ThreadPoolExecutor(par) as ex:
        for fid, msg in ex.map(lambda i: run(i, run_name), ids):
            print(fid, msg, flush=True)
    print("ALL_DONE")
