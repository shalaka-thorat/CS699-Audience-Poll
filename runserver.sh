#!/bin/bash

python3 -m venv ./poll_app/virt
source ./poll_app/virt/bin/activate
pip install -r ./poll_app/requirements.txt

python3 ./poll_app/run.py
