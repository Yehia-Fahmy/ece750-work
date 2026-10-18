#!/bin/sh
set -eu

cd "$(dirname "$0")"
TECTONIC=${TECTONIC:-tectonic}

for source in L??-summary.tex; do
    "$TECTONIC" --untrusted --outdir .. "$source"
done

"$TECTONIC" --untrusted --outdir ../../midterm midterm-guide.tex
