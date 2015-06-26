#!/usr/bin/env python3
# encoding: utf-8

import re
import ana_useful
from math import *

##################################################################
# EXPANSION
##################################################################

def expansion_valid_window(windows, linkwords):
    valid_windows = []
    for window in windows:
        exists_linkword = False
        for occurrence in window:
            if ana_useful.is_cand(occurrence):
                pos_cand = window.index(occurrence)
            if occurrence[1] in linkwords:
                exists_linkword = True
        #Les expansions ne doivent pas contenir de mot de schéma
        if not exists_linkword:
            clean_window = ana_useful.window_wo_fword(window)
            # Le CAND est forcément en position 2 par construction et suppression des mots v
            if (clean_window[0][2] == 't' and clean_window[2][2] == 't'):
                valid_windows.append(window[:pos_cand+1])
                valid_windows.append(window[pos_cand:])
    return valid_windows

def expansion_cand_search(valid_windows, stopword_pattern, expansion_threshold):
    shape_list = []
    dict_cand_windows = {}
    norm_aword_list = []

    for window in valid_windows:
        shape = ''
        for occurrence in window:
            if (occurrence[2] not in ['t','v']):
                shape += occurrence[2]
                shape += ' '
            if (occurrence[2] == 't'):
                if norm_aword_list == []:
                    norm_aword_list.append(occurrence[1].lower())
                    shape += occurrence[1].lower()
                    shape += ' '
                else:
                    found = False
                    for norm_aword in norm_aword_list:
                        if ana_useful.egal_sple_term(norm_aword,occurrence[1]):
                            shape += norm_aword
                            shape += ' '
                            found = True
                            break
                    if found == False:
                        norm_aword_list.append(occurrence[1].lower())
                        shape += occurrence[1].lower()
                        shape += ' '
        shape_list.append(shape.strip())

    # Construction d'un dictionnaire de valid_windows pour chaque shape
    i = 0
    for shape1 in shape_list:
        dict_cand_windows.setdefault(shape1,[]).append(valid_windows[i])
#Old version
#        if shape1 not in dict_cand_windows:
#            dict_cand_windows[shape1] = [valid_windows[i]]
#        else:
#            dict_cand_windows[shape1] += [valid_windows[i]]
        i += 1

    # Vérification du dépassement de seuil, expansion est une "expansion potentielle" avant d'être validée et insérée dans le final_dict
    final_dict = {}
    for expansion in dict_cand_windows:
        if ( (len(dict_cand_windows[expansion])) >= expansion_threshold ):
            final_dict[expansion] = dict_cand_windows[expansion]
    return final_dict


def expansion_search(dict_occ_ref, candidates, linkwords, stopword_pattern, expansion_threshold, log_file_path):
    dict_expa = {}
    windows = ana_useful.define_windows(dict_occ_ref,candidates,3,2)

    valid_windows = expansion_valid_window(windows, linkwords)
    dict_cand_windows = expansion_cand_search(valid_windows, stopword_pattern, expansion_threshold)

    # Changer les étiquettes dans le texte
    for shape in dict_cand_windows:
        new_cand,occ_count = ana_useful.new_cand(dict_cand_windows[shape])
        ana_useful.write_log(log_file_path, 'EXPANSION TROUVEE ' + str(new_cand) + ' ' + str(occ_count))
        ana_useful.write_log(log_file_path, '   LISTE DES OCCURRENCES ')
        for window_cand in dict_cand_windows[shape]:
            ana_useful.write_log(log_file_path, '   ' + str(window_cand))
        dict_expa.setdefault(new_cand,[]).append(dict_cand_windows[shape])
    return dict_expa



#            ana_useful.admission(dict_occ_ref, window_cand, new_cand, log_file_path)

##################################################################
# EXPRESSION
##################################################################


#schema = [au, aux, d',de, du, des, en] pourquoi pas "avec"
#une fenetre valide ne contient que 2 CAND, séparés par un mot de schéma, avec éventuellement un mot 't' au milieu.
def expression_valid_window(window, candidates, linkwords):
    valid_window = []
    if (ana_useful.exists_linkword(window, linkwords) == True and ana_useful.count_cand(window) == 2):
        if ana_useful.is_cand(window[-1]):
            valid_window = window #dans ce cas la fenetre valide est de type (CAND1 + "mot quelconque" + CAND2) avec un mot de schéma quelque part.
        else:
            short_window = ana_useful.cut_window(window, 2)
            #Puisqu'on a 2 CAND et que la fenetre fait 3 mots et que le dernier mot n'est pas un CAND alors la fenetre était de type CAND + CAND + mot quelconque
            if ana_useful.exists_linkword(short_window, linkwords) == True:
                valid_window = short_window #dans ce cas la fenetre valide est de type (CAND1 + CAND2) avec un mot de schéma entre eux .
        return valid_window


'''return a dict that looks like {shortshape: [valid_windows]}
shortshape is composed of two candidates concatenanted CANDCAND (no awords, no stopwords)'''
def expression_find_cand(valid_windows, expression_threshold):
    shortshape_list = []
    dict_cand_windows = {}
    i = 0
    for window in valid_windows:
        shortshape = ''
        #créer une shortshape pour chaque fenetre. une shortshape est 'CANDCAND'
        #apriori toutes les shortshapes commenceront par le même cand (celui en argument de la fonction `recherche_expression`)
        for occurrence in window:
            if ana_useful.is_cand(occurrence):
                shortshape += occurrence[2]
        shortshape_list.append(shortshape) # l'ordre des shortshapes dans shortshape_list conserve l'ordre des fenetres in valid_windows

    for shortshape in shortshape_list:
        occ_count = shortshape_list.count(shortshape)
        if occ_count >= expression_threshold:
            dict_cand_windows.setdefault(shortshape,[]).append(valid_windows[i])
#old version
#            if shortshape in dict_cand_windows:
#                dict_cand_windows[shortshape] += [valid_windows[i]]
#            else:
#                dict_cand_windows[shortshape] = [valid_windows[i]]
        i += 1
    return dict_cand_windows


def expression_search(dict_occ_ref, candidates, linkwords, expression_threshold, log_file_path):
    dict_expre = {}
    for candidate in candidates:
        candidate = [candidate]
        windows = ana_useful.define_windows(dict_occ_ref, candidate, 3, 1) #fenetre du type `CAND1 + (cand ou mot quelconque) + (cand ou mot quelconque)`. Les mots stop ("v") ne sont pas représentés
        valid_windows = []
        windows_cand_list = []


        for window in windows:
            valid_window = expression_valid_window(window, candidate, linkwords)
            if valid_window: #évite les erreur dûes à une fenetre valide vide.
                valid_windows.append(valid_window)
        if valid_windows != []:
            dict_cand_windows = expression_find_cand(valid_windows, expression_threshold)
            if dict_cand_windows != {}:

                for shortshape, windows_cand_list in dict_cand_windows.items():
                    new_cand, occ_count = ana_useful.new_cand(windows_cand_list)
                    dict_expre.setdefault(new_cand,[]).append(windows_cand_list)

                    ana_useful.write_log(log_file_path, 'EXPRESSION TROUVEE ' + str(new_cand) + ' ' + str(occ_count))
                    ana_useful.write_log(log_file_path, '   LISTE DES OCCURRENCES ')

                    for window_cand in windows_cand_list:
                        ana_useful.write_log(log_file_path, '   ' + str(window_cand))
                        ana_useful.admission(dict_occ_ref, window_cand, new_cand, log_file_path)
    return dict_expre


##################################################################
# SIMPLE
##################################################################

#on cherche des mots rattachés à n'importe quel candidat par un mot de schéma. ex: couleurs de FLEUR, couleur de MUR, colleur de CARTON (c'est un exemple problematique)
# -> captera couleur.

#fait un dico de tous les mots trouvés (modulo une égalité souple)
def dict_found_words(valid_windows):
    dict_aword = {}
    # On ne peut pas modifier au fil de l'eau un dict sur lequel on itère
    # Donc on construit d'abord un dict avec tous les mots t
    # Peu importe s'ils sont égaux à l'égalité souple près

    for window in valid_windows:
        for occurrence in window: #a priori il n'y a qu'un seul t dans chaque fenetre'
            if occurrence[2] == 't':
                dict_aword.setdefault(occurrence[1],[]).append(window)
#                if occurrence[1] in dict_aword:
#                    dict_aword[occurrence[1]].append(window) # on garde toute la fenetre pour vérifier les différents seuils pour chaque clef.
#                else:
#                    dict_aword[occurrence[1]] = window

    # On nettoie le dico en utilisant l'égalité souple
    dict_aword_2 = {}
    done = []
    for aword in dict_aword.keys():
        if aword not in done:
            dict_aword_2[aword] = dict_aword[aword]
            for aword2 in dict_aword.keys():
                if aword != aword2 and ana_useful.egal_sple_term(aword, aword2):
                    dict_aword_2[aword].extend(dict_aword[aword2])
                    done.append(aword2)

    # trouve la shortshape collectant le plus d'occurence parmis toutes les shortshapes en égalité souple.
    # comme pour ranger une liste, on a un buff qui stocke la shortshape rattachée au plus d'occurrence.
    # dico final est donc de la même shortshape que dict_aword ou dict_aword_2, à savoir, {'mot quelconque': [valid_windows]}
    final_dict = {}
    for aword in dict_aword_2.keys():
        buff = {}
        for aword2 in dict_aword_2.keys():
            if ana_useful.egal_sple_term(aword, aword2):
                if len(dict_aword_2[aword]) > len(dict_aword_2[aword2]):
                    if (aword not in buff):
                        buff[aword] = dict_aword_2[aword]
                        if aword2 in buff and aword != aword2:
                            del(buff[aword2])
                else:
                    if (aword2 not in buff):
                        buff[aword2] = dict_aword_2[aword2]
                        if aword in buff and aword != aword2:
                            del(buff[aword])
        if list(buff.keys())[0] not in final_dict:
            final_dict.update(buff)
    return final_dict

def nucleus_find_cand(dict_aword, nucleus_threshold, linkwords):
    dict_occ_cand = {}
    for shortshape, windows in dict_aword.items():
        for window in windows:
            count_s1 = 0 #Meme mot schema et même CAND
            count_s2 = 0 #Meme mot schema et CAND differents
            count_s3 = 0 #Mot schema different et même CAND
            count_s4 = 0 #Mot schema different et CAND different
            linkword = ana_useful.which_linkword(window, linkwords)
            cand = ana_useful.which_cand(window)

            for window1 in windows:
                if window1 != window:
                    linkword1 = ana_useful.which_linkword(window1, linkwords)
                    cand1 = ana_useful.which_cand(window1)
                    # TODO supprimer les doublons

                    if linkword[1] == linkword1[1] and cand[2] == cand1[2]:
                        count_s1 += 1
                    elif linkword[1] == linkword1[1] and cand[2] != cand1[2]:
                        count_s2 += 1
                    elif linkword[1] != linkword1[1] and cand[2] == cand1[2]:
                        count_s3 += 1
                    elif linkword[1] != linkword1[1] and cand[2] != cand1[2]:
                        count_s4 += 1
        if count_s1 >= nucleus_threshold[0] or count_s2 >= nucleus_threshold[1] or count_s3 >= nucleus_threshold[2] or count_s4 >= nucleus_threshold[3]:
            for window in windows:
                for occurrence in window:
                    if occurrence[2] == 't':
                        dict_occ_cand.setdefault(shortshape, []).append(occurrence)
    return dict_occ_cand



#doit retourner la fenetre tronquée valide contenant un mot (non CAND) lié à un CAND par un mot schéma (après ce CAND) ou none si ne trouve rien.
def simple_valid_window(window, linkwords):
    if ana_useful.exists_linkword(window, linkwords):
        for occurrence in window:
            index_cand = 0
            if ana_useful.is_cand(occurrence):
                index_cand = window.index(occurrence)
                break
        right_window = window[index_cand:]
        if ana_useful.count_cand(right_window) < 2 and ana_useful.exists_linkword(right_window, linkwords):
            return right_window

def nucleus_search(dict_occ_ref, candidates, linkwords, nucleus_threshold, log_file_path):
    dict_nucleus = {}
    windows = ana_useful.define_windows(dict_occ_ref, candidates, 3, 2)
    valid_windows = []
    for window in windows:
        valid_window = simple_valid_window(window, linkwords)
        if valid_window:
            valid_windows.append(valid_window)
        windowR = ana_useful.symmetric_window(window)
        valid_windowR = simple_valid_window(windowR, linkwords)
        if valid_windowR:
            valid_window = ana_useful.symmetric_window(valid_windowR)
            valid_windows.append(valid_window)

    dict_aword = dict_found_words(valid_windows)
    dict_occ_cand = nucleus_find_cand(dict_aword, nucleus_threshold, linkwords)

    if dict_occ_cand != {}:
        for shortshape, occ_cand_list in dict_occ_cand.items():
            new_cand, occ_count = ana_useful.new_cand_nucleus(occ_cand_list)
            dict_nucleus.setdefault(new_cand,[]).append(occ_cand_list)

            ana_useful.write_log(log_file_path, 'NOYAU TROUVE ' + str(new_cand) + ' ' + str(occ_count))
            # TODO retrouver les fenetres valides qui ont permis de créer le noyau
            ana_useful.write_log(log_file_path, '   LISTE DES OCCURRENCES')
            for occ_cand in occ_cand_list:
                ana_useful.write_log(log_file_path, '   ' + str(occ_cand))
            #print('SIMPLE TROUVE', shortshape, occ_cand_list)

            occ_cand = occ_cand_list[0] #cela sert juste à savoir que le parametre que l'on envoie dans la fonction change etiquette est une etiquette simple et pas une fenetre (composée d'étiquettes). Le contenu de cette variable est de la shortshape d'une etiquette, qu'importe le contenu.
            ana_useful.admission(dict_occ_ref, occ_cand, new_cand, log_file_path)
    return dict_nucleus
