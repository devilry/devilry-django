#!/bin/sh

if test -d ".venv"; then
    rm -r .venv
fi

python -m venv .venv || { echo 'FAILED: python -m venv .venv' ; exit 1; };