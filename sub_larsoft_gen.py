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

  DEFAULT_NEVENTSPERJOB = 10
  DEFAULT_ESTART = 0
  DEFAULT_G4_FCL = "protoDUNE_g4_3ms_sce.fcl"
  DEFAULT_DETSIM_FCL = "protoDUNE_detsim_pdnoise.fcl"
  DEFAULT_RECO_FCL = "protoDUNE_reco.fcl"

  parser = argparse.ArgumentParser(description="Submits LArSoft Gen-G4-Detsim-Reco jobs to HTCondor as DAGs")
  parser.add_argument("-n","--nevents",type=int,required=True,help="Total number of events to generate")
  parser.add_argument("-j","--neventsperjob",type=int,default=DEFAULT_NEVENTSPERJOB,help="Number of events per job, default: {}".format(DEFAULT_NEVENTSPERJOB))
  parser.add_argument("-e","--estart",type=int,default=DEFAULT_ESTART,help="First event number of first job, default: {}".format(DEFAULT_ESTART))
  parser.add_argument("gen_fcl",help="fcl file to use for generation")
  parser.add_argument("--g4_fcl",default=DEFAULT_G4_FCL,help="fcl file to use for GEATN4 particle simulation, default: '{}'".format(DEFAULT_G4_FCL))
  parser.add_argument("--detsim_fcl",default=DEFAULT_DETSIM_FCL,help="fcl file to use for detector simulation, default: '{}'".format(DEFAULT_DETSIM_FCL))
  parser.add_argument("--reco_fcl",default=DEFAULT_RECO_FCL,help="fcl file to use for reconstruction, default: '{}'".format(DEFAULT_RECO_FCL))
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
