#!/usr/bin/env python2

# Make like python3
from __future__ import print_function
from __future__ import division
#from builtins import int

import os
import os.path
import subprocess
import argparse
import string
import datetime
import math

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Submits LArSoft Gen-G4-Detsim-Reco jobs to HTCondor as DAGs")
  parser.add_argument("-n","--nevents",type=int,required=True,help="Total number of events to generate")
  parser.add_argument("-j","--neventsperjob",type=int,default=10,help="Number of events per job")
  parser.add_argument("-e","--estart",type=int,default=0,help="First event number of first job")
  parser.add_argument("gen_fcl",help="fcl file to use for generation")
  parser.add_argument("--g4_fcl",default="protoDUNE_g4_3ms_sce.fcl",help="fcl file to use for GEATN4 particle simulation")
  parser.add_argument("--detsim_fcl",default="protoDUNE_detsim_pdnoise.fcl",help="fcl file to use for detector simulation")
  parser.add_argument("--reco_fcl",default="protoDUNE_reco.fcl",help="fcl file to use for reconstruction")
  parser.add_argument("output_directory",help="output directory")

  args = parser.parse_args(['-n','30',"gen_single.fcl","/output"])

  print("Generating {} events with {} events/job using gen fcl '{}' and output directory: '{}'".format(args.nevents,args.neventsperjob,args.gen_fcl,args.output_directory))

  now = datetime.datetime.now().replace(microsecond=0).strftime("%y%m%d%H%M%S")
  nRuns = int(math.ceil(args.nevents//args.neventsperjob))

  genBase = os.path.basename(args.gen_fcl)
  genBase = os.path.splitext(genBase)[0]
  genBase = genBase.replace("gen_","")
  outDir = args.output_directory + "/{}_{}/".format(genBase,now)

  for iRun in range(nRuns):
    genOut = "events_{}_{}_{}_gen.root".format(genBase,now,iRun)
    g4Out = os.path.splitext(genOut)[0] + "_g4.root"
    detsimOut = os.path.splitext(g4Out)[0] + "_detsim.root"
    recoOut = os.path.splitext(detsimOut)[0] + "_reco.root"
    script_args = {
      "gen_args": "-c {} -o {} -e {} -n {}".format(args.gen_fcl,genOut,args.estart+iRun*args.neventsperjob,args.neventsperjob),
      "g4_args": "-c {} {} -o {}".format(args.g4_fcl,os.path.join(outDir,genOut),g4Out),
      "detsim_args": "-c {} {} -o {}".format(args.detsim_fcl,os.path.join(outDir,g4Out),detsimOut),
      "reco_args": "-c {} {} -o {}".format(args.reco_fcl,os.path.join(outDir,detsimOut),recoOut),
    }
    templateParams = script_args.copy()
    templateParams.update(vars(args))
    templateParams["iRun"] = iRun
    templateParams["nRuns"] = nRuns
    templateParams["outDir"] = outDir
    print(templateParams)
    dagText = ""
    with open("templates/larsoft_gen.dag") as dagTemplateFile:
      dagTemplate = string.Template(dagTemplateFile.read())
      dagText = dagTemplate.substitute(templateParams)
    print(dagText)
