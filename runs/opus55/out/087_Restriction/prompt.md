You are a senior PHP developer with expertise in legacy code modernization.
Your task is to migrate one legacy WordPress 4.0 PHP file up to PHP 8.3 standards while preserving functional equivalence. Preserve observable behavior, including inputs, outputs, side effects, and call compatibility.

## The file

- Edit ONLY this file: `subjects/migrated/opus_5_5/087_Restriction.php` (it starts as a copy of the original).
- Original for reference (read-only): `subjects/original/087_Restriction.php`
- It is the WordPress file ``. The full WordPress 4.0 tree is in `wordpress-base/` for context.

## Tools (each runs inside a PHP 8.3 container; call them via Bash from this directory)

- `tools/test` — runs this file's PHPUnit behavioral checks (`tests/files/087_SimplePieRestrictionRuntimeBehaviorTest.php`) against your migrated file under PHP 8.3 with E_ALL. Deprecation notices count as failures. Pass `--filter <name>` to run one check.
- `tools/test-original` — the same checks against the unmodified original, for reference.
- `tools/lint` — `php -l` on your migrated file.
- `tools/rector` — Rector (UP_TO_PHP_83 rule set) dry-run on your migrated file in isolation; lists the PHP-version modernization findings that remain. `tools/rector --diff` also prints the changes Rector would make.
- `tools/php <args>` — PHP 8.3 CLI with this directory as cwd, for your own scratch scripts (put them in `scratch/`).

You may read the tests and stubs under `tests/` to understand the expected contract.

## Definition of done

1. Every check in `tools/test` passes.
2. `tools/rector` reports no remaining PHP-version findings — or, for any that remain, applying them would change observable behavior or call compatibility, and you can say why for each one.
3. `tools/lint` is clean.

## Rules

- Do not modify anything outside `subjects/migrated/opus_5_5/087_Restriction.php` (except scratch files in `scratch/`). Scoring re-runs a pristine copy of the harness, so edits to tests, stubs, config or vendor are discarded and only make your results misleading.
- The checks are a sample of the file's contract, not all of it. Modernize the code genuinely: no special-casing of test inputs, no detecting the test environment, no deleting functionality the checks happen not to cover. Keep public function, method and class names, signatures, and return values compatible with callers elsewhere in WordPress.
- No network access is needed or allowed.

When finished, reply with a short summary: checks passed/total, Rector findings remaining (with justification for each), and any behavior you deliberately changed and why.
