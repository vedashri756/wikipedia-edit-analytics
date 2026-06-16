#!/usr/bin/env python3
import sys
import re

current_title = None

for line in sys.stdin:
    line = line.strip()
    title_match = re.search(r'<title>(.*?)</title>', line)
    if title_match:
        current_title = title_match.group(1)
    if '<revision>' in line and current_title:
        print(f'{current_title}\t1')
