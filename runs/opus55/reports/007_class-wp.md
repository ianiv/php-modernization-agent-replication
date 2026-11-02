# 007_class-wp

Agent session for `subjects/original/007_class-wp.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 7/7 (original: 3/7) |
| Rector PHP-version findings | 9 originally, 7 resolved, 0 introduced |
| Remaining Rector rules | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector |
| Turns | 43 |
| Wall-clock | 189 s |
| Cost | $0.81 |
| Output tokens | 14,827 (of which thinking 3,769) |
| Permission denials | 2 |
| Edits outside the target file | none |
| Session id | `53c74ce4-bf54-48a7-b62e-6a05fbedb082` |

## Agent's final report

All 7 checks pass (84 assertions), lint is clean, and Rector has 2 findings left. I'm leaving both in place on purpose because applying them would break existing callers. For comparison, the unmodified original fails 4 of the 7 checks under PHP 8.3.

**What was broken on PHP 8.3**
- **The old-style constructor.** PHP 8 no longer treats a method named after the class as its constructor, so `WP_MatchesMapRegex()` never ran. Its `output` stayed `null` and rewrite-rule substitution (`$matches[1]` and so on) quietly stopped working. I added a real `__construct()` and kept `WP_MatchesMapRegex()` as an ordinary method that calls it, so code calling `parent::WP_MatchesMapRegex()` or `$obj->WP_MatchesMapRegex()` still works.
- **The check that drops post types visitors can't query.** It compared the requested type against the values returned by `get_post_types()`. Where those values are objects (as in the test fixtures), PHP 8's comparison rules never find a match, so a valid `post_type` was thrown away. It now compares against the array keys. In real WordPress, the names output is a `name => name` map, so this gives the same result there.

**Modernization applied**
- Short `[]` array syntax, `??`, and `[$x] = explode(...)` destructuring.
- `str_starts_with` and `str_contains` instead of `strpos`.
- `$this->callback(...)` as the callback; `(int)` instead of `intval`.
- `(string)` casts where a value could be `null`, such as `parse_url()` with no path or a failed `preg_replace`, to avoid PHP 8.1 null-argument deprecations.

**Rector findings remaining**
1. **Php4ConstructorRector:** it now only flags the `WP_MatchesMapRegex()` method I kept for compatibility. Applying it would remove that method and break any caller that uses it directly.
2. **ClassPropertyAssignToConstructorPromotionRector:** promoting the properties would rename the constructor parameters to `$_subject` and `$_matches`, which breaks callers passing them by name (`subject:`, `matches:`). It would also reorder the declared properties, which changes the output of `serialize()`, `var_export()` and `(array)` casts.

**Behavior I changed on purpose**
- `send_headers()` no longer has the PHP 5.2 fallback for when `header_remove()` doesn't exist. That function always exists on PHP 5.3 and later, so the branch could never run.
- The post-type check is described above. For normal WordPress data it gives the same result as before.

I left the loose comparisons (`==`, `!=`, `in_array` without strict mode) unchanged, so they behave exactly as the original does on PHP 8.3.

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   cd subjects/migrated/opus_5_5 && cp 007_class-wp.php /tmp/007_before.php; cd ../../..; tools/rector --help 2>&1 | head -20; cat tools/rector
   ```

2. `Bash`

   ```
   cd subjects/migrated/opus_5_5 && tools_dummy=1; perl -0pi -e '
   s/\barray\(/[/g if 0;
   ' 007_class-wp.php; grep -n "array(" 007_class-wp.php
   ```

## Files

- Task prompt: [`../out/007_class-wp/prompt.md`](../out/007_class-wp/prompt.md)
- Migrated file: [`../out/007_class-wp/migrated.php`](../out/007_class-wp/migrated.php)
- Raw record: [`../out/007_class-wp/agent.json`](../out/007_class-wp/agent.json)
