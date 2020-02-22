#!/usr/bin/python

# mmaligneralign.py


import yasara,string,disk,os
from python2to3 import *

# residue conversion dictionnary
aa_dict = {'ALA':'A','CYS':'C','ASP':'D','GLU':'E','PHE':'F','GLY':'G','HIS':'H','ILE':'I','LYS':'K','LEU':'L','MET':'M','ASN':'N','PRO':'P','GLN':'Q','ARG':'R','SER':'S','THR':'T','VAL':'V','TRP':'W','TYR':'Y','H1S':'H','H2S':'H'}

# Align_Molecules
# ==============
def Align_Molecules(cachedir,foldxbin,mollist,objectnumbers):
  # open list for pdb files
  pdbfiles = []
  # set pdb filename
  for objnum in objectnumbers:
      pdbfilename = "Object"+str(objnum)+".pdb"
      pdbfiles.append(pdbfilename)
      # save pdb
      yasara.SavePDB(objnum,os.path.join(cachedir,pdbfilename))
  # change to temp folder
  os.chdir(cachedir)
  # citation to MMligner
  citation="Please cite Collier et al., Bioinformatics. 33(7):1005-1013."
  # show BuildModel message
  yasara.ShowMessage("Running structural alignment with MMligner. "+citation)
  # build the MMligner command
  mmlignercommand = foldxbin + " ./" + pdbfiles[0] + ":" + mollist[0] + " ./" + pdbfiles[1] + ":" + mollist[1] + " --superpose"
  # run MMligner
  print(mmlignercommand)
  os.system(mmlignercommand)
  try:
    print(os.path.join(cachedir,"Object"+str(objectnumbers[-1])+".pdb_superposed__1.pdb"))
    newobjlist = yasara.LoadPDB(os.path.join(cachedir,"Object"+str(objectnumbers[-1])+".pdb_superposed__1.pdb"), center=None, correct=None)
  except: 
    yasara.plugin.end("Cannot read MMligner output. Make sure you have set the correct MMligner file locations in Analyze > Align > Configure plugin")
  # transfer aligened PDB with original object
  yasara.TransferObj(newobjlist[0],objectnumbers[0],local="Match")
  # rename repaired object to RepairPDB
  yasara.NameObj(newobjlist[0],"AlignedObj"+str(objectnumbers[-1]))
  # show LoadPDB message of repaired structure
  yasara.ShowMessage("Aligned PDB loaded in YASARA soup as Object "+str(newobjlist[0])+". You can save this PDB when the plugin procedure ends. Please wait ...")
  # stop showing messages on screen        
  yasara.HideMessage()
  yasara.Wait(5,"Seconds")
  # return the objectnumber of the aligned PDB
  return newobjlist[0]
  