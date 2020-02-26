#!/usr/bin/python

# mmaligneralign.py


import yasara
import string
import disk
import os
from collections import namedtuple

from python2to3 import *

# Represents a yasara object being aligned
YObject = namedtuple("YObject", ["filename", "num", "mols"])


def molecule(obj):
  """Convert a YObject into an argument for MMLigner"""
  chainIDs = obj.mols.replace("_", "")

  if chainIDs == "":
    return obj.filename
  else:
    return obj.filename + ":" + chainIDs

def execute_mmligner(mmligner_bin, objects):
  """Execute MMLigner on provided inputs"""
  import subprocess
  mmlignercommand = [mmligner_bin,
                     molecule(objects[0]),
                     molecule(objects[1]),
                     "--superpose"]

  return subprocess.call(mmlignercommand)

def align_molecules(mmligner_bin, objects):
  """ Align Molecules with mmligner"""
  assert len(objects) == 2, "MMLigner can only align pairs of structures"

  # Expected output name
  expected_result = objects[1].filename+"_superposed__1.pdb"

  if 0 != execute_mmligner(mmligner_bin, objects):
    return "MMLigner encountered an error"

  if not disk.pathexists(expected_result):
    return "MMLigner did not find any useful alignments for these objects"

  try:
    newobj = yasara.LoadPDB(expected_result, center=None, correct=None)[0]
  except: 
    return "Yasara failed to load the MMLigner result"

  # transfer aligened PDB with original object
  yasara.TransferObj(newobj, objects[0].num, local="Match")

  # rename repaired object to RepairPDB
  yasara.NameObj(newobj, "AlignedObj{}".format(objects[1].num))

  # return the objectnumber of the aligned PDB
  return newobj
  
