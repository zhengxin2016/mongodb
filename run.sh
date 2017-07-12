#!/usr/bin/env bash

echo '---------------dialogue.py------------------'
python3 dialogue.py
if [[ $? -ne 0 ]]; then
        exit
fi
echo '---------------sale.py------------------'
python3 sale.py

