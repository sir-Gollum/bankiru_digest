#!/bin/sh

echo "started" >> digest.log

cd /Users/sir_Gollum/src/bankiru_digest
source /Users/sir_Gollum/.python-envs//Users/sir_Gollum/src/bankiru_digest/bin/activate
python digest.py > digest.log

exit 0