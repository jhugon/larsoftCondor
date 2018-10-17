#!/bin/bash

setupDirectory=/scratch/jhugon/v07_07_01_e17debug
setupScript=$setupDirectory/setup.sh

nmax=1000
outdir="/cshare/vol2/users/jhugon/condor_output/beamreco"

if [ -z "$1" ]; then
    echo "No argument supplied, input raw data file required."
    exit 1
fi

date
echo "larsoft reco job"
echo "Submit dir: "
pwd
echo "args: "$@
infilename=$(realpath $1)

echo "Setting up DUNE software"
cd $setupDirectory
source $setupScript
cd $TMPDIR
echo "Done setting up DUNE software"

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

infilebase=$(basename $1 .root)
outfilename="${infilebase}_beamreco_${version}.root"
histsfilename="hists_${infilebase}_beamreco_${version}.root"
logfilename="${infilebase}_beamreco_${version}.log"
echo "infilename: $infilename"
echo "outfilename: $outfilename"
echo "histsfilename: $histsfilename"
echo "logfilename: $logfilename"
echo "outdir: $outdir"
echo "nmax: $nmax"
echo "version: $version"
echo "qual: $qual"
command="lar -c beamevent_job.fcl -s $infilename -o $outfilename -T $histsfilename"

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
