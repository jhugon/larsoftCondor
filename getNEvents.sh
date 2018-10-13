#!/bin/bash

echo $@ >& /scratch/jhugon/condor/args.txt

version=v07_07_00_01
qual=prof:e17

if [ -z "$1" ]; then
    echo "No argument supplied, number of events per job required." >& 2
    exit 1
fi

if [ -z "$2" ]; then
    echo "No argument supplied, input raw data file required."  >& 2
    exit 1
fi

infilename=$(realpath $2)
eventsPerJob=$1

echo "Setting up DUNE software" >& 2
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh >& 2
setup mrb >& 2
setup dunetpc $version -q $qual >& 2
echo "Done setting up DUNE software" >& 2

totalEvents=$(python -c "import ROOT; f = ROOT.TFile(\"${infilename}\"); print f.Events.GetEntries()")
nJobs=$(python -c "import math; print int(math.ceil(float($totalEvents)/$eventsPerJob))")

echo "nEventsTotal = $totalEvents"
echo "nJobs = $nJobs"
