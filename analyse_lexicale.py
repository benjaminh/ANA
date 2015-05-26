#!/usr/bin/env python3
# encoding: utf-8

import re
import utiles
from math import *

##################################################################
# EXPANSION
##################################################################

def recherche_expansion(dico_etiquettes, candidats , mots_schema, stopword_pattern):
    fenetres = utiles.defini_fenetres(dico_etiquettes,candidats,3,2)
    fenetres_valides = []
    liste_fenetres_cand = []
    liste_forme = []
    seuil = 2
    i = 0
    for fenetre in fenetres:
        presence_schema = False
        for etiquette in fenetre:
            if utiles.est_un_cand(etiquette):
                pos_cand = fenetre.index(etiquette)
            if etiquette[1] in mots_schema:
                presence_schema = True
        #Les expansions ne doivent pas contenir de mot de schéma
        if not presence_schema:
            fenetre_propre = utiles.fenetre_sans_v(fenetre)
            # Le CAND est forcément en position 2 par construction et suppression des mots v
            if (fenetre_propre[0][2] == 't' and fenetre_propre[2][2] == 't'):
                fenetres_valides.append(fenetre[:pos_cand+1])
                fenetres_valides.append(fenetre[pos_cand:])
    for possible_cand in fenetres_valides:
        forme = ''
        for etiquette in possible_cand:
            if (etiquette[2] in ['t','v']):
                forme += etiquette[1]
            else:
                forme += etiquette[2]
            forme += ' '
        liste_forme.append(forme.strip())
    # Vérification du dépassement de seuil
    for forme1 in liste_forme:
        occurrence = 0
        # Compter le nombre d'occurence à l'égalité souple près
        for forme2 in liste_forme:
            if (utiles.egal_sple_chain(forme1,forme2, stopword_pattern)):
                occurrence += 1
        if ( (occurrence) >= seuil ):
            liste_fenetres_cand.append(fenetres_valides[i])
            print('EXPANSION TROUVEE : ', forme1, ' ', occurrence)
        i += 1

    # Changer les étiquettes dans le texte
    liste_fenetres_cand_sans_indices = [utiles.fenetre_sans_indice(fenetre) for fenetre in liste_fenetres_cand]
    for fenetre_cand in liste_fenetres_cand:
        # Vérification de la présence d'une étiquette de candidat dans une unique fenêtre (les fenêtres étant tronquées autour des candidats)
        # Si deux fenêtres se chevauchent avec le même candidat, prendre la forme qui a la plus grande occurrence
        # Sinon, en choisir une au hasard
        for etiquette in fenetre_cand:
            if utiles.est_un_cand(etiquette):
                cand = etiquette
        for fenetre in liste_fenetres_cand:
            # Détection d'un chevauchement
            if (cand in fenetre and fenetre_cand != fenetre):
                print('CHEVAUCHEMENT : ',fenetre_cand , ' et ', fenetre)
                cand_fenetre_occ = liste_fenetres_cand_sans_indices.count(utiles.fenetre_sans_indice(fenetre_cand))
                autre_fenetre_occ = liste_fenetres_cand_sans_indices.count(utiles.fenetre_sans_indice(fenetre))
                if (cand_fenetre_occ >= autre_fenetre_occ):
                    liste_fenetres_cand.pop(liste_fenetres_cand.index(fenetre))
                else:
                    liste_fenetres_cand.pop(liste_fenetres_cand.index(fenetre_cand))
    for fenetre_cand in liste_fenetres_cand:
        # TODO prendre en compte les nouveaux candidats du type "terme + (n * v) + CAND" par exemple
        # ex: labels et APPELLATIONS devient LABELS ET APPELLATIONS
        new_forme = ''
        for etiquette in fenetre_cand:
            if (etiquette[2] in ['t','v']):
                new_forme += etiquette[1]
            else:
                new_forme += etiquette[2]
            new_forme += ' '
        new_cand = new_forme
        utiles.change_etiquette(dico_etiquettes, fenetre_cand, new_cand)
    return liste_fenetres_cand

##################################################################
# EXPRESSION
##################################################################


#schema = [au, aux, d',de, du, des, en] pourquoi pas "avec"
#une fenetre valide ne contient que 2 CAND, séparés par un mot de schéma, avec éventuellement un mot 't' au milieu. 
def expression_fenetre_valide(fenetre,cand,schema):
    fenetre_valide = []
    if (utiles.schema_present(fenetre, schema) == True and utiles.compte_cand(fenetre) == 2):
        if utiles.est_un_cand(fenetre[-1]):
            fenetre_valide = fenetre #dans ce cas la fenetre valide est de type (CAND1 + "mot quelconque" + CAND2) avec un mot de schéma quelque part.
        else:
            fenetre_tronque = utiles.tronque_fenetre(fenetre, 2) 
            #Puisqu'on a 2 CAND et que la fenetre fait 3 mots et que le dernier mot n'est pas un CAND alors la fenetre était de type CAND + CAND + mot quelconque
            if utiles.schema_present(fenetre_tronque, schema) == True:
                fenetre_valide = fenetre_tronque #dans ce cas la fenetre valide est de type (CAND1 + CAND2) avec un mot de schéma entre eux .
        return fenetre_valide

def expression_repere_cand(fenetres_valides, seuil):
    liste_forme = []
    liste_fenetres_cand = []
    i = 0
    for fenetre in fenetres_valides:
        forme = ''
        #créer une forme pour chaque fenetre. une forme est 'CANDCAND'
        #apriori toutes les formes commenceront par le même cand (celui en argument de la fonction `recherche_expression`)
        for etiquette in fenetre:
            if utiles.est_un_cand(etiquette):
                forme += etiquette[2]
        liste_forme.append(forme) # l'ordre des formes dans liste_forme conserve l'ordre des fenetres in fenetres_valides
        
    for forme in liste_forme:
        occ = liste_forme.count(forme)
        if occ >= seuil:
            liste_fenetres_cand.append(fenetres_valides[i])
        i += 1
    return liste_fenetres_cand
   
def recherche_expression(dico_etiquettes,candidats,schema):
    for candidat in candidats:
        candidat = [candidat]
        fenetres = utiles.defini_fenetres(dico_etiquettes,candidat,3,1) #fenetre du type `CAND1 + (cand ou mot quelconque) + (cand ou mot quelconque)`. Les mots stop ("v") ne sont pas représentés
        fenetres_valides = []
        liste_fenetres_cand = []
        seuil = 2
        for fenetre in fenetres:
            fenetre_valide = expression_fenetre_valide(fenetre,candidat,schema)
            if fenetre_valide: #évite les erreur dûes à une fenetre valide vide.
                fenetres_valides.append(fenetre_valide)
        if fenetres_valides != []:
            liste_fenetres_cand = expression_repere_cand(fenetres_valides, seuil)
            if liste_fenetres_cand != []:
                new_cand, occurrence = utiles.new_cand(liste_fenetres_cand)
                print('EXPRESSION TROUVEE : ', new_cand, ' ', occurrence)
                for fenetre_cand in liste_fenetres_cand:
                    utiles.change_etiquette(dico_etiquettes, fenetre_cand, new_cand)

##################################################################
# SIMPLE
##################################################################

#on cherche des mots rattachés à n'importe quel candidat par un mot de schéma. ex: couleurs de FLEUR, couleur de MUR, colleur de CARTON (c'est un exemple problematique)
# -> captera couleur. 

#fait une liste de tous les mots trouvés (modulo une égalité souple)
def dico_mots_trouves(fenetres_valides):
    dico_t = {}
    # On ne peut pas modifier au fil de l'eau un dict sur lequel on itère
    # Donc on construit d'abord un dict avec tous les mots t
    # Peu importe s'ils sont égaux à l'égalité souple près
    for fenetre in fenetres_valides:
        for etiquette in fenetre: #a priori il n'y a qu'un seul t dans chaque fenetre'
            if etiquette[2] == 't':
                if etiquette[1] in dico_t:
                    dico_t[etiquette[1]].extend([fenetre])
                else:
                    dico_t[etiquette[1]] = [fenetre]
    # On nettoie le dico en utilisant l'égalité souple
    dico_t_2 = {}
    deja_fait = []
    for t in dico_t.keys():
        if t not in deja_fait:
            dico_t_2[t] = dico_t[t]
            for t2 in dico_t.keys():
                if t != t2 and utiles.egal_sple_term(t, t2):
                    dico_t_2[t].extend(dico_t[t2])
                    deja_fait.append(t2)

    dico_final = {}
    for t in dico_t_2.keys():
        tampon = {}
        for t2 in dico_t_2.keys():
            if utiles.egal_sple_term(t, t2):
                if len(dico_t_2[t]) > len(dico_t_2[t2]):
                    if (t not in tampon):
                        tampon[t] = dico_t_2[t]
                        if t2 in tampon and t != t2:
                            del(tampon[t2])
                else:
                    if (t2 not in tampon):
                        tampon[t2] = dico_t_2[t2]
                        if t in tampon and t != t2:
                            del(tampon[t])
        if list(tampon.keys())[0] not in dico_final:
            dico_final.update(tampon)
    return dico_final
    
def simple_repere_cand(dico_t, seuil, schema):
    liste_cand = []
    for t, fenetres in dico_t.items():
        compt_s1 = 0 #Meme mot schema et même CAND
        compt_s2 = 0 #Meme mot schema et CAND differents
        compt_s3 = 0 #Mot schema different et même CAND
        compt_s4 = 0 #Mot schema different et CAND different
        for fenetre in fenetres:
            mot_schema = utiles.quel_schema(fenetre,schema)
            cand = utiles.quel_cand(fenetre)
            
            for fenetre1 in fenetres:
                mot_schema1 = utiles.quel_schema(fenetre1,schema)
                cand1 = utiles.quel_cand(fenetre1)
                #print(t,mot_schema,mot_schema1,cand,cand1)
                # TODO supprimer les doublons
                if mot_schema[1] == mot_schema1[1] and cand[2] == cand1[2]:
                    compt_s1 += 1
                elif mot_schema[1] == mot_schema1[1] and cand[2] != cand1[2]:
                    compt_s2 += 1
                elif mot_schema[1] != mot_schema1[1] and cand[2] == cand1[2]:
                    compt_s3 += 1
                elif mot_schema[1] != mot_schema1[1] and cand[2] != cand1[2]:
                    compt_s4 += 1
        if compt_s1 >= seuil[0] or compt_s2 >= seuil[1] or compt_s3 >= seuil[2] or compt_s4 >= seuil[3]:
            liste_cand.append(t)
            print("SIMPLE TROUVE : ", t , ' ', compt_s1,compt_s2,compt_s3,compt_s4)
#        else:
#            print("SIMPLE PAS TROUVE : ", t , ' ', compt_s1,compt_s2,compt_s3,compt_s4)
    return liste_cand

#doit retourner la fenetre tronquée valide contenant un mot (non CAND) lié à un CAND par un mot schéma (après ce CAND) ou none si ne trouve rien. 
def simple_fenetre_valide(fenetre,schema):
    if utiles.schema_present(fenetre, schema):
        for etiquette in fenetre:
            index_cand = 0
            if utiles.est_un_cand(etiquette):
                index_cand = fenetre.index(etiquette)
                break
        fenetre_droite = fenetre[index_cand:]
        if utiles.compte_cand(fenetre_droite) < 2 and utiles.schema_present(fenetre_droite, schema):
            return fenetre_droite

def recherche_simple(dico_etiquettes,candidats,schema):
    fenetres = utiles.defini_fenetres(dico_etiquettes,candidats,3,2)
    fenetres_valides = []
    liste_fenetres_cand = []
    seuil = [3,5,5,10]
    for fenetre in fenetres:
        fenetre_valide = simple_fenetre_valide(fenetre,schema)
        if fenetre_valide:
            fenetres_valides.append(fenetre_valide)
        else:
            fenetreR = utiles.symetrique_fenetre(fenetre)
            fenetre_valideR = simple_fenetre_valide(fenetreR,schema)
            if fenetre_valideR:
                fenetres_valides.append(fenetre_valideR)
            
    dico_t = dico_mots_trouves(fenetres_valides)
    liste_cand = simple_repere_cand(dico_t,seuil,schema)
