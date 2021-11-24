#!/bin/bash -i
set -e
set -o pipefail
clear
conda activate cherokee-diffwave
tensorboard --logdir models --port 8090 --bind_all
