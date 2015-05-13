#!/usr/bin/env python3
# encoding: utf-8

import re
import utiles


##################################################################
# EXPANSION
##################################################################

def recherche_expansion(dico_etiquettes,candidats):
    fenetres = utiles.defini_fenetres(dico_etiquettes,candidats,3,2)
    fenetres_valides = []
    liste_fenetres_cand = []
    liste_forme = []
    seuil = 2
    i = 0
    for fenetre in fenetres:
        fenetre_propre = utiles.fenetre_sans_v(fenetre)
        # Le CAND est forcément en position 2 par construction et suppression des mots v
        if (fenetre_propre[0][2] == 't' and fenetre_propre[2][2] == 't'):
            fenetres_valides.append([fenetre_propre[0], fenetre_propre[1]])
            fenetres_valides.append([fenetre_propre[1], fenetre_propre[2]])
    for possible_cand in fenetres_valides:
        forme1 = ''
        forme2 = ''
        for etiquette in possible_cand:
            if (etiquette[2] == 't'):
                forme1 += etiquette[1]
            else:
                forme2 += etiquette[2]
        liste_forme.append(forme1+forme2)
    # Vérification du dépassement de seuil
    occurrence = 0
    for forme in liste_forme:
        occurrence = liste_forme.count(forme)
        if ( occurrence >= seuil ):
            liste_fenetres_cand.append(fenetres_valides[i])
        i += 1
    # Changer les étiquettes dans le texte
    for fenetre_cand in liste_fenetres_cand:
        new_cand = fenetre_cand[0][1] + ' ' + fenetre_cand[1][2]
        utiles.change_etiquette(dico_etiquettes, fenetre_cand, new_cand)
    return liste_fenetres_cand

##################################################################
# EXPRESSION
##################################################################

#schema = [de, du, des, en] pourquoi pas "avec"
#une fenetre valide ne contient que 2 CAND, séparés par un mot de schéma, avec éventuellement un mot 't' au milieu. 
def expression_fenetre_valide(fenetre,cand,schema):
    valide =[]
    compte_cand = 0
    schema_present = False

    for etiquette in fenetre:
        if compte_cand < 2:
            if etiquette[2] in schema:
                schema_present = True
            if utiles.est_un_cand(etiquette):
                compte_cand += 1 # capte forcément le premier candidat, qui sera identique dans toutes les fenetres. (voir le focntionnement de utiles.defini_fenetres)
            valide.append(etiquette)
    if (schema_present == True and compte_cand == 2):
        return valide

def expression_repere_cand(fenetres_valides, seuil):
    liste_forme = []
    liste_cand = []
    i = 0
    for fenetre in fenetres_valides:
        forme = ''
        #créer une forme pour chaque fenetre. une forme est 'CANDCAND'
        #apriori toutes les formes commenceront par le même cand (celui en argument de la fonction `recherche_Expression`)
        for etiquette in fenetre:
            if utiles.est_un_cand(etiquette):
                forme += etiquette[2] 
        liste_forme.append(forme) # l'ordre des formes dans liste_forme conserve l'ordre des fenetres in fenetres_valides
        
    for forme in liste_forme:
        i += 1
        occ = liste_forme.count(forme)
        if occ >= seuil:
            liste_cand.append(fenetres_valides[i])
    return liste_cand
   
def recherche_expression(dico_etiquettes,candidat,schema):
    fenetres = utiles.defini_fenetres(dico_etiquettes,candidat,3,1) #feentre du type `CAND1 + (cand ou mot quelconque) + (cand ou mot quelconque)`. Les mots stop ("v") ne sont pas représentés
    fenetres_valides = []
    liste_cand = []
    seuil = 3
    for fenetre in fenetres:
        fenetres_valides.append(expression_fenetre_valide(fenetre,candidat,schema))
    liste_cand = expression_repere_cand(fenetres_valides, seuil)


##################################################################
# SIMPLE
##################################################################

#def simple_fenetre_valide(fenetre,schema,candidats):
#    for etiquette in fenetre:
#        if (etiquette[2] in schema):
#            mot_schema = etiquette
#        schema_index = fenetre.index(mot_schema)
#        if (fenetre[schema_index-1] == 't' or est_un_cand(fenetre[schema_index-1] or (fenetre[schema_index-1] == 'v' and (fenetre[schema_index-2] == 't' or est_un_cand(fenetre[schema_index-2]))
#        and (fenetre[schema_index+1] == 't' or est_un_cand(fenetre[schema_index+1] or (fenetre[schema_index+1] == 'v' and (fenetre[schema_index+2] == 't' or est_un_cand(fenetre[schema_index+2])):
#            return True
#        else return False
    
#def recherche_simple(dico_etiquettes,candidats,schema):
#    fenetres = utiles.defini_fenetres(dico_etiquettes,candidats,5,3)
#    fenetres_valides = []
#    liste_cand = []
#    seuil = [3,5,5,10]
#    for fenetre in fenetres:
#        if simple_fenetre_valide(fenetre) and simple_fenetre_valide(symetrique_fenetre(fenetre)):
#            fenetres_valides.append(fenetre)
    


