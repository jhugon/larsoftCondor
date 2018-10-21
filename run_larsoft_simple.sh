#!/bin/bash

date
echo "Starting larsoft simple job"
echo "Submit dir: "
pwd
echo "args: "$@

cd $TMPDIR
echo "work dir:"
pwd

echo "=================================="
echo "=========== env =================="
echo "=================================="
env
echo "=================================="
echo "=================================="
echo "=================================="

echo "Setting up DUNE software"
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup mrb
setup dunetpc $version -q $qual
echo "Done setting up DUNE software"

echo "Running lar..."
lar $@

echo "Done!"
date
