#!/usr/bin/env python3
# encoding: utf-8

import math
import os
import re
import distance
from collections import Counter

#paramètre globaux ou initialisation#############################
seuil_egal_sple = 8

#ecrire log
def write_log(log_file_path, indication):
    with open(log_file_path, 'a', encoding = 'utf8') as logfile:
        logfile.write(indication + '\n')

#supprime l''accent de la première lettre du mot
#pas pour un problème d'encodage, mais pour un pb humain: les erreurs de "lettre non-accentué" en majuscule sont fréquentes. on veut : Île = Ile.
def accent_remove(lower_word):
    accent = ['é', 'è', 'ê', 'ë', 'ù', 'û', 'ü', 'ç', 'ô', 'ö', 'œ', 'î', 'ï', 'â', 'à', 'ä']
    wo_accent = ['e', 'e', 'e', 'e', 'u', 'u', 'u', 'c', 'o', 'o', 'oe', 'i', 'i', 'a', 'a', 'a']
    word = ''
    first_caracter = lower_word[0]
    lower_word2 = lower_word[1:]
    if first_caracter in accent:
        index = accent.index(first_caracter)
        first_caracter = first_caracter.replace(accent[index], wo_accent[index])
        if first_caracter in accent:
            print('ERREUR', first_caracter)
    word = first_caracter + lower_word2
    return word

#construit une regex de tous les stopWords
def stopword_regex(stopword_file_path):
    with open(stopword_file_path, 'r', encoding='utf8') as stopwordfile:
        stoplist = build_list(stopwordfile)
        #stoplist = map(lambda s: "\\b" + s + "\\b", stoplist)
        stopstring = '|'.join(stoplist)
        stopstring = '(?siu)' + '(' + stopstring + ')'
        stopword_pattern = re.compile(stopstring)
        return stoplist

# attention div#0 si word1 == word2
# utilisé pour egal_souple_term
# 
def close(word1, word2):
    totleng = len(word1) + len(word2)
    dist = distance.levenshtein(word1, word2)
    closeness = totleng / (seuil_egal_sple* dist)
    return closeness

#Prend 2 termes et retourne un booléen. Permet de définir si 2 termes sont égaux, en calculant une proximité entre eux. Un seuil de flexibilité est défini. ne tient pas compte des majuscules mais des accent oui. 
def egal_sple_term(word1, word2):
    souple = False
    if word1 != '' and word2 != '':
        word1 = accent_remove(word1.lower())
        word2 = accent_remove(word2.lower())
        if ((word1 == word2) or (word2 == word1 + 's') or (word1 == word2 + 's') or (word2 == word1 + 'e') or (word1 == word2 + 'e') or (word1 == word2 + 'es') or (word2 == word1 + 'es')):
            souple = True
        elif word2[0] != word1[0]:
            souple = False
        else:
            closeness = close(word1, word2)
            if closeness > 1:
                souple = True
    return souple

#Prend 2 chaînes et retourne un booléen. Permet de définir si 2 chaînes sont égales. Retire les mots de la `stoplist` contenu dans les chaïnes. Calcul la sommes des proximités des paires de mots (chaine A, chaine B contiennent les paires A1 B1; A2 B2; A3 B3).
def egal_sple_chain(string1, string2, stopword_pattern):
#    st1 = re.sub(stopword_pattern, '', string1)
#    st2 = re.sub(stopword_pattern, '', string2)
    st1 = []
    st2 = []
    string1 = string1.split()
    string2 = string2.split()
    for word in string1:
        word = word.lower()
        if word not in stopword_pattern:
            st1.append(word)
    for word in string2:
        word = word.lower()
        if word not in stopword_pattern:
            st2.append(word)
    souple = True
    if len(st1) != len(st2):
        souple = False
    else:
        for word in st1:
            if not egal_sple_term(st2[st1.index(word)], word):
                souple = False
    return souple

#prend un fichier ligne à ligne et construit une liste avec un élément dans la liste pour chaque ligne
#file object est le produit de `open`
def build_list(fileobject):
    lines = fileobject.readlines()
    list_out = list(map(lambda s: re.sub(r'\n', '', s), lines))
    return list_out
    
# in dict_occ_ref, the keys are 'position' and the values are [shape, status, history]. str shape; str status; list of occurrence(s) history
def text2occ(txt_file_path, stopword_file_path, bootstrap_file_path):
    dict_occ_ref = {}
    i = 0
    with open(txt_file_path, 'r', encoding = 'utf8') as txtfile:
        with open(stopword_file_path, 'r', encoding = 'utf8') as stopfile:
            with open(bootstrap_file_path, 'r', encoding = 'utf8') as bootstrapfile:
                text = txtfile.read()
                stoplist = build_list(stopfile)
                cands = build_list(bootstrapfile)
                #texte = re.sub('-', '_', texte) # pour éviter de perdre les traits d'union '-'
                separator = re.compile(r'\W+') #attention selon les distrib, W+ peut catcher les lettre accentuées comme des "non lettre"
                words = re.split(separator, text)
                for word in words:
                    lower_word = word.lower()
                    i += 1
                    marked = False
                    if (lower_word in stoplist) or (re.match(r'(\b\d+\b)', word) and not re.match(r'(1\d\d\d|20\d\d)', word)): #les chiffres sont des 'v' mais pas les dates.:
                        marked = True
                        dict_occ_ref[i] = [word, 'v', []] #the history is empty at the begining
                    for cand in cands:
                        egaux = egal_sple_term(cand, lower_word)
                        if egaux == True:
                            marked = True
                            dict_occ_ref[i] = [word, cand, []] #the history is empty at the begining
                    if marked == False:
                        dict_occ_ref[i] = [word, 't', []] #the history is empty at the begining
            return dict_occ_ref


#prend en paramètres: le dico des étiquettes, une liste de `CAND`, `width` (taille de la fenetre) et `w` (position du `CAND` dans la fenêtre (1, 2, 3 ou 4 souvent)) et sort une liste de toutes les suites d'étiquettes numérotées (une fenetre) correspondant aux critères: les fenêtres. Les étiquettes sont de la shortshape [indice, mot, typemot] dans les fenetres.
def define_windows(dict_occ_ref, candidates, width, cand_pos):
    windows = []
    before_cand = cand_pos-1 # nombre d'étiquette avant le candidat dans la fenetre
    after_cand = width-cand_pos # nombre d'étiquette apres le candidat dans la fenetre
    for cand in candidates:
        for key, value in iter(dict_occ_ref.items()):
            window =[]
            if cand == value[1]: #trouve les étiquettes contenant candidat dans le dico
                #construit une window composée d'étiquettes
                window.append([key,value[0],value[1], value[2]]) #ajoute l'occurrence du candidat trouvé
                count_bw = 0
                count_fw = 0
                key1 = key
                key2 = key
                # boucle pour insérer autant d'étiquettes que demandées (paramètres width et w) après le candidat (les stopwords (de type noté 'v') ne comptent pas)
                while count_fw < after_cand:
                    key1 +=1
                    if key1 in dict_occ_ref:
                        occurrence = [key1] + dict_occ_ref[key1]
                        window.append(occurrence) #insere les occurrence en fin de window. occurrence de la forme [indice, mot, typemot, history]
                        if occurrence[2] != 'v':
                            count_fw += 1
                # boucle pour insérer autant d'étiquettes que demandées (paramètres width et cand_pos) avant le candidat (les stopwords (de type noté 'v') ne comptent pas)
                while count_bw < before_cand:
                    key2 -=1
                    if key2 in dict_occ_ref:
                        occurrence = [key2] + dict_occ_ref[key2]
                        window.insert(0, occurrence) #insere les occurrence en début de window. occurrence de la forme [indice, mot, typemot, history]
                        if occurrence[2] != 'v':
                            count_bw += 1
                windows.append(window)  #met la window dans la liste des windows recherchées.
    return windows

def admission(dict_occ_ref, window, new_cand_shape, log_file_path):
    '''
    new_cand est une chaîne de caractères normalisée en fonction des cas:
    - expression
    - expansion
    - simple
    It only modifies one window (= works window per window = doesn't accept a list of windows)
    '''
    new_string_list = []
    
    # in case of a nucleus, the var window is actualy an occurrence 
    if isinstance(window[0], int):
        occurrence = window
        # in dict_occ_ref, the keys are 'position' and the values are [shape, status, history]. str shape; str status; list of window history
        history = dict_occ_ref[occurrence[0]][2] # catch the history of the occurrence that will be modify
        history.append(occurrence) #between brackets because it's a window composed of a single occurrence
        dict_occ_ref[occurrence[0]] = [occurrence[1], new_cand_shape, history]
#       write_log(log_file_path, "ETIQUETTE SIMPLE CHANGEE", new_cand, position)

    # in case of an expression, or expansion
    else:
        window.sort(key=lambda x: x[0]) #trie les occurrences de la window par ordre d'indice croissant . au cas où
        
        occurrence1 = window[0]
        new_position = occurrence1[0]
        new_history = []
        if new_position in dict_occ_ref: # sinon une opération de change etiquette a déjà été effectuée pendant cette passe à cet indice.
            for occurrence in window:
                position = occurrence[0]
                to_change = dict_occ_ref[position]
                new_string_list.append(to_change[0]) # catch the shapes of the occurrences concerned
                new_string = ' '.join(new_string_list)
                new_history.append(to_change[2]) # catch the history of the occurrences concerned
            history = dict_occ_ref[new_position][2] # catch the history of the occurrence that will be modify
            history.append(new_history) # rajoute à history le new_history
            dict_occ_ref[new_position] = [new_string, new_cand, history] # remplace la première étiquette de la window (en arg) par le new_string, le new_cand et update history
#            write_log(log_file_path, "ETIQUETTE CHANGEE", new_cand, new_indice)
            for occurrence in window[1:]:
                position = occurrence[0] # get the keys of the occ to delete
                del dict_occ_ref[position] # supprime les autres indices dans le dict_occ_ref
                write_log(log_file_path, '  OCCURRENCE RE-COMBINÉE : ' + str(occurrence) + ' ' + str(window))


#prend une window d'étiquette et supprime tout les mots de la stoplist contenu dans cette window. retourne une window_sans_v (sans linkwords)
#pas pour opérer mais pour faire des vérification de windows valides
def window_wo_fword(window):
    window_wo_fword = []
    for occurrence in window:
        if occurrence[2] != 'v':
            window_wo_fword.append(occurrence)
    return window_wo_fword

# Pour faire des calculs d'occurrence sans se préoccuper des indices
def window_wo_position(window):
    window_wo_pos = []
    for occ in window:
        window_wo_pos.append(occ[1:])
    return window_wo_pos

def symmetric_window(window):
    new_window = list(reversed(window))
    return new_window

def is_cand(occurrence):
    if occurrence[2] not in ['t', 'v']:
        return True
    else:
        return False
        
def count_cand(window):
    count_cand = 0
    for occurrence in window:
        if is_cand(occurrence):
            count_cand += 1
    return count_cand
    
def which_cand(window):
    for occurrence in window:
        if is_cand(occurrence):
            return occurrence
    
def exists_linkword(window, linkwords):
    exists_linkword = False
    for occurrence in window:
        if occurrence[1] in linkwords:
            exists_linkword = True
    return exists_linkword
    
def which_linkword(window, linkwords):
    for occurrence in window:
        if occurrence[1] in linkwords:
            return occurrence
        
#prend une liste de window candidates et retourne un tuple [string, int] contenant la shortshape la plus fréquente et son occurence
def new_cand(windows_cand_list):
    shape_list = []
    for window in windows_cand_list:
        shape = ''
        for occurrence in window:
            if occurrence[2] not in ['v', 't']:
                shape += occurrence[2] 
            else:
                shape += occurrence[1]
            shape += ' '
        shape_list.append(shape.strip())
    new_cand = min(shape_list, key=len).lower() # choose the shortest shape among the equivalent ones in windows_cand_list
    occ_count = len(windows_cand_list)
    return new_cand,occ_count #shortshape string et occurence de cette shortshape

def new_cand_nucleus(occ_cand_list):
    shortshape_list = []
    for occurrence in occ_cand_list:
        shortshape_list.append(occurrence[1].strip())
    new_cand = min(shortshape_list, key=len).lower()
    occ_count = len(occ_cand_list)
    return new_cand,occ_count #shortshape string et occurence de cette shortshape

# tronque une fenetre après un certain nombre de mot non "v"
def cut_window(window, lenght):
    count = 1
    short_window = []
    for occurrence in window:
        if count < lenght:
            short_window.append(occurrence)
        if occurrence[2] != 'v':
            count += 1
        if count == lenght:
            break
    return short_window

def recession(dict_occ_ref, threshold, log_file_path, stopword_pattern):
    cands = []
    dict_cand = {}
#1. build a dico, to count the occurrences of each candidate.
    for position, value in dict_occ_ref.items():
        if value[1] not in ['v', 't']:
            dict_cand.setdefault(value[1],[]).append(position) # ajoute la position de chaque forme candidate trouvé dans un dico, à la clef "candidat"
#old version
#            if value[1] in dict_cand:
#                dict_cand[value[1]].append(position)
#            else:
#                dict_cand[value[1]] = [position] # ajoute la position de chaque forme candidate trouvé dans un dico, à la clef "candidat"
#2. check if cand is still occuring in the dict_occ-ref
    for candidate, position_list in dict_cand.items():
        if len(position_list) >= threshold:
            cands.append(candidate)
        else: #supprime ce CAND et redécompose en étiquettes marquées 't'
            for position in position_list:
                #recupère le texte contenu dans cette etiquette CAND à supprimer
                last_history = dict_occ_ref[position][2].pop() #returns and remove last item of the history. last_histoy is a window of occurrences
                for occurrence in last_history:
                    replace_pos = occurrence[0]
                    replace_val = ocurrence[1:]
                    dict_occ_ref[replace_pos] = [replace_val]
                write_log(log_file_path, 'RECESSION de ' + str(candidate) + ' (' + str(position) + ') ' + ' vers ' + str(last_history))
                    
        #old version        
#                old_occurences = old_occurences.split() #liste de mots du texte contenu dans l'étiquette CAND
#                replace_pos = position
#                for old_occ in old_occurences:
#                    dict_occ_ref[replace_pos] = [old_occ, 't']
##                    write_log(log_file_path, 'MOT REMPLACE', dico_etiquettes[clef_replace], clef_replace)
#                    replace_pos += 1
#            write_log(log_file_path, 'MOT SUPPRIME ' + str(candidate) + ' ' + str(position_list))
    return cands
    
#p145 mais en différent! Pour modifier les étiquettes sans que les 3 modes de découverte de nouveau CAND se bousculent
#def heuristique(newcand_et_liste_fenetre_cand)
   

#get all the original positions of the occurences in a window
def get_pos(window):
    positions_list = []
    for occurrence in window:
        positions_list.append(occurrence[0])
    return positions_list

#sould return a list of all the occurrences (nucleuses) corresponding to the asked 'cand_shape'. 
#doit servir la construction du dico des nucleus
def where_R_nucleus(dict_occ_ref, cand_shape):
    occ_list = []    
    for position, value in dict_occ_ref.items():
        if ((value[1] == 't') and (egal_sple_term(value[0], cand_shape))): # Test on 't' word to avoid catching 'v' words (ie. 'il') for a candidate (ie. 'île')
            occurence = [position, value[0], value[1], value[2]]
            occ_list.append(occurence)
    return occ_list

        
        
'''
les dict_expa, dict_expre, dict_nucleus doivent être de la forme suivant: {new_cand:[occurences]}
le dict des nucleus doit peut-être être traité à part, et avant les autres pour favoriser l'exploration du texte.
'''
def conflict_gestion(dict_occ_ref, dict_nucleus, dict_expa, dict_expre, threshold, log_file_path):
    seen = []
    tampon = []
##### for the nucleuses
    # 1: building the dict containing all the occurences to modify in the dict_occ_ref
    all_nucleus_dict = {}
    for new_cand_shape in dict_nucleus:
        occ_list = where_R_nucleus(dict_occ_ref, new_cand_shape)
        all_nucleus_dict[new_cand_shape] = occ_list
    # 2: modify by most occuring form
    #sort the dictionary in a tuple (cand shape, [occ_list]), in which the first item contain the most occuring cand_shape. 
    #NB: the nucleuses are composed by a unique word, so a unique occurence, so there are no "windows" but only opccurences
    all_nucleus_ordered = sorted(all_nucleus_dict, key=lambda new_cand_shape: len(all_nucleus_dict[new_cand_shape]), reverse=True)
    for new_cand_shape in all_nucleus_ordered: # item is cand shape
        occurrences = all_nucleus_dict[new_cand_shape]
        for occ in occurrences:
            if occ[0] not in seen:
                seen.append(occ[0])
                admission(dict_occ_ref, occ, new_cand_shape, log_file_path)
        write_log(log_file_path, 'NUCLEUS ADMIS ' + str(new_cand_shape) + ' ' + str(len(occurrences)))

            
##### for the other new_cands
    all_cands_dict = {}
    all_cands_dict.update(dict_expa)
    all_cands_dict.update(dict_expre) #concatenante the 2 dicts
    
    seen = []
    tampon = []
    #trie le dictionnaire en un tuple (cand shape, [occ_list]) dont le premier item contient le cand_shape ayant le plus d'occurences
    print(all_cands_dict)
    all_candshape_ordered = sorted(all_cands_dict, key=lambda new_cand_shape: len(all_cands_dict[new_cand_shape]), reverse=True)
    
    for new_cand_shape in all_candshape_ordered:
        windows = all_cands_dict[new_cand_shape]
        passed = False #to know if the new_cand has been accepted
        seen_buff = [] #to count the number of accepted occurrences (not in conflict with a previous one)
        buff = []
        occ_count = threshold #initialized with the smallest possible. THe count begin when the threshold is crossed
        for window in windows:
            pos_list = get_pos(window)
            deja_vu =  any((True for x in pos_list if x in seen)) # doesn't enter in the loop if one of the position has allready be seen.
            if not deja_vu:
                if passed: # passed if true only if there are more than 3 elements to modify 
                    seen.extend(pos_list)
                    admission(dict_occ_ref, window, new_cand_shape, log_file_path)
                    occ_count += 1
                elif len(buff) < threshold:# until there are 3 elements to modify
                    buff += window
                    seen_buff.extend(pos_list)
                elif len(buff) == threshold: # where there are 3 elements to modify (threshold crossed)
                    seen.extend(seen_buff)
                    for window in buff: # admission only accepts one window
                        admission(dict_occ_ref, window, new_cand_shape, log_file_path)
                    passed = True
        if passed:
            write_log(log_file_path, 'CANDIDAT TROUVEE' + str(new_cand_shape) + ' ' + str(occ_count))
    
    
#    
#    
#    
#    
#    
