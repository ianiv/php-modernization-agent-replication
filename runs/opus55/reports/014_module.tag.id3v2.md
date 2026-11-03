# 014_module.tag.id3v2

Agent session for `subjects/original/014_module.tag.id3v2.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 6/6 (original: 0/6) |
| Rector PHP-version findings | 9 originally, 8 resolved, 0 introduced |
| Remaining Rector rules | ChangeSwitchToMatchRector |
| Turns | 34 |
| Wall-clock | 359 s |
| Cost | $1.12 |
| Output tokens | 18,377 (of which thinking 7,161) |
| Permission denials | 5 |
| Edits outside the target file | none |
| Session id | `bd2ffc8f-6e75-4f91-ab09-0561ceddb35e` |

## Agent's final report

I've migrated `014_module.tag.id3v2.php` to PHP 8.3. All 6 checks pass (92 assertions) under E_ALL, lint is clean, and Rector has one finding left, which I'm leaving on purpose (explained below).

**What changed:**
- **Curly-brace string offsets** (`$x{5}` → `$x[5]`, 15 places): this was the fatal error that stopped every check from running on PHP 8.
- **Syntax updates:** `array()` → `[]` and `list()` → `[]` (both done with a token-based script, so nothing inside strings or comments was touched), and `isset($a) ? $a : d` → `$a ?? d`.
- **Static method calls:** `$this->StaticMethod()` → `static::StaticMethod()`. This picks the method the same way as before, so subclasses that override these methods still get called.
- **Newer string functions:** `str_starts_with` replaces `substr(...)=='lit'` where the literal is the same length, and `str_contains` replaces `strpos(...)!==false`, `===false` and the true/false use of `strstr`.
- **`utf8_encode()`** (deprecated in 8.2) → `mb_convert_encoding($x, 'UTF-8', 'ISO-8859-1')`, which does the same conversion.
- **`(string)` casts** on string arguments of built-in functions (`substr`, `strlen`, `strpos`, `trim`, `explode`, `preg_*`, …). A null now gives `''`, as PHP 5 did silently, but without PHP 8.1's deprecation notice. My script added 356 casts, more than the 226 Rector proposed, because some are on values that are always strings; those extra casts are harmless but noisy.
- **Two `switch` blocks → `match`:** the MP3ext warning selection and the UTF-16 word-size choice. All their case labels are non-numeric strings, so `match`'s strict comparison behaves the same as the old loose one.

**Remaining Rector finding:** `ChangeSwitchToMatchRector` on `IsValidID3v2FrameName()`. I didn't apply it because `switch` compares loosely and `match` compares strictly. A caller passing the major version as a string (`"3"`) currently gets a frame-name match result; after the change it would get `false`. That is a real behaviour change for callers.

**Deliberate behaviour decision:** the footer flags line was `ord(substr($footer{5}))`, which calls `substr()` with only one argument. On PHP 5 that returned NULL with a warning, so `$id3_flags` was always 0. On PHP 8 the same call throws an `ArgumentCountError`. I set `$id3_flags = 0;` with a comment, which keeps the old result instead of crashing. The obvious intended code, `ord($footer[5])`, would change what gets parsed, so I left it out. It's a one-line change if you'd rather fix the bug.

The scratch scripts are in `scratch/` (`transform.php`, `pass2.php`, `casts.php`, plus a backup `before_casts.php`).

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   wc -l subjects/original/014_module.tag.id3v2.php; tools/rector --diff > scratch/diff.txt 2>&1; wc -l scratch/diff.txt; grep -n "utf8_\|NullToStrict\|match (" scratch/diff.txt | head -50
   ```

2. `Bash`

   ```
   cat tools/_env; container exec php83 cat /work/harness/rector_isolated.sh; container exec php83 cat /work/pkg/PHP_Migration/rector.php
   ```

3. `Bash`

   ```
   tools/rector --diff > scratch/rector.diff 2>&1; grep -c "" scratch/rector.diff
   ```

4. `Bash`

   ```
   F=subjects/migrated/opus_5_5/014_module.tag.id3v2.php && tools/php -r 'copy($argv[1], "scratch/before_casts.php");' $F && tools/php scratch/casts.php $F && tools/lint && tools/test 2>&1 | tail -2 && tools/rector
   ```

5. `Bash`

   ```
   tools/rector --diff 2>&1 | grep -E "^[-+]"; diff subjects/original/014_module.tag.id3v2.php subjects/migrated/opus_5_5/014_module.tag.id3v2.php | grep "^>" | grep -E "string\) (\(|\\$this|static::[A-Z]\w+\(\\$\w+\)\))" | head; diff subjects/original/014_module.tag.id3v2.php subjects/migrated/opus_5_5/014_module.tag.id3v2.php | grep -c "^>"
   ```

## Files

- Task prompt: [`../out/014_module.tag.id3v2/prompt.md`](../out/014_module.tag.id3v2/prompt.md)
- Migrated file: [`../out/014_module.tag.id3v2/migrated.php`](../out/014_module.tag.id3v2/migrated.php)
- Raw record: [`../out/014_module.tag.id3v2/agent.json`](../out/014_module.tag.id3v2/agent.json)
