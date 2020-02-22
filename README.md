# yasara-mmligner-plugin

Initial version of the yasara plugin of MMligner 

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
# Version 1.0.0

Installation:

1. Download the binary of MMligner from http://lcb.infotech.monash.edu.au/mmligner/
2. Save it in a folder of your choice
3. Download the plugin and unzip it in the <yasara installation folder>/plg folder.
4. Start YASARA
5. Load any PDB file into YASARA
6. Configure the MMligner plugin via Analyse > Align > Configure MMligner plugin
7. Select the binary MMligner in the subsequent dialogue

Use:
1. Load two PDD files into YASARA
2. Align the structures via Analyse > Align > Molecules with MMligner
3. Select the target structure you would like to align the other molecule onto
4. Select the second structure
5. Wait until the alignment has succeeded
