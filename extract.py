#!/usr/bin/env python3
# encoding: utf-8
import useful
import objects

# en meta: il faut 1 dict pour les occurrences + 1 set pour les candidats
# ce sont nos 2 types d'objets typiques.

##########################
####### nucleus ##########
##########################
def nucleus_step(OCC, CAND, nucleus_threshold):
    #nucleus_threshold should be tuple formated like "vector" (see above)
    twords_dict = {}
    for cand in CAND:
        window = CAND[cand].nuc_window(OCC)# key:t_word_pos; value: (link_word_type, cand_id)
        twords_dict.update(window)
    twordsmerged = useful.merge_egal_sple_dict(OCC,twords_dict)
    #twordsmerged {key: tuple of (twords_position); value: list of tuples(link_word_type, cand_id)}
    for case in twordsmerged:
        if len(twordsmerged[case]) > min(nucleus_threshold):
            vector = useful.count_nuc_cases(twordsmerged[case])
                #vector is tuple like this
                # s1: same linkword same CAND
                # s2: same linkword, different CAND
                # s3: different linkword, same CAND
                # s4: different linkword, different CAND
            if any([True for x in range(4) if vector[x] >= nucleus_threshold[x]]):
                next_id = max(CAND) + 1
                positions = set([tuple([position]) for position in case]) #we want a set of tuple of position presented like this set([(1,), (3,), (6,)])
                CAND[next_id] = objects.Nucleus(idi = next_id, where = positions)#new CAND is created
                CAND[next_id].buildnuc(OCC, CAND)

##########################
###### expression ########
########## and ###########
###### expansion #########
##########################

def exp_step(OCC, CAND, expression_threshold, expansion_threshold):
    CAND2build = {}# storing the CAND to be created while looping in the dict
    for cand_id in CAND:
        expawin = CAND[cand_id].expa_window(OCC)# {t_word_pos: tuple_cand_positions)
        expre_where, expre_what = CAND[cand_id].expre_window(OCC)
        # expre_where{tuple(cand_id, nextcand_id): set of tuples(cand_positions)}
        # expre_what{tuple(cand_positions): tuple(occ_pos of the ptential expre)}
        ########conflict management #first: check for forbidden positions, because valid expa
        expawinmerged = useful.merge_egal_sple_dict(OCC, expawin)# {tuple(t_word_pos):list of (tuple_cand_positions)}
        forbid = set()
        if expawinmerged:
            for expa_twords_eq in expawinmerged:
                if len(expa_twords_eq) > expansion_threshold:
                    forbid.union(set(expawinmerged[expa_twords_eq]))# forbid = set(tuple_cand_positions)
                    #Build the cand expa (inside or not) by the way...
                    where = set()#where is set of tuple of expa_positions
                    for valid_tword in expa_twords_eq:# for t_word in the tuple of equivalent t_words
                        where.add(tuple(range(min(expawin[valid_tword]),valid_tword+1)))# tuple = expa position = all lintegers between min of the cand positions and tword position (+1 for range method behaviour)
                    next_id = max(CAND) + 1 + len(CAND2build)
                    CAND2build[next_id] = (next_id, where)# new CAND to be created (stored while looping in the dict)
        #second: remove the allready  position from the expre_windows and build exprewindow dict (clean one)
        exprewin = {}
        if expre_where:
            for couple in expre_where:
                if len(expre_where[couple]) > expression_threshold:# set of tuples(cand_positions). the other, not long enough are rejected
                    for cand_positions in expre_where[couple]:#for each tuple of cand_positions
                        if cand_positions not in forbid:
                            exprewin.setdefault(couple, set()).add(expre_what[cand_positions])#retrieve the whole expre pos from the single first cand_pos
            #third : building the new expre, starting with the less occurring ones. Managing conflicts for cases like A de B de C
            for couple in sorted(exprewin, key=lambda couple: len(exprewin[couple])):#the less occuring expre first
             #FIXME ordre de traitement des expre et gérer les conflicts:
             # d'abord ceux qui ont le moins d'occurrence, dans la limite de ne pas empecher la formation de ceux qui en ont le plus!
                if len(exprewin[couple]) > expression_threshold:
                    next_id = max(CAND) + 1 + len(CAND2build)
                    CAND2build[next_id] = (next_id, exprewin[couple])# new CAND to be created (stored while looping in the dict)
    for idi, value in CAND2build.items():#building all the new cands
        CAND[idi] = objects.Candidat(idi = value[0], where = value[1])
        CAND[idi].build(OCC, CAND)

##########################
####### recession#########
##########################

def recession_step(OCC, CAND, recession_threshold):
    todel = set()
    for idi in CAND:
        if CAND[idi].recession(recession_threshold, OCC, CAND):#None == false
            todel.add(idi)
    for idi in todel:
        del CAND[idi]
