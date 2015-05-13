#!/usr/bin/env python3
# encoding: utf-8

import utiles
import analyse_lexicale
import re

txt_file_path = 'test/txt.txt'
stopword_file_path = 'test/stoplist_Fr.txt'
bootstrap_file_path = 'test/bootstrap'
stopword_pattern = utiles.stopword_regex(stopword_file_path)
etiq_text = utiles.etiquette_texte(txt_file_path, stopword_file_path, bootstrap_file_path)

with open(bootstrap_file_path, 'r', encoding = 'utf8') as fichierbootstrap:
    cand = fichierbootstrap.readlines()
    cands = list(map(lambda s: re.sub(r'\n', '', s), cand))
    analyse_lexicale.recherche_expansion(etiq_text,cands)
