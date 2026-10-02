#!/usr/bin/env bash
# tagline_sweep.sh: capture homepage once per tagline (H1 swapped in-browser), then score each with 3 runs per judge.
P=/home/pfrpc/pythonvirtualenvs/pftpy/bin/python
while IFS='|' read -r id text; do
  $P capture.py --base http://127.0.0.1:8138 --out runs/tag-$id --pages / --h1 "$text" > runs/tag-$id.log 2>&1
done < taglines.txt
while IFS='|' read -r id text; do
  ( $P critic.py score --run runs/tag-$id --page home --runs 3 | tail -1 | sed "s#^#$id|$text|#" ) &
done < taglines.txt
wait
