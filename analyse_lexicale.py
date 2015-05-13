#!/usr/bin/env python3
# encoding: utf-8

import re
import utiles

def recherche_expansion(dico_etiquettes,candidats):
    fenetres = utiles.defini_fenetres(dico_etiquettes,candidats,3,2)
    #print(fenetres)
    fenetres_valides = []
    liste_cand = []
    seuil = 3
    for fenetre in fenetres:
        fenetre_propre = utiles.fenetre_sans_v(fenetre)
        # Le CAND est forcément en position 2 par construction et suppression des mots v
        if (fenetre_propre[0][2] == 't' and fenetre_propre[2][2] == 't'):
            fenetres_valides.append([fenetre_propre[0], fenetre_propre[1]])
            fenetres_valides.append([fenetre_propre[1], fenetre_propre[2]])
    for possible_cand in fenetres_valides:
        occurrence = 0
        for expansion in fenetres_valides:
            if possible_cand == expansion:
                occurrence +=1
        if ( (occurrence - 1) >= seuil):
            liste_cand.append(possible_cand)
    print(liste_cand)
