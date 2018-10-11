#!/bin/bash

date
cd $TMPDIR
pwd
echo "dummy run larsoft"
echo "args: "$@
command="lar -c protoDUNE_reco_data.fcl $1"
echo "command: "$command
echo "=================================="
env
echo "=================================="
ls -lhtr
date
