#!/usr/bin/env bash
# round.sh <run> <page-paths...> : capture + panel score every page + video judge on home
set -e
run=$1; shift
P=/home/pfrpc/pythonvirtualenvs/pftpy/bin/python
$P capture.py --base http://127.0.0.1:8138 --out runs/$run --pages "$@" --video > runs/$run.capture.log 2>&1 || { mkdir -p runs/$run; $P capture.py --base http://127.0.0.1:8138 --out runs/$run --pages "$@" --video > runs/$run.capture.log 2>&1; }
for path in "$@"; do
  slug=$(echo "$path" | sed 's#^/##; s#/$##; s#/#__#g'); [ -z "$slug" ] && slug=home
  $P critic.py score --run runs/$run --page $slug > runs/$run/$slug.score.txt 2>&1 &
done
$P critic.py video --run runs/$run --page home > runs/$run/home.video.txt 2>&1 &
wait
for path in "$@"; do slug=$(echo "$path" | sed 's#^/##; s#/$##; s#/#__#g'); [ -z "$slug" ] && slug=home; echo "== $slug $(tail -1 runs/$run/$slug.score.txt)"; done
