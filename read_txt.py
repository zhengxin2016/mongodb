#!/usr/bin/env python3

for line in open('test.txt'):
    line = line.strip()
    if 'G：' in line:
        string = line.split('：')[-1]
    elif 'G:' in line:
        string = line.split(':')[-1]
    elif 'G' in line:
        string = line.split('G')[-1]
    else:
        continue
    if '/' in string:
        print(string.strip().replace('/', '\n'))
    else:
        print(string.strip())
