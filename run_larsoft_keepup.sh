#!/bin/bash

version=v07_08_00_03
qual=prof:e17
#overrides version and qual
#setup_dir=/scratch/jhugon/v07_07_03_01
#setup_script=setup.sh
#version="v07_07_03_01plustest"
nmax=1000
outdir="/cshare/vol2/users/jhugon/condor_output/reco_keepup_v07_08_00_03"

if [ -z "$1" ]; then
    echo "No argument supplied, input raw data file required."
    exit 1
fi

if [ -z "$nEventsTotal" ]; then
  echo "Error nEventsTotal ENV var not set"
  exit 1;
fi
if [ -z "$nEventsPerJob" ]; then
  echo "Error nEventsPerJob ENV var not set"
  exit 1;
fi
if [ -z "$nJobs" ]; then
  echo "Error nJobs ENV var not set"
  exit 1;
fi
if [ -z "$ProcId" ]; then
  echo "Error ProcId ENV var not set"
  exit 1;
fi

date
echo "larsoft reco job"
echo "Submit dir: "
pwd
echo "args: "$@
infilename=$(realpath $1)
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
  mrbslp
fi
cd $TMPDIR

#nEventsTotal=$(python -c "import ROOT; f = ROOT.TFile(\"${infilename}\"); print f.Events.GetEntries()")
#echo "Events in file: $nEventsTotal"
#if [ -z "$nJobs" ]; then
#    nJobs=1
#fi
#if [ -z "$ProcId" ]; then
#    ProcId=0
#fi
#nEventsPerJob=$(python -c "import math; print int(math.ceil(float($nEventsTotal)/$nJobs))")
echo "Total Events: $nEventsTotal"
echo "Events Per Job: $nEventsPerJob"
echo "ProcId: $ProcId"
nSkip=$(python -c "print ${ProcId}*${nEventsPerJob}")
echo "nSkip: $nSkip"
nmax=$(python -c "print min($nmax,$nEventsPerJob)")
jobSuffix=$(python -c "print \"_job${ProcId}\" if $nJobs > 1 else \"\"")

infilebase=$(basename $1 .root)
outdir=$outdir/$infilebase
outfilename="${infilebase}_reco_${version}${jobSuffix}.root"
histsfilename="hists_${infilebase}_reco_${version}${jobSuffix}.root"
logfilename="${infilebase}_reco_${version}${jobSuffix}.log"
echo "infilename: $infilename"
echo "outfilename: $outfilename"
echo "histsfilename: $histsfilename"
echo "logfilename: $logfilename"
echo "outdir: $outdir"
echo "nmax: $nmax"
echo "version: $version"
echo "qual: $qual"
command="lar -c protoDUNE_SP_keepup_decoder_reco.fcl --nskip $nSkip -n $nmax -s $infilename -o $outfilename -T $histsfilename"

echo "Running: \"$command\""
$command >& $logfilename
echo "Done!"
echo "=================================="
ls -lhtr
echo "=================================="
echo "Making ouput directory: $outdir"
mkdir -p $outdir
echo "Copying to output directory..."
cp $logfilename $outdir
cp $histsfilename $outdir
cp $outfilename $outdir
echo "Done!"
date
