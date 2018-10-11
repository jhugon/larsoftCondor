#!/bin/bash

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
cd $TMPDIR
echo "work dir:"
pwd

version=v07_07_00_01
qual=prof:e17
nmax=1000

outdir="/scratch/jhugon/np04_data/reco"

infilebase=$(basename $1 .root)
unpackedfilename="${infilebase}_unpacked_${version}.root"
unpackedHistsfilename="hists_${infilebase}_unpacked_${version}.root"
unpackedLogfilename="${infilebase}_unpacked_${version}.log"
outfilename="${infilebase}_reco_${version}.root"
histsfilename="hists_${infilebase}_reco_${version}.root"
logfilename="${infilebase}_reco_${version}.log"
#unpackedfilename="$databasedir/unpacked/${infilebase}_unpacked_${version}.root"
#unpackedHistsfilename="$databasedir/unpacked/hists_${infilebase}_unpacked_${version}.root"
#unpackedLogfilename="$databasedir/unpacked/${infilebase}_unpacked_${version}.log"
#outfilename="$databasedir/reco/${infilebase}_reco_${version}.root"
#histsfilename="$databasedir/reco/hists_${infilebase}_reco_${version}.root"
#logfilename="$databasedir/reco/${infilebase}_reco_${version}.log"
echo "infilename: $infilename"
echo "unpackedFilename: $unpackedfilename"
echo "unpackedHistsfilename: $unpackedHistsfilename"
echo "unpackedLogfilename: $unpackedLogfilename"
echo "outfilename: $outfilename"
echo "histsfilename: $histsfilename"
echo "logfilename: $logfilename"
echo "outdir: $outdir"
echo "nmax: $nmax"
echo "version: $version"
echo "qual: $qual"
unpackcommand="nice lar -c RunRawDecoder.fcl -n $nmax -s $infilename -o $unpackedfilename -T $unpackedHistsfilename"
command="nice lar -c protoDUNE_reco_data.fcl -n $nmax -s $unpackedfilename -o $outfilename -T $histsfilename"

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

echo "Running: \"$unpackcommand\""
nice $unpackcommand >& $unpackedLogfilename
echo "Running: \"$command\""
nice $command >& $logfilename
echo "Done!"
echo "=================================="
ls -lhtr
echo "=================================="
echo "Copying to output directory..."
cp $logfilename $outdir
cp $unpackedLogfilename $outdir
cp $histsfilename $outdir
cp $outfilename $outdir
echo "Done!"
date
