#!/usr/bin/env python3

def clean_str(string):
    string = string.replace(',', '，')
    string = string.replace('.', '。')
    string = string.replace('?', '？')
    string = string.replace('!', '！')
    return string.strip()
