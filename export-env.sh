#!/bin/bash

cd "$(dirname "$0")" || exit 1

conda env export --no-builds | grep -v "prefix:" > environment.yml

