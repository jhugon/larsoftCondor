#!/bin/bash

date
echo "Starting larsoft simple job"
echo "Initial dir: "
pwd

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

if [ -z "$setup_script" ]; then # if no setups script, do default setup
  echo "Setting up DUNE software"
  source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
  setup mrb
  setup dunetpc $version -q $qual
  echo "Done setting up DUNE software"
else
  if [ -z "$setup_dir" ]; then
    source $setup_script
  else
    cd $setup_dir
    source $setup_script
  fi
fi
cd $TMPDIR
echo "DUNETPC_DIR="$DUNETPC_DIR

echo "Running lar..."
lar -c $fcl $infile -T $histfile >& $logfile

echo "Done!"
echo "Files in work dir:"
ls -lhtr
date
