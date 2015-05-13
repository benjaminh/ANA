#!/usr/bin/env python3
# encoding: utf-8

import math
import os
import re
import distance
from collections import Counter

#paramètre globaux ou initialisation#############################
seuil_egal_sple = 8
stopword_pattern = (r'') #sera utilisé comme var globale. (première fonction lancée)


#construit une regex de tous les stopWords
def stopword_regex(stopword_file_path):
    with open(stopword_file_path, 'r', encoding='utf8') as stopwordfile:
        stoplist = construit_liste(stopwordfile)
        stoplist = map(lambda s: "\\b" + s + "\\b", stoplist)
        stopstring = '|'.join(stoplist)
        stopword_pattern = re.compile(stopstring, re.U)

# attention div#0 si mot1 == mot2
# utilisé pour egal_souple_term
def prox(motA, motB):
    mot1 = motA.lower()
    mot2 = motB.lower()
    totleng = len(mot1) + len(mot2)
    dist = distance.levenshtein(mot1, mot2)
    proxim = totleng / (seuil_egal_sple* dist)
    return proxim

#Prend 2 termes et retourne un booléen. Permet de définir si 2 termes sont égaux, en calculant une proximité entre eux. Un seuil de flexibilité est défini. ne tient pas compte des majuscules mais des accent oui. 
def egal_sple_term(mot1, mot2):
    souple = False
    if ((mot1 == mot2) or (mot1 == mot2 + 's') or (mot1 == mot2 + 's')):
        souple = True
    else:
        proximite = prox(mot1, mot2)
        if proximite > 1:
            souple = True
    return souple

#Prend 2 chaînes et retourne un booléen. Permet de définir si 2 chaînes sont égales. Retire les mots de la `stoplist` contenu dans les chaïnes. Calcul la sommes des proximités des paires de mots (chaine A, chaine B contiennent les paires A1 B1; A2 B2; A3 B3).
def egal_sple_chain(chaine1, chaine2):
    ch1 = re.sub(stopword_pattern, '', chaine1)
    ch2 = re.sub(stopword_pattern, '', chaine2)
    ch1 = chaine1.split()
    ch2 = chaine2.split()
    souple = True
    if len(ch1) != len(ch2):
        souple = False
    else:
        for mot in ch1:
            if not egal_sple_term(ch2[ch1.index(mot)], mot):
                souple = False
    return souple

#prend un fichier ligne à ligne et construit une liste avec un élément dans la liste pour chaque ligne
#file object est le produit de `open`
def construit_liste(fileobject):
    lignes = fileobject.readlines()
    liste = list(map(lambda s: re.sub(r'\n', '', s), lignes))
    liste.pop()
    return liste
    
def etiquette_texte(txt_file_path, stopword_file_path, bootstrap_file_path):
    dico_etiq = {}
    i = 0
    with open(txt_file_path, 'r', encoding = 'utf8') as fichiertxt:
        with open(stopword_file_path, 'r', encoding = 'utf8') as fichierstop:
            with open(bootstrap_file_path, 'r', encoding = 'utf8') as fichierbootstrap:
                texte = fichiertxt.read()
                stoplist = construit_liste(fichierstop)
                cands = construit_liste(fichierbootstrap)
                #texte = re.sub('-', '_', texte) # pour éviter de perdre les traits d'union '-'
                separateur = re.compile(r'\W+') #attention selon les distrib, W+ peut catcher les lettre accentuées comme des "non lettre"
                mots = re.split(separateur, texte)
                mots.pop()
                for mot in mots:
                    motlower = mot.lower()
                    i += 1
                    marked = False
                    if motlower in stoplist:
                        marked = True
                        dico_etiq[i] = [mot, 'v']
                    for cand in cands:
                        egaux = egal_sple_term(cand, motlower)
                        if egaux == True:
                            marked = True
                            dico_etiq[i] = [mot, cand]
                    if marked == False:
                        dico_etiq[i] = [mot, 't']
            return dico_etiq


#prend en paramètres: le dico des étiquettes, une liste de `CAND`, `W` (taille de la fenetre) et `w` (position du `CAND` dans la fenêtre (1, 2, 3 ou 4 souvent)) et sort une liste de toutes les suites d'étiquettes numérotées (une fenetre) correspondant aux critères: les fenêtres. Les étiquettes sont de la forme [indice, mot, typemot] dans les fenetres.
def defini_fenetres(dico, liste_CAND, W, w):
    fenetres = []
    av_cand = w-1 # nombre d'étiquette avant le candidat dans la fenetre
    ap_cand = W-w # nombre d'étiquette apres le candidat dans la fenetre
    for cand in liste_CAND:
        for key, value in iter(dico.items()):
            fenetre =[]
            if cand == value[1]: #trouve les étiquettes contenant candidat dans le dico
                #construit une fenetre composée d'étiquettes
                fenetre.append([key,value[0],value[1]]) #ajoute l'étiquette du candidat trouvé
                comptAv = 0
                comptAp = 0
                key1 = key
                key2 = key
                # boucle pour insérer autant d'étiquettes que demandées (paramètres W et w) après le candidat (les stopwords (de type noté 'v') ne comptent pas)
                while comptAp < ap_cand:
                    key1 +=1
                    if key1 in dico:
                        etiquette = [key1] + dico[key1]
                        fenetre.append(etiquette) #insère les étiquettes en fin de fenetre. etiquette de la forme [indice, mot, typemot]
                        if etiquette[2] != 'v':
                            comptAp += 1
                # boucle pour insérer autant d'étiquettes que demandées (paramètres W et w) avant le candidat (les stopwords (de type noté 'v') ne comptent pas)
                while comptAv < av_cand:
                    key2 -=1
                    if key2 in dico:
                        etiquette = [key2] + dico[key2]
                        fenetre.insert(0, etiquette) #insere les étiquettes en début de fenetre. etiquette de la forme [indice, mot, typemot]
                        if etiquette[2] != 'v':
                            comptAv += 1
                fenetres.append(fenetre)  #met la fenetre dans la liste des fenetres recherchées.
    return fenetres

def change_etiquette(dico, fenetre, new_cand):
    '''
    new_cand est une châine de caractères normalisée en fonction des cas:
    - expression
    - expansion
    - simple
    '''
    new_string_list = []
    fenetre.sort(key=lambda x: x[0]) #trie les étiquette de la fenetre par ordre d'indice croissant . au cas où
    
    etiquette1 = fenetre[0]
    new_indice = etiquette1[0]
    
    for etiquette in fenetre:
        indice = etiquette[0]
        to_change = dico[indice]
        new_string_list.append(to_change[0])
        new_string = ' '.join(new_string_list)
    dico[new_indice] = [new_string, new_cand] # remplace la première étiquette de la fenetre par le new_string et le new_cand
        
    for etiquette in fenetre[1:]:
        indice = etiquette[0]
        del dico[indice] # supprime les autres indices dans le dico

    
#prend une fenetre d'étiquette et supprime tout les mots de la stoplist contenu dans cette fenetre. retourne une fenetre_sans_v (sans mots_schema)
#pas pour opérer mais pour faire des vérification de fenetres valides
def fenetre_sans_v(fenetre):
    fenetre_sans_v = []
    for etiquette in fenetre:
        if etiquette[2] != 'v':
            fenetre_sans_v.append(etiquette)
    return fenetre_sans_v

def symetrique_fenetre(fenetre):
    new_fenetre = list(reversed(fenetre))
    return new_fenetre

def est_un_cand(etiquette):
    if etiquette[2] not in ['t', 'v']:
        return True
    else:
        return False
        
#prend une liste de fenetre candidates et retourne un string contenant la forme la plus fréquente
def new_cand(liste_fenetres_cand):
    liste_formes = []
    for fenetre in liste_fenetres_cand:
        forme = ''
        for etiquette in fenetre: 
            if etiquette[2] not in ['v', 't']:
                forme += etiquette[2] 
            else:
                forme += etiquette[1]
        forme += ' '
        liste_formes.append(forme)
    mostcommon = Counter(liste_formes).most_common(1) #mostcommon est une liste de 1 tuple [('forme', occurence)]
    themostcommon = mostcommon[0] 
    return themostcommon[0]

    
    
    
