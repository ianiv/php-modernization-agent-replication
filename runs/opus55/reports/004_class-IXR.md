# 004_class-IXR

Agent session for `subjects/original/004_class-IXR.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 8/8 (original: 2/8) |
| Rector PHP-version findings | 9 originally, 9 resolved, 0 introduced |
| Remaining Rector rules | none |
| Turns | 30 |
| Wall-clock | 259 s |
| Cost | $1.20 |
| Output tokens | 26,591 (of which thinking 6,813) |
| Permission denials | 1 |
| Edits outside the target file | none |
| Session id | `3d94c8c2-88cd-4a36-a561-aef0c4b61a36` |

## Agent's final report

The migration is finished and all three done criteria are met:

- **Checks:** 8/8 pass (105 assertions).
- **Rector:** 0 PHP-version findings remain. It started with 9.
- **Lint:** clean.

**What changed**
- **Constructors:** each class now uses `__construct`. I kept the old same-name constructor methods (`IXR_Server()`, `IXR_Client()`, and so on) as thin wrappers that call `self::__construct(...)`. WordPress's `wp_xmlrpc_server` calls `$this->IXR_Server($this->methods)`. Because the wrapper uses `self::` and not `$this->`, calling it from a subclass doesn't re-enter the subclass's own constructor. A scratch script with a subclass built the same way confirmed this works.
- **Syntax updates:** `var` became `public`, `array()` became `[]`, and `isset ? :` became `??`. `str_starts_with`/`str_contains` replace the old `substr`/`strstr` checks, `is_a()` became `instanceof`, and `(double)`/`(boolean)`/`is_integer`/`is_double` became their standard names. `#[\Override]` is on the two overridden methods. The XML parser handlers are now first-class callables, in place of the `xml_set_object` setup.
- **Constructor promotion:** applied in `IXR_Value`, `IXR_Request`, `IXR_Client`, `IXR_Error` and `IXR_Base64`. A promoted property is declared where the constructor sits, so I moved some property declarations below the constructor to keep the original order. Order matters here: `get_object_vars()` follows it, and so do the struct members when one of these objects is turned into an `IXR_Value`. The scratch script confirmed the order is unchanged.

**Deliberate behaviour changes** (each one keeps old PHP 5–7 results or removes PHP 8 errors and deprecations)
- `htmlspecialchars` now passes `ENT_COMPAT | ENT_HTML401` explicitly. PHP 8.1 changed the default to also encode single quotes, so this keeps the old output.
- Values that might be null are cast to `(string)` before `htmlspecialchars`, `substr`, `trim`, `parse_url`, `base64_*` and `strlen`. This avoids PHP 8.1 deprecations and gives the same result as PHP 5 did for null.
- **`count()` on null:** this now throws a TypeError in PHP 8. The two `call()` methods now count null as 0 and other non-countable values as 1, as PHP 5 did. That matters for a request with no `<params>`.
- **Callbacks with no signature:** in `IXR_IntrospectionServer::call()`, a callback without a stored signature (such as `system.multicall`) used to crash on `array_shift(null)`. It now gets an empty signature and returns the same -32602 error the original returned. The old "undefined index" notice is gone.
- **Error message lookup:** the method-not-found error now reads `$this->message?->methodName`, so a missing message gives the same empty name without a warning.
- **`$currentTag`:** it is now a declared property. `tag_open()` writes `currentTag`, not the declared `_currentTag`, so the original created a dynamic property, which is deprecated in PHP 8.2. The new property starts as null where it used to be absent.

I left `mktime`/`date` alone: they still take the original arguments, and with valid input they behave the same.

The scratch scripts are in `scratch/` (`order.php`, `compat.php`).

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   cd <repo>/runs/opus55/ws/004_class-IXR; sed -n 1,41p subjects/original/004_class-IXR.php > scratch/header.txt; wc -l scratch/header.txt
   ```

## Files

- Task prompt: [`../out/004_class-IXR/prompt.md`](../out/004_class-IXR/prompt.md)
- Migrated file: [`../out/004_class-IXR/migrated.php`](../out/004_class-IXR/migrated.php)
- Raw record: [`../out/004_class-IXR/agent.json`](../out/004_class-IXR/agent.json)
