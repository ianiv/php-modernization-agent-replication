# 020_class-ftp

Agent session for `subjects/original/020_class-ftp.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 8/8 (original: 0/8) |
| Rector PHP-version findings | 7 originally, 7 resolved, 2 introduced |
| Remaining Rector rules | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector |
| Turns | 10 |
| Wall-clock | 244 s |
| Cost | $1.01 |
| Output tokens | 24,962 (of which thinking 8,051) |
| Permission denials | 1 |
| Edits outside the target file | none |
| Session id | `155984d8-bab4-4ccd-98d1-944da6d52c13` |

## Agent's final report

The migration is finished: all 8 checks pass (106 assertions), lint is clean, and Rector has 2 findings left that I chose not to apply.

**Rector findings I left in place**
1. **Php4ConstructorRector** wants to delete the old-style `ftp_base()` method. Since PHP 8 it is no longer a constructor, just an ordinary public method that calls `__construct()`. Code can still call `$obj->ftp_base()` or `parent::ftp_base()`, so removing it would break those callers.
2. **ClassPropertyAssignToConstructorPromotionRector** wants to turn `$verb`/`$le` into promoted properties `$Verbose`/`$LocalEcho`. That renames the constructor's parameters, which breaks any caller using named arguments. It would also change the order in which properties are declared and the order things are set in the constructor. The subclasses in `class-ftp-pure.php` and `class-ftp-sockets.php` call `parent::__construct(true/false, $verb, $le)`, so I kept the signature exactly as it was.

**What I changed**
- `var` became `public`, `array()` became `[]`, and `$x{0}` became `$x[0]` (the curly-brace form is a fatal error in PHP 8).
- I added `#[\AllowDynamicProperties]` to the class. `SetServer()` writes `$this->verbose` (lowercase), and subclasses may add properties too; without the attribute PHP 8.2+ raises deprecation notices. I also declared the `$features` property.
- The removed `ereg_replace`/`ereg`/`eregi` calls are now `preg_*` calls that keep the old matching rules: `.` matches newlines and `$` only matches at the very end of the string. `glob_regexp()` still returns `1` on a match and `false` otherwise, as before. I didn't use Rector's suggested `preg_quote()` rewrite, because it would treat the glob regex as plain text and break matching.
- Missing array keys and variables that were never set are now handled with `??` or an explicit starting value, so PHP 8 doesn't warn about them or about `null` being passed to built-in functions. The results are the same as before. This covers the `pathinfo()` extension, `systype()` reading a field that isn't there, the `sscanf()` results passed to `mktime()` (cast to `int`, matching how PHP 5 turned `null` into 0), and the `$b` that `parselisting()` could return without ever setting it.
- In `mmkdir()`, it now passes `dirname((string) $dir)` and no longer passes an extra argument to the one-parameter `mkdir()`.

**Behaviour I changed on purpose**
- **`glob()` with an array as `$handle`:** it used the removed `each()` function. In the original this branch never worked, because each entry was handed to `ereg` as an array. It now loops over the array's values with `foreach`, which is what the code was clearly meant to do.
- **`mget()` permissions:** listings give permissions as text like `drwxr-xr-x`. Passing that text to PHP 8's `chmod()` is a fatal error, so non-numeric permissions are now skipped. The original `chmod()` call never worked on that text either. The `"date"` key, which `parselisting()` never sets, is checked before it is used.
- **Undefined variables in `nlist()` and `fput()`:** `nlist()` used an `$arg` that was never set, and `fput()` used a `$rest` that was never set. Both always behaved as empty or 0, so I made that explicit.
- **One original bug left in on purpose:** when a pattern contains `;`, `glob_pattern_match()` calls a method that doesn't exist, `my_regexp()`. That crashes in the original too, and I didn't change it.
- **Comment encoding:** the original's French comments contained non-UTF-8 bytes, and those characters were lost when I rewrote the file. Only comments are affected.

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   cd <repo>/runs/opus55/ws/020_class-ftp; f=subjects/migrated/opus_5_5/020_class-ftp.php
   perl -0pi -e 's/^\tvar \$/\tpublic \$/mg; s/\$lucifer\[0\]\{0\}/\$lucifer[0][0]/g; s/\barray\(\)/[]/g' $f
   grep -n "array(" $f
   ```

## Files

- Task prompt: [`../out/020_class-ftp/prompt.md`](../out/020_class-ftp/prompt.md)
- Migrated file: [`../out/020_class-ftp/migrated.php`](../out/020_class-ftp/migrated.php)
- Raw record: [`../out/020_class-ftp/agent.json`](../out/020_class-ftp/agent.json)
