# 061_class.wp-scripts

Agent session for `subjects/original/061_class.wp-scripts.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 5/5 (original: 5/5) |
| Rector PHP-version findings | 5 originally, 4 resolved, 0 introduced |
| Remaining Rector rules | FirstClassCallableRector |
| Turns | 13 |
| Wall-clock | 56 s |
| Cost | $0.21 |
| Output tokens | 3,372 (of which thinking 394) |
| Permission denials | 1 |
| Edits outside the target file | none |
| Session id | `bda88a8a-658c-4f94-8595-71bbc1274c73` |

## Agent's final report

All three checks are met: 5 of 5 checks pass (66 assertions), lint is clean, and one Rector finding remains on purpose.

**What I changed in `subjects/migrated/opus_5_5/061_class.wp-scripts.php`:**
- **String prefix checks:** the four `0 === strpos(...)` checks in `do_item()` and `in_default_dir()` now use `str_starts_with()`. The `preg_match()` input gets a `(string)` cast too. A `null` script source used to trigger PHP 8.1+ "null passed to string function" deprecations; it is now handled as an empty string, which gives the same result as before. An empty needle still matches, so behaviour on 8.x is unchanged.
- **Shorter syntax:** I replaced `$x ? $x : $default` with `$x ?: $default`, which gives the same result.
- **Arrays:** all `array()` literals now use `[]`, including the `[&$this]` passed by reference.

**The Rector finding I left in place:** `FirstClassCallableRector` wants to change `add_action('init', [ $this, 'init' ], 0)` to `$this->init(...)`. I didn't apply it because it would break callers. `$this->init(...)` creates a `Closure`, so WordPress would store the hook under a different ID. Then `remove_action('init', [ $wp_scripts, 'init' ], 0)` and `has_action()` would no longer find the hook. It would also change what plugins see when they inspect `$wp_filter`.

**Deliberate behaviour changes:** none.

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   cd subjects/migrated/opus_5_5 && f=061_class.wp-scripts.php && perl -0pi -e '
   s/array\(&\$this\)/[&\$this]/;
   s/\$this->registered\[\$handle\]->ver \? \$this->registered\[\$handle\]->ver : /\$this->registered[\$handle]->ver ?: /;
   s/preg_match\(\x27\|\^\(https\?:\)\?\/\/\|\x27, \$src\)/preg_match(\x27|^(https?:)?\/\/|\x27, (string) \$src)/;
   s/0 === strpos\(\$src, \$this->content_url\)/str_starts_with( (string) \$src, (string) \$this->content_url )/;
   s/0 === strpos\( \$src, \x27\/\x27 \. WPINC \. \x27\/js\/l10n\x27 \)/str_starts_with( (string) \$src, \x27\/\x27 . WPINC . \x27\/js\/l10n\x27 )/;
   s/0 === strpos\( \$src, \$test \)/str_starts_with( (string) \$src, (string) \$test )/;
   s/= array\(\);/= [];/;
   ' $f && cd ../../.. && tools/lint && tools/test 2>&1 | tail -3 && tools/rector --diff 2>&1 | tail -25
   ```

## Files

- Task prompt: [`../out/061_class.wp-scripts/prompt.md`](../out/061_class.wp-scripts/prompt.md)
- Migrated file: [`../out/061_class.wp-scripts/migrated.php`](../out/061_class.wp-scripts/migrated.php)
- Raw record: [`../out/061_class.wp-scripts/agent.json`](../out/061_class.wp-scripts/agent.json)
