#!/usr/bin/env python2

# Make like python3
from __future__ import print_function
from __future__ import division
#from builtins import int

import os
import os.path
import shutil
import subprocess
import argparse
import string
import datetime
import math

if __name__ == "__main__":

  DEFAULT_NEVENTSPERJOB = 10
  DEFAULT_ESTART = 1
  DEFAULT_G4_FCL = "protoDUNE_g4_3ms_sce.fcl"
  DEFAULT_DETSIM_FCL = "protoDUNE_detsim.fcl"
  DEFAULT_RECO_FCL = "protoDUNE_reco.fcl"
  DEFAULT_VERSION = "v07_07_01"
  DEFAULT_QUAL = "e17:prof"

  parser = argparse.ArgumentParser(description="Submits LArSoft Gen-G4-Detsim-Reco jobs to HTCondor as DAGs")
  parser.add_argument("-n","--nevents",type=int,required=True,help="Total number of events to generate")
  parser.add_argument("-j","--neventsperjob",type=int,default=DEFAULT_NEVENTSPERJOB,help="Number of events per job, default: {}".format(DEFAULT_NEVENTSPERJOB))
  parser.add_argument("-e","--estart",type=int,default=DEFAULT_ESTART,help="First event number of first job, default: {}".format(DEFAULT_ESTART))
  parser.add_argument("gen_fcl",help="fcl file to use for generation")
  parser.add_argument("--g4_fcl",default=DEFAULT_G4_FCL,help="fcl file to use for GEATN4 particle simulation, default: '{}'".format(DEFAULT_G4_FCL))
  parser.add_argument("--detsim_fcl",default=DEFAULT_DETSIM_FCL,help="fcl file to use for detector simulation, default: '{}'".format(DEFAULT_DETSIM_FCL))
  parser.add_argument("--reco_fcl",default=DEFAULT_RECO_FCL,help="fcl file to use for reconstruction, default: '{}'".format(DEFAULT_RECO_FCL))
  parser.add_argument("--version",default=DEFAULT_VERSION,help="dunetpc software version, default: '{}'".format(DEFAULT_VERSION))
  parser.add_argument("--qual",default=DEFAULT_QUAL,help="dunetpc software qualifier, default: '{}'".format(DEFAULT_QUAL))
  parser.add_argument("output_directory",help="output directory")

  args = parser.parse_args()

  print("Generating {} events with {} events/job using gen fcl '{}' and output directory: '{}'".format(args.nevents,args.neventsperjob,args.gen_fcl,args.output_directory))

  now = datetime.datetime.now().replace(microsecond=0).strftime("%y%m%d%H%M%S")
  nRuns = int(math.ceil(args.nevents//args.neventsperjob))

  genBase = os.path.basename(args.gen_fcl)
  genBase = os.path.splitext(genBase)[0]
  genBase = genBase.replace("gen_","")
  outDir = args.output_directory + "/{}_{}/".format(genBase,now)
  os.makedirs(outDir)
  #os.chmod(outDir,0o0755)
  logOutDir = "{}_{}/".format(genBase,now)
  os.makedirs(logOutDir)
  #os.chmod(logOutDir,0o0755)
  runScriptFn = os.path.join(logOutDir,"run_larsoft_simple.sh")
  subScriptFn = os.path.join(logOutDir,"larsoft_gen.sub")
  shutil.copyfile("run_larsoft_simple.sh",runScriptFn)
  shutil.copyfile("templates/larsoft_gen.sub",subScriptFn)
  os.chmod(runScriptFn,0o0755)

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
      "gen_transfer_output_files": "log,{}".format(genOut),
      "gen_transfer_output_remaps": "log={}/log_gen_{};{}={}".format(outDir,iRun,genOut,os.path.join(outDir,genOut)),
      "g4_transfer_output_files": "log,{}".format(g4Out),
      "g4_transfer_output_remaps": "log={}/log_g4_{};{}={}".format(outDir,iRun,g4Out,os.path.join(outDir,g4Out)),
      "detsim_transfer_output_files": "log,{}".format(detsimOut),
      "detsim_transfer_output_remaps": "log={}/log_detsim_{};{}={}".format(outDir,iRun,detsimOut,os.path.join(outDir,detsimOut)),
      "reco_transfer_output_files": "log,{}".format(recoOut),
      "reco_transfer_output_remaps": "log={}/log_reco_{};{}={}".format(outDir,iRun,recoOut,os.path.join(outDir,recoOut)),
    }
    for job in ["gen","g4","detsim","reco"]:
      for fn in ["log","output","error"]:
        script_args[job+"_"+fn] = "{}_{}.{}".format(job,iRun,fn)
    templateParams = script_args.copy()
    templateParams.update(vars(args))
    templateParams["iRun"] = iRun
    templateParams["nRuns"] = nRuns
    templateParams["outDir"] = outDir
    dagText = ""
    with open("templates/larsoft_gen.dag") as dagTemplateFile:
      dagTemplate = string.Template(dagTemplateFile.read())
      dagText = dagTemplate.substitute(templateParams)
    dagFn = "job_{}.dag".format(iRun)
    with open(os.path.join(logOutDir,dagFn),'w') as dag:
      dag.write(dagText)
    originaldir = os.getcwd()
    print(originaldir)
    subprocess.check_call(["condor_submit_dag",dagFn],cwd=logOutDir)
