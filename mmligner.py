# YASARA PLUGIN
# TOPIC:       Molecular modeling
# TITLE:       MMligner plugin
# AUTHOR:      James Collier, Alexander Botzki. VIB
# LICENSE:     GPL3 (www.gnu.org)
# DESCRIPTION: This plugin provides access to the structural alignment software MMligner
###########################################################################################################################
# This is a YASARA plugin to be placed in the /plg subdirectory #
# Go to www.yasara.org/plugins for documentation and downloads  #
#################################################################
# Web address of the MMligner site to download the program: http://lcb.infotech.monash.edu.au/mmligner/
# Please cite the article when publishing results from this plugin:
# J. H. Collier,  L. Allison,  A. M. Lesk,  P. J. Stuckey,  M. Garcia de la Banda  &  A. S. Konagurthu 
# Statistical inference of protein structural alignments using information and compression
# Bioinformatics. 33(7):1005-1013.
# Version 0.9.0
#
"""
MainMenu: Analyze
  PullDownMenu: Align
    PopUpMenu after Molecules with MUSTANG: Molecules with MMligner
      MoleculeSelectionMenu: Select first molecule and chain
      MoleculeSelectionMenu: Select second molecule and chain
      Request: AlignMMLigner

    PopUpMenu: Configure MMligner plugin
      FileSelectionMenu: Select your MMligner executable file
        MultipleSelections: No
        Filename: *
      Request: FileLocations
"""

import os
import yasara
import disk

from mmligneralign import align_molecules, YObject


ERROR_MESSAGE = """Cannot execute MMligner.
 Make sure you have set the correct MMligner file
 locations in Analyze > Align > Configure plugin.
"""

SUCCESS_MESSAGE = """
Aligned PDB loaded in YASARA soup as Object {}.
 You can save this PDB when the plugin procedure ends. Please wait ...
"""


def mmligner_cache(mmligner_tmp):
  cache = os.path.join(os.getcwd(), mmligner_tmp)
  if not os.path.isdir(cache):
    disk.remove(cache)
  if not os.path.exists(cache):
    disk.makedirs(cache, yasara.permissions)

  return cache

def mmligner_exe(mmligner_path):
  from subprocess import call

  call(mmligner_path)

  return mmligner_path

def disabled_check():
  """ ASSIGN 1 TO yasara.plugin.exitcode IF THIS PLUGIN CANNOT WORK AND SHOULD
      BE DISABLED (DATA MISSING, WRONG OPERATING SYSTEM ETC.)"""
  yasara.plugin.exitcode = 0

def file_locations():
  """ Set file locations of MMaligner binary,
      this section needs to be the first one,
      otherwise even this section will raise an error at the end"""
  xbinpath = yasara.selection[0].filename[0]

  if not os.path.split(xbinpath)[-1][:8] == 'mmligner':
    yasara.plugin.end("Invalid file. Download MMligner from http://lcb.infotech.monash.edu.au/mmligner/")

  lines = open("mmligner.cnf","r").readlines()
  with open("mmligner.cnf","w") as output:
    for line in lines:
      if line.startswith("MMLIGNER_BIN"):
        output.write("MMLIGNER_BIN = "+xbinpath+"\n")
      else:
        output.write(line)

def run_mmligner():
  """Run the mmligner program"""
  import traceback
  # show MMLigner message
  citation = "Please cite Collier et al., Bioinformatics. 33(7):1005-1013."
  yasara.ShowMessage("Running structural alignment with MMligner. "+citation)

  # make the list of molname selections
  # put all molecules from each selection in 1 string
  # molecules that are "empty" (e.g. " ") are ignored
  # duplicates are discarded
  mols = [
    "".join(set([molecule.name.strip() for molecule in yasara.selection[0].molecule])),
    "".join(set([molecule.name.strip() for molecule in yasara.selection[1].molecule]))
    ]

  # molecules should belong to same object
  objectnumbers = [yasara.selection[0].molecule[0].object.number.inyas,
                   yasara.selection[1].molecule[0].object.number.inyas]

  # set the cache dir from the config file
  cachedir = mmligner_cache(yasara.plugin.config["MMLIGNER_TMP"])

  # set the cache dir from the config file
  try:
    mmligner_bin = mmligner_exe(yasara.plugin.config["MMLIGNER_BIN"])
  except FileNotFoundError:
    yasara.plugin.end(ERROR_MESSAGE)

  # Prepare objects being aligned
  objects = [YObject(os.path.join(cachedir, "Object{}.pdb".format(num)), num, mols[i])
             for i, num in enumerate(objectnumbers)]
  for pdbfilename, objnum, _ in objects:
    yasara.SavePDB(objnum, pdbfilename)

  # run mmligner
  cwd = os.getcwd()
  os.chdir(cachedir)
  newobj = align_molecules(mmligner_bin, objects)
  os.chdir(cwd)

  # Cleanup
  disk.remove([os.path.join(cachedir, f) for f in os.listdir(cachedir)])
  
  # show LoadPDB message
  if isinstance(newobj, str):
    yasara.plugin.end(newobj)
  else:
    yasara.ShowMessage(SUCCESS_MESSAGE.format(newobj))

  # stop showing messages on screen        
  yasara.HideMessage()
  yasara.Wait(5,"Seconds")
    


# Main program
# ============
requests = {"CheckIfDisabled": disabled_check,
            "FileLocations": file_locations,
            "AlignMMLigner": run_mmligner}
try:
  requests[yasara.request]()
except KeyError:
  yasara.plugin.end("Unknown request: {}".format(yasara.request))


#=================================#

# stop the plugin, einde.
yasara.plugin.end()

#=================================#
