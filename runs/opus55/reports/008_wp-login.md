# 008_wp-login

Agent session for `subjects/original/008_wp-login.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 7/7 (original: 7/7) |
| Rector PHP-version findings | 8 originally, 7 resolved, 0 introduced |
| Remaining Rector rules | NullToStrictStringFuncCallArgRector |
| Turns | 24 |
| Wall-clock | 97 s |
| Cost | $0.40 |
| Output tokens | 7,660 (of which thinking 1,669) |
| Permission denials | 1 |
| Edits outside the target file | none |
| Session id | `9075981f-98c2-4e2c-8bdb-f78e5f5be02e` |

## Agent's final report

The migrated `wp-login.php` passes all 7 checks (60 assertions), lint is clean, and one Rector rule is still reported. Leaving it alone is deliberate.

**What changed:**
- `dirname(__FILE__)` → `__DIR__`.
- Old `array(...)` syntax → `[...]`.
- `list()` → `[...]` destructuring.
- `isset(x) ? x : default` → `x ?? default`.
- `0 === strpos(...)` → `str_starts_with`, and `false !== strpos(...)` → `str_contains`.
- All six `setcookie()` calls now use the PHP 7.3 options-array form. `httponly` is set only where the original passed `true`, so the cookies sent are the same.
- `rawurlencode( (string) $user_login )`: `$user_login` comes from the user record, so the cast can't change any real output.

**Rector finding remaining: `NullToStrictStringFuncCallArgRector`.** It wants `(string)` casts on request values: `$_SERVER['REQUEST_URI']`, `$_POST['user_login']`, the reset-password cookie, and `$_REQUEST['redirect_to']`. I left them out for two reasons:
- **The null case it guards against doesn't come up.** Request values from PHP are strings or arrays, never null. In the one case where null could appear, an unset `REQUEST_URI` (e.g. running from the command line), both versions already warn about the missing key.
- **It would change behaviour on array input.** Today a request like `user_login[]=x` makes `strpos`/`trim`/`str_contains` throw a `TypeError`. With the cast, the code would quietly carry on with the string `"Array"` plus a warning. That's a different code path: it could look up a user called "Array" or rewrite a redirect it currently rejects.

**Behaviour changed on purpose:** none.

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   tools/rector --diff 2>&1 | sed -n '/begin diff/,/end diff/p' | sed '1d;$d' > scratch/r.diff; (echo '--- a'; echo '+++ b'; cat scratch/r.diff) > scratch/r2.diff; patch --dry-run subjects/migrated/opus_5_5/008_wp-login.php scratch/r2.diff
   ```

## Files

- Task prompt: [`../out/008_wp-login/prompt.md`](../out/008_wp-login/prompt.md)
- Migrated file: [`../out/008_wp-login/migrated.php`](../out/008_wp-login/migrated.php)
- Raw record: [`../out/008_wp-login/agent.json`](../out/008_wp-login/agent.json)
