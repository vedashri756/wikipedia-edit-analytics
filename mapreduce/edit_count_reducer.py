#!/usr/bin/env python3
import sys

current_article = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    parts = line.split('\t')
    if len(parts) != 2:
        continue
    article, count = parts[0], int(parts[1])
    if article == current_article:
        current_count += count
    else:
        if current_article:
            print(f'{current_article}\t{current_count}')
        current_article = article
        current_count = count

if current_article:
    print(f'{current_article}\t{current_count}')
