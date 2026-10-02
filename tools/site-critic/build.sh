#!/usr/bin/env bash
# Build the worktree for local capture: baseURL must be local or alias pages redirect to production.
cd "$(dirname "$0")/../.." && /home/pfrpc/tmp/hugo148/hugo --gc --baseURL http://127.0.0.1:8138/ -d /home/pfrpc/tmp/pfsite-rev-build 2>&1 | grep -E "ERROR|Total"
