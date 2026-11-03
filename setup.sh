#!/bin/bash
# setup.sh — prepare the environment used in the paper (macOS + Apple `container`; any Docker-compatible runtime works
# with the same commands: replace `container` with `docker`).
#  1. downloads the original study's replication package (Zenodo 20274676) into pkg/
#  2. starts a long-lived PHP 8.3 container named php83 with this directory mounted at /work
#  3. installs the PHP extensions and Composer used by the harness
#  4. regenerates the no-change baseline (runs/original_baseline is shipped; this re-checks it)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"

if [ ! -d pkg/PHP_Migration ]; then
  mkdir -p pkg_dl && curl -sL https://zenodo.org/api/records/20274676/files/LLMpHpSANER.zip/content -o pkg_dl/pkg.zip
  unzip -q pkg_dl/pkg.zip -d pkg_dl && mv pkg_dl/LLMpHpSANER pkg && rm -rf pkg_dl pkg/PHP_Migration/.git
fi

# The default resolver inside Apple container VMs did not answer in our setup; a public resolver fixes it.
container run -d --name php83 --dns 1.1.1.1 --cpus 8 --memory 8G -v "$ROOT":/work -w /work php:8.3-cli sleep infinity
container exec php83 sh -c 'apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends git unzip libzip-dev >/dev/null \
  && docker-php-ext-install bcmath zip >/dev/null \
  && printf "error_reporting=E_ALL\nmemory_limit=1G\ndate.timezone=UTC\n" > /usr/local/etc/php/conf.d/zz-harness.ini \
  && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer >/dev/null \
  && php -v | head -1'

# Baseline: the unchanged originals must reproduce the package's OriginalTestResults.txt check for check.
container exec -w /work/pkg/PHP_Migration/UnitTest/wordPress php83 sh -c 'mkdir -p build/results/original && \
  SUBJECT_ROOT=subjects/original SANDBOX_ROOT=build/sandboxes/original php vendor/bin/phpunit -c phpunit.xml \
  --log-junit build/results/original/junit.xml --testdox-text build/results/original/testdox.txt | tail -1; rm -rf build/sandboxes'
diff <(grep '\[' pkg/OriginalTestResults.txt) <(grep '\[' pkg/PHP_Migration/UnitTest/wordPress/build/results/original/testdox.txt) \
  && echo "Baseline reproduced check for check."
