#!/usr/bin/env python3
# encoding: utf-8

import utiles
import analyse_lexicale
import re
import sys


#FICHIERS D'ENTREE#####################################################
if sys.argv[1]:
    txt_file_path = sys.argv[1]
else:
    txt_file_path = 'test/txt.txt'

stopword_file_path = 'test/stoplist_Fr.txt'
bootstrap_file_path = 'test/bootstrap'
schema_file_path = 'test/schema'
log_file_path = 'test/log'
stopword_pattern = utiles.stopword_regex(stopword_file_path)
etiq_text = utiles.etiquette_texte(txt_file_path, stopword_file_path, bootstrap_file_path)

# construire la liste cands à partir d'une recherche dans le dico des étiquettes et pas à partir du fichier bootstrap
with open(bootstrap_file_path, 'r', encoding = 'utf8') as fichierbootstrap:
    cands = utiles.construit_liste(fichierbootstrap)
print('BOOTSTRAP : ',cands)

with open(schema_file_path, 'r', encoding = 'utf8') as fichierschema:
    mots_schema = utiles.construit_liste(fichierschema)
    
########################################################################


#SEUILS#################################################################
seuil_simple = [3,5,5,10]
'''
Meme mot schema et même CAND
Meme mot schema et CAND differents
Mot schema different et même CAND
Mot schema different et CAND different
'''
seuil_expansion = 3
seuil_expression = 3
seuil_recession = min(seuil_expansion, seuil_expression, min(seuil_simple))
#########################################################################

with open(log_file_path, 'w', encoding = 'utf8') as log_file:
    log_file.write("FICHIER LOG\n")

i = 0
while i < 10:
    analyse_lexicale.recherche_simple(etiq_text, cands, mots_schema, seuil_simple, log_file_path)
    cands = utiles.recession(etiq_text, seuil_recession, log_file_path)
    analyse_lexicale.recherche_expansion(etiq_text, cands, mots_schema, stopword_pattern, seuil_expansion, log_file_path)
    cands = utiles.recession(etiq_text, seuil_recession, log_file_path)
    analyse_lexicale.recherche_expression(etiq_text, cands, mots_schema, seuil_expression, log_file_path)
    cands = utiles.recession(etiq_text, seuil_recession, log_file_path)
    i += 1

print(cands)

