#!/bin/sh
set -eu

cd "$(dirname "$0")"
TECTONIC=${TECTONIC:-tectonic}

for source in L??-summary.tex midterm-guide.tex; do
    "$TECTONIC" --untrusted "$source"
done
