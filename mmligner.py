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
#!/usr/bin/python
import yasara,string,disk,os
import mmaligneralign
#import mmlignerutilities,mmlignerplotoutput

from python2to3 import *

# set non-calculation requests so we don't clean the cache folder after these. 
noncalc = ['FileLocations']
# redundant files that can be removed when saving FoldX output to new folder
redundantfiles = ['PdbList_']
# MMLigner absolute path
mmligner_bin = ""


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
  # count molecules
  molcount = yasara.selection[0].molecules + yasara.selection[1].molecules

  # make the list of molname selections
  # put all molecules from each selection in 1 string
  mollist = [
    "".join([molecule.name for molecule in yasara.selection[0].molecule]),
    "".join([molecule.name for molecule in yasara.selection[1].molecule])
    ]

  # molecules should belong to same object
  objectnumbers = [yasara.selection[0].molecule[0].object.number.inyas,
                   yasara.selection[1].molecule[0].object.number.inyas]

  # set the cache dir from the config file
  cachedir = os.path.join(os.getcwd(), yasara.plugin.config["MMLIGNER_TMP"])

  # run mmligner
  newobjnumber = mmaligneralign.Align_Molecules(cachedir, mmligner_bin, mollist, objectnumbers)

  # stop showing messages on screen        
  yasara.HideMessage()


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
