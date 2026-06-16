#!/usr/bin/env python3
import sys, re

contributor = None
comment = ''

for line in sys.stdin:
    line = line.strip()
    u = re.search(r'<username>(.*?)</username>', line)
    ip = re.search(r'<ip>(.*?)</ip>', line)
    c = re.search(r'<comment>(.*?)</comment>', line)
    if u:
        contributor = u.group(1)
    elif ip:
        contributor = 'IP:' + ip.group(1)
    if c:
        comment = c.group(1).lower()
    if '</revision>' in line and contributor:
        is_revert = 1 if 'revert' in comment or 'rv ' in comment else 0
        print(f'{contributor}\t1,{is_revert}')
        contributor = None
        comment = ''
