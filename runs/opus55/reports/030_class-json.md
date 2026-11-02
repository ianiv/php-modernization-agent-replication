# 030_class-json

Agent session for `subjects/original/030_class-json.php` (Claude Opus 5.5 in Claude Code, headless).

| | |
|---|---|
| Checks passing (scored on pristine harness) | 7/7 (original: 0/7) |
| Rector PHP-version findings | 6 originally, 6 resolved, 2 introduced |
| Remaining Rector rules | Php4ConstructorRector, BinaryOpBetweenNumberAndStringRector |
| Turns | 25 |
| Wall-clock | 331 s |
| Cost | $1.15 |
| Output tokens | 25,751 (of which thinking 5,196) |
| Permission denials | 1 |
| Edits outside the target file | none |
| Session id | `f540c237-fbb6-4854-a41f-3f0a515443e0` |

## Agent's final report

The migration is finished. All 7 checks pass (65 assertions), `tools/lint` is clean, and Rector has 2 findings left, both of which I left alone on purpose.

**What changed** (all in `subjects/migrated/opus_5_5/030_class-json.php`):
- **Fatal error fixed:** string offsets like `$s{0}` became `$s[0]`. PHP 8 refuses to load the file with the old syntax, which is why all 7 checks failed at first.
- **Constructors:** PHP 8 no longer treats a method named after its class as the constructor. Without a fix, `new Services_JSON(SERVICES_JSON_LOOSE_TYPE)` would quietly ignore its flags. Both classes now have `__construct()`. The old `Services_JSON()` and `Services_JSON_Error()` methods are still there and just call it, so older code that calls them still works.
- **Properties:** `$use` is now declared, using constructor promotion. It used to be created on the fly, which PHP 8.2 deprecates. `var` became `public`.
- **`isError()` is now `static`.** It is called as `Services_JSON::isError(...)`, which PHP 8 only allows for static methods. `$json->isError()` still works.
- **`toJSON()` guard:** before checking whether the value returned by `toJSON()` has its own `toJSON()`, the code now checks that it is an object or string. In PHP 8 that check throws a TypeError if `toJSON()` returns something like an int.
- **Rector modernizations:** short arrays, `implode`, `count`, `(int)`, `$obj::class`, `match` in the two UTF-16 helpers, first-class callables in `array_map`, and `(string)` casts where null used to be passed to string functions.

**Remaining Rector findings:**
1. **`Php4ConstructorRector`:** it wants the old PHP 4-style constructor methods removed or renamed. I kept them on purpose: they now only forward to `__construct()`, and removing them would break any subclass or plugin that calls `parent::Services_JSON()` or `parent::Services_JSON_Error()`.
2. **`BinaryOpBetweenNumberAndStringRector`:** it wants to rewrite `$substr_chrs_c_2 != '\\\''` (and the `\\"` version) as `!= 0`. That is a Rector mistake: those are string literals (`\'` and `\"`), not numbers. The rewrite would break how escaped quotes are decoded.

**Behavior I deliberately changed:**
- **Numbers from `encode()` now come back as strings.** `encode(0)` used to return the int `0` and now returns the string `'0'`; floats work the same way. The checks require this. The JSON text is unchanged: nested numbers already became exactly this text when joined into arrays and objects.
- **Unsupported input no longer crashes.** Values that PHP 8 would turn into a TypeError now get a defensive cast: a non-object `toJSON()` result, or null and other non-string input to the string helpers.

**Bug I kept on purpose:** `isError()` returns `false` for `Services_JSON_Error` objects. It compares the class name against lowercase `'services_json_error'`, and `get_class()` has returned the name's real capitalization since PHP 5. The original running on PHP 5 or 7 behaves the same way, so I preserved it, and my scratch script confirmed it. If you'd rather fix it, the fix is a case-insensitive comparison or `instanceof Services_JSON_Error`.

My scratch script (`scratch/check.php`) also covered loose-type decoding, nested `toJSON()`, Unicode and slash escaping, and calling the old `Services_JSON()` method directly. All gave the expected results.

## Permission denials

Commands the harness allowlist rejected; the agent continued with other tools.

1. `Bash`

   ```
   F=subjects/migrated/opus_5_5/030_class-json.php; grep -nE '\$\w+\{' $F | wc -l; perl -pi -e 's/(\$\w+)\{([^{}]*)\}/$1\[$2\]/g' $F; grep -nE '\$\w+\[(\$c|0|1|2|\+\+\$c)' $F | wc -l; perl -pi -e 's/\barray\(/[/g if 0' $F
   ```

## Files

- Task prompt: [`../out/030_class-json/prompt.md`](../out/030_class-json/prompt.md)
- Migrated file: [`../out/030_class-json/migrated.php`](../out/030_class-json/migrated.php)
- Raw record: [`../out/030_class-json/agent.json`](../out/030_class-json/agent.json)
