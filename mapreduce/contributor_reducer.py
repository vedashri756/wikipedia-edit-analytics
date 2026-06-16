#!/usr/bin/env python3
import sys

current = None
total_edits = 0
total_reverts = 0

for line in sys.stdin:
    line = line.strip()
    parts = line.split('\t')
    if len(parts) != 2: continue
    contrib = parts[0]
    vals = parts[1].split(',')
    edits, reverts = int(vals[0]), int(vals[1])
    if contrib == current:
        total_edits += edits
        total_reverts += reverts
    else:
        if current:
            print(f'{current}\t{total_edits}\t{total_reverts}')
        current = contrib
        total_edits = edits
        total_reverts = reverts

if current:
    print(f'{current}\t{total_edits}\t{total_reverts}')
