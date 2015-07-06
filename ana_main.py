#!/usr/bin/env python3
# encoding: utf-8

import ana_useful
import ana_collect
import re
import sys


#FICHIERS D'ENTREE#####################################################
# if sys.argv[1]:
#     txt_file_path = sys.argv[1]
# else:
txt_file_path = 'test/txt.txt.cleaned'

stopword_file_path = 'test/stoplist_Fr.txt'
bootstrap_file_path = 'test/bootstrap'
linkwords_file_path = 'test/schema'
log_file_path = 'test/log'
stopword_pattern = ana_useful.stopword_regex(stopword_file_path)
dict_occ_ref = ana_useful.text2occ(txt_file_path, stopword_file_path, bootstrap_file_path)

# construire la liste cands à partir d'une recherche dans le dico des étiquettes et pas à partir du fichier bootstrap
with open(bootstrap_file_path, 'r', encoding = 'utf8') as bootstrapfile:
    cands = ana_useful.build_list(bootstrapfile)
print('BOOTSTRAP : ',cands)

with open(linkwords_file_path, 'r', encoding = 'utf8') as linkwordsfile:
    linkwords = ana_useful.build_list(linkwordsfile)

########################################################################


#SEUILS#################################################################
nucleus_threshold = [3,5,5,10]
'''
Meme mot schema et même CAND
Meme mot schema et CAND differents
Mot schema different et même CAND
Mot schema different et CAND different
'''
expansion_threshold = 3
expression_threshold = 3
recession_threshold = min(expansion_threshold, expression_threshold, min(nucleus_threshold))
#########################################################################

with open(log_file_path, 'w', encoding = 'utf8') as logfile:
    ana_useful.write_log(log_file_path,"########################################\n")
    ana_useful.write_log(log_file_path,"FICHIER LOG\n")
    ana_useful.write_log(log_file_path,"ANALYSE DU FICHIER : " + txt_file_path + "\n")
    ana_useful.write_log(log_file_path,"BOOTSTRAP : " + str(cands) + "\n")
    ana_useful.write_log(log_file_path,"########################################\n")

for nb_passe in range(1, 15):
    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path, 'passe n°' + str(nb_passe) + " RECHERCHE DE NOYAUX\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    dict_nucleus = ana_collect.nucleus_search(dict_occ_ref, cands, linkwords, nucleus_threshold, log_file_path)


    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " RECHERCHE D'EXPANSIONS\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    dict_expa = ana_collect.expansion_search(dict_occ_ref, cands, linkwords, stopword_pattern, expansion_threshold, log_file_path)


    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " RECHERCHE D'EXPRESSIONS\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    dict_expre = ana_collect.expression_search(dict_occ_ref, cands, linkwords, expression_threshold, log_file_path)

    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,"\n\n########################################\n")
    ana_useful.write_log(log_file_path,'passe n°' + str(nb_passe) + " GESTION DE CONFLITS ET VALIDATION'\n")
    ana_useful.write_log(log_file_path,"########################################\n")
    ana_useful.conflict_gestion(dict_occ_ref, dict_nucleus, dict_expa, dict_expre, recession_threshold, log_file_path)
    cands = ana_useful.recession(dict_occ_ref, recession_threshold, log_file_path, stopword_pattern)

    print(cands)
