#!/usr/bin/env python3
# encoding: utf-8

import ana_useful
import ana_collect
import re
import sys
import os
import ntpath

#FICHIERS D'ENTREE#####################################################
linkwords_file_path = 'french/schema'
stopword_file_path = 'french/stoplist_Fr.txt'
ana_useful.build_linklist(linkwords_file_path)
ana_useful.build_stoplist(stopword_file_path)
########################

txt_file_path_fromhere = 'memoire1_test2/text4ana.txt'
path = os.path.dirname(os.path.realpath(txt_file_path_fromhere))
os.chdir(path)

txt_file_path = ntpath.basename(txt_file_path_fromhere)
bootstrap_file_path = 'bootstrap'

if not os.path.exists('output/'):
	os.makedirs('output/')
log_file_path = 'output/log'

# construire la liste cands à partir d'une recherche dans le dico des étiquettes et pas à partir du fichier bootstrap
with open(bootstrap_file_path, 'r', encoding = 'utf8') as bootstrapfile:
    cands = ana_useful.build_bootlist(bootstrapfile)
print('BOOTSTRAP : ',cands)

dict_occ_ref = ana_useful.text2occ(txt_file_path)

########################################################################


#SEUILS#################################################################
# nucleus_threshold = [3,5,5,10]
# nucleus_threshold = [2,4,4,6]
nucleus_threshold = [1,2,2,3]
#this is just to catch, then if there are less than 3 occ oof the catched nucleus, it's erased
'''
Meme mot schema et même CAND
Meme mot schema et CAND differents
Mot schema different et même CAND
Mot schema different et CAND different
'''
expansion_threshold = 2
expression_threshold = 2
# recession_threshold = min(expansion_threshold, expression_threshold, min(nucleus_threshold))
recession_threshold = 3
#########################################################################

with open(log_file_path, 'w', encoding = 'utf8') as logfile:
    ana_useful.write_log(log_file_path,"########################################\n")
    ana_useful.write_log(log_file_path,"FICHIER LOG\n")
    ana_useful.write_log(log_file_path,"ANALYSE DU FICHIER : " + txt_file_path + "\n")
    ana_useful.write_log(log_file_path,"BOOTSTRAP : " + str(cands) + "\n")
    ana_useful.write_log(log_file_path,"########################################\n")


dict_expa = {}
dict_expre = {}

for nb_passe in range(1, 3):
    dict_expa = {}
    dict_expre = {}
    for nucleus_steps in range(1, 3):
        ana_useful.write_log(log_file_path,"\n\n########################################\n")
        ana_useful.write_log(log_file_path, 'passe __ n°' + str(nb_passe) + " RECHERCHE DE NOYAUX\n")
        ana_useful.write_log(log_file_path,"########################################\n")
        dict_nucleus = ana_collect.nucleus_search(dict_occ_ref, cands, nucleus_threshold, log_file_path)
        ana_useful.conflict_manager(dict_occ_ref, dict_nucleus, dict_expa, dict_expre, recession_threshold, log_file_path)
        cands = ana_useful.recession(dict_occ_ref, recession_threshold, log_file_path)

    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " RECHERCHE D'EXPANSIONS\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    dict_expa = ana_collect.expansion_search(dict_occ_ref, cands, expansion_threshold, log_file_path)

    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " RECHERCHE D'EXPRESSIONS\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    dict_expre = ana_collect.expression_search(dict_occ_ref, cands, expression_threshold, log_file_path)

    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " GESTION DE CONFLITS ET VALIDATION'\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    ana_useful.conflict_manager(dict_occ_ref, dict_nucleus, dict_expa, dict_expre, recession_threshold, log_file_path)
    old_len_cands = len(cands)
    cands = ana_useful.recession(dict_occ_ref, recession_threshold, log_file_path)
    diff = len(cands)-old_len_cands
    print('Variation du nombre de candidats :', diff)

    print('CANDIDATS \n step n°',nb_passe, '\n', cands, '\n\n################# step n°',nb_passe+1, '#################\n')

ana_useful.write_output(cands, dict_occ_ref)
