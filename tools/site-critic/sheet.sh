#!/usr/bin/env bash
# sheet.sh <run> <page> [desktop|mobile] -> runs/<run>/<page>.<vp>.sheet.jpg (first 6 viewport frames tiled)
run=$1; page=$2; vp=${3:-desktop}
files=($(ls runs/$run/$page.$vp.frame0[0-5].png 2>/dev/null))
n=${#files[@]}; [ $n -eq 0 ] && exit 1
args=(); for f in "${files[@]}"; do args+=(-i "$f"); done
w=$([ "$vp" = desktop ] && echo 720 || echo 300)
filter=""; for i in $(seq 0 $((n-1))); do filter+="[$i]scale=$w:-1[s$i];"; done
if [ "$vp" = desktop ]; then
  cols=3; [ $n -lt 3 ] && cols=$n
  layout=""; for i in $(seq 0 $((n-1))); do r=$((i/cols)); c=$((i%cols)); layout+="$((c*w))_$((r*450))|"; done
  for i in $(seq 0 $((n-1))); do filter+="[s$i]"; done
  filter+="xstack=inputs=$n:layout=${layout%|}:fill=white"
else
  for i in $(seq 0 $((n-1))); do filter+="[s$i]"; done; filter+="hstack=inputs=$n"
fi
[ $n -eq 1 ] && filter="[0]scale=$w:-1"
ffmpeg -y -loglevel error "${args[@]}" -filter_complex "$filter" -q:v 4 runs/$run/$page.$vp.sheet.jpg && echo runs/$run/$page.$vp.sheet.jpg
