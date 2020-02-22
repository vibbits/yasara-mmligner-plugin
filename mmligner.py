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

# amino acid residue list
aminoacidDict = {}
aas = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y','y','p','s','z']

aas2 = ['ALA','CYS','ASP','GLU','PHE','GLY','HIS','ILE','LYS','LEU','MET','ASN','PRO','GLN','ARG','SER','THR','VAL','TRP','TYR','PTR','TPO','SEP','TYS']

nucs=['a','c','g','t','u']

for index in range( len(aas) ):
  aminoacidDict[ aas2[index ] ] = aas[index]

# set non-calculation requests so we don't clean the cache folder after these. 
noncalc = ['FileLocations']
# redundant files that can be removed when saving FoldX output to new folder
redundantfiles = ['PdbList_']

# Main program
# ============

# check if operating system is OK, otherwise disable the plugin
if (yasara.request=="CheckIfDisabled"): yasara.plugin.exitcode=0
  # ASSIGN A 1 TO yasara.plugin.exitcode IF THIS PLUGIN CANNOT WORK AND SHOULD
  # BE DISABLED (DATA MISSING, WRONG OPERATING SYSTEM ETC.)
  # check operating system

# *************************************************************************************************************************************************
# * set file locations of MMaligner binary, this section needs to be the first one, otherwise even this section will raise an error at the end *
# *************************************************************************************************************************************************
elif (yasara.request=="FileLocations"):
  xbinpath = yasara.selection[0].filename[0]
  # stop if wrong rotabase file was selected (just by filename)
  if not os.path.split(xbinpath)[-1] == 'mmligner64.exe':
    yasara.plugin.end("Invalid file. Download MMligner from http://lcb.infotech.monash.edu.au/mmligner/")
  lines = open("mmligner.cnf","r").readlines()
  output = open("mmligner.cnf","w")
  for line in lines:
    print(line)
    if line.startswith("MMLIGNER_BIN"): output.write("MMLIGNER_BIN = "+xbinpath+"\n")
    else: output.write(line)
  output.close()
# continue if OK, do some basic initializing
else:
  # check for path of MMligner binary
  if not os.path.exists(yasara.plugin.config["MMLIGNER_BIN"]):
    yasara.plugin.end("Cannot locate the MMligner executable file. Please click Analyze > Align > Configure plugin to select the MMligner executable file.")
  # hide Console for speed gain
  yasara.Console("Hidden")
  # set the cache dir
  cachedir = os.path.join(os.getcwd(),yasara.plugin.config["MMLIGNER_TMP"])
  # Delete temp folder only if a calculation is chosen. This saves the 'Save last calculation' plugin command from deletion after eg. FixResidues ...
  if yasara.request not in noncalc: disk.rmdir(cachedir)
  # make the cachedir if not already present
  if (not os.path.exists(cachedir)): disk.makedirs(cachedir,yasara.permissions)
  # get the mmligner executable absolute path and put double quotes around it to handle paths with spaces
  xbin='"'+yasara.plugin.config["MMLIGNER_BIN"]+'"'
  # put fixed residues in a list, this yasara command returns the unique atom number string (same as residue.number.inyas)
  fixedreslist = yasara.ListRes("Property=10000")

# ************************************************************************************
# * save the last calculation in a specified folder (copy entire cache folder there) *
# ************************************************************************************
if (yasara.request=="SaveCalc"):
  # grab the selected copy folder
  savetarget = yasara.selection[0].filename[0]
  # set the cache dir from the config file
  cachedir = os.path.join(os.getcwd(),yasara.plugin.config["FOLDX_TMP"])
  # remove redundant cache files. don't copy these to save folder
  for filename in redundantfiles:
    disk.remove(os.path.join(cachedir,filename))
  # check if the path is real
  try:
    # here we assume a folder and not a prefix was selected
    os.listdir(savetarget)
    targetfolder = savetarget
    targetprefix = ""
  except OSError:
    # here we assume a file prefix was given. check if underlying folder is real
    os.listdir(os.path.split(savetarget)[0])
    targetfolder = os.path.split(savetarget)[0]
    targetprefix = os.path.split(savetarget)[1]
  except:
    yasara.plugin.end("No proper folder was selected. You probably specified an unexisting folder.")
  # which files to copy?
  # all files
  cachelist = os.listdir(cachedir)
  # see if we don't overwrite any files. if so, do not continue
  copylist = os.listdir(targetfolder)
  for filename in cachelist:
    if targetprefix != "" and targetprefix != "*" and targetprefix+"_"+filename in copylist:
      yasara.plugin.end("Identical filenames found in source folder and selected save folder. Please empty the save folder or select a new save folder or choose another filename prefix to avoid overwriting.")
    elif (targetprefix == "" or targetprefix == "*") and filename in copylist:
      yasara.plugin.end("Identical filenames found in source folder and selected save folder. Please empty the save folder or select a new save folder or choose another filename prefix to avoid overwriting.")    
  # raise error when cache folder is empty
  if cachelist == []:
    yasara.plugin.end("No recent calculation found.")
  # copy the entire cache dir to the copy folder
  for filename in cachelist:
    disk.copy(os.path.join(cachedir,filename),os.path.join(targetfolder,filename))
    yasara.write("Downloaded "+filename+" from "+cachedir+" to "+targetfolder)

# **********
# * AlignMMLigner *
# **********
if (yasara.request=="AlignMMLigner"):
  # count molecules
  molcount = yasara.selection[0].molecules + yasara.selection[1].molecules
  # open a list to store all molecule descriptors
  allmols = []
  # make the list of molname selections, put all molecules from each selection in 1 string for FoldX
  mollist = []
  firstrange = ""
  
  for i in range(yasara.selection[0].molecules):
    firstrange += yasara.selection[0].molecule[i].name
    allmols.append(yasara.selection[0].molecule[i])
  secondrange = ""
  for i in range(yasara.selection[1].molecules):
    secondrange += yasara.selection[1].molecule[i].name
    allmols.append(yasara.selection[1].molecule[i])
  mollist.append(firstrange)
  mollist.append(secondrange)
  # molecules should belong to same object
  objectnumbers = [allmols[0].object.number.inyas, allmols[1].object.number.inyas]
  #for molecule in allmols:
  #  nextobjectnum = molecule.object.number.inyas
  #  if nextobjectnum != objectnumber:
  #    yasara.plugin.end("To calculate interaction energy, the molecules must be in the same object. Please try again and select molecules from one object.")
  # same molecule cannot occur in both selections
  #for mol in firstrange:
  #  if mol in secondrange:
  #    yasara.plugin.end("First and second selection cannot contain the same molecule "+mol)
  # no nameless molecules
  if firstrange.find(" ") != -1 or secondrange.find(" ") != -1:
    yasara.plugin.end("To calculate FoldX interaction energy, all molecules in the object should have unique names. Please rename all nameless molecules with Edit > Rename > Molecule.")
  # run analysecomplex
  newobjnumber = mmaligneralign.Align_Molecules(cachedir,xbin,mollist,objectnumbers)
  # make plot string of energy
  #intEnergy = foldxplotoutput.PlotAnalyseComplex_Molecules(cachedir,mollist,objectnumber)
  # make plot string of interface residues
  #intResidues = foldxutilities.ListInterfaceResidues(cachedir,objectnumber)
  # plot interface residues
  #yasara.write(intResidues)
  # plot interaction energy
  #yasara.write(intEnergy)
  
  # open the console
  yasara.Console("Open")
  # stop showing messages on screen        
  yasara.HideMessage()

#===================================================================================================================#

# stop the plugin, einde.
yasara.plugin.end()

#===================================================================================================================#
