#!/bin/bash

date
cd $TMPDIR
pwd
echo "dummy run larsoft"
echo "args: "$@
command="lar -c $1 -n $2"
echo "command: "$command
echo "=================================="
env
echo "=================================="
ls -lhtr
date
