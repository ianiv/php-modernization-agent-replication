# Tools, Not Prompts: Revisiting LLM-Based Legacy PHP Modernization with an Agent Harness

Paper: [`paper/tools-not-prompts.pdf`](paper/tools-not-prompts.pdf) (LaTeX source in [`paper/tex/`](paper/tex/); build with `make -C paper/tex`)

Author: Ianiv Schweber - Just a random guy on the Internet

This repository replicates and extends Mahmud et al., *When Modernization Breaks Working Code: A Single-File Study of LLMs
on Legacy PHP* ([arXiv:2610.40269](https://arxiv.org/abs/2610.40269); package: [Zenodo 20274676](https://zenodo.org/records/20274676)).
That study prompted five LLMs once per file to migrate 100 WordPress 4.0 files to PHP 8.3. It found that every model left
fewer working files than not changing the code at all.

We rerun the study's own scoring harness (630 hidden PHPUnit checks and 511 Rector PHP-version findings) with Claude Opus 5.5
under two conditions:

| Approach | Compatible files | Checks passed | Regressions | Repairs | Rector findings resolved |
|---|---:|---:|---:|---:|---:|
| Unchanged originals | 83 | 531 | – | – | 0% |
| Best model in the original study (Claude Sonnet 4) | 59 | 473 | 126 | 68 | 53.2% |
| Rector (original study) | 82 | 581 | 12 | 62 | 99.0% |
| **Opus 5.5, single-shot** (original prompt and extractor) | **94** | **617** | **1** | **87** | **67.5%** |
| **Opus 5.5, agent** (Claude Code + PHP 8.3, tests, lint, Rector) | **99** | **624** | **0** | **93** | **92.4%** |

The remaining file (009, `getid3.php`) cannot pass under the single-file protocol. Its checks load an unmigrated dependency
that PHP 8 rejects, and every approach in the original study also scores 0/6 on it.

## Validation

- The unchanged originals reproduce the package's `OriginalTestResults.txt` check for check (`runs/original_baseline`).
- Re-scoring the package's archived Sonnet 4 outputs reproduces the published figures exactly: 59 files, 76.3% preservation,
  68.7% repair, and 272 Rector findings resolved (`runs/sonnet_replay/score`).
- Rector run on each file in isolation reproduces the published 511 findings.

## Layout

```
paper/tools-not-prompts.pdf     the paper (compiled from paper/tex)
paper/tex/                      LaTeX source: main.tex, refs.bib, Makefile (figures drawn in TikZ/pgfplots)
setup.sh                        downloads the original package and starts a PHP 8.3 container; reproduces the baseline
harness/
  make_ws.sh                    isolated per-file agent workspace + tools/{test,test-original,lint,rector,php}
  task_prompt.md                agent instructions
  run_one.sh, run_all.sh        agent condition (Claude Code headless, claude-opus-5-5)
  oneshot.py                    single-shot condition (original prompt template and extractor, verbatim)
  rector_isolated.sh            Rector UP_TO_PHP_83 on one file in isolation
  score.sh, metrics.py          scoring on a pristine copy of the original harness
runs/
  original_baseline/            junit + testdox for the unchanged originals
  opus55/out/<id>/              agent: final report + run stats (agent.json), prompt, migrated.php, result.json, tamper.txt
  opus55/reports/               readable Markdown page per agent session, plus an index table
  opus55_oneshot/out/<id>/      single-shot: raw responses, migrated.php, result.json
  */score/                      summary.json, per_file.csv, rector.jsonl, junit.xml, testdox.txt, phpunit.log
```

## Reproduce

Requirements: macOS with Apple [`container`](https://github.com/apple/container) (or Docker: substitute `docker` for
`container`), Python 3, and Claude Code logged in.

```bash
./setup.sh                                 # package, PHP 8.3 container, baseline check
harness/run_all.sh opus55 6                # agent condition, 6 sessions in parallel
python3 -I harness/oneshot.py opus55_oneshot 8   # single-shot condition
harness/score.sh opus55                    # -> runs/opus55/score/summary.json
harness/score.sh opus55_oneshot
```

Every run script skips files that already have outputs, so you can rescore the shipped outputs without rerunning the
models. Remove `runs/<run>/out` to regenerate them.

## Notes

- **Paths.** Absolute local paths in the run records and logs were replaced with `<repo>` (the repository root) or `~`.
  The records are otherwise unedited.
- **Agent sessions.** The agent runs used `claude -p --output-format json`, which saves each session's final report
  and statistics but not the turn-by-turn conversation. `runs/opus55/reports/` presents those records readably
  (`python3 -I harness/render_reports.py`). Single-shot responses are complete, since each is a single call.
- **Not included.** This repository does not include the original replication package. `setup.sh` downloads it from
  Zenodo.
- **WordPress code.** The `migrated.php` and `response_*.txt` files are modified versions of WordPress 4.0 source files.
  WordPress is licensed under the GNU General Public License v2 or later, and so are those files (see `NOTICE`).
- **Cost.** The agent run cost $39.66 and the single-shot run $26.92, as reported by Claude Code.
