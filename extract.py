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
        window = cand.nuc_window(OCC)# key:t_word_pos; value: (cand_id, link_word_type)
        twords_dict.update(window)

    twordsmerged = useful.merge_egal_sple_dict(twords_dict)
    #{twordsmerged[tuple of (twords_position)]: list of tuples(cand_id, link_word_type)}
    for case in twordsmerged:
        vector = useful.count_nuc_cases(twordsmerged[case])
            #vector is tuple like this
            # s1: same linkword same CAND
            # s2: same linkword, different CAND
            # s3: different linkword, same CAND
            # s4: different linkword, different CAND
        if any[True for x in range(3) if vector[x] >= nucleus_threshold[x]]:
            next_id = max(CAND) + 1
            CAND[next_id] = Nucleus(idi = next_id, where = twordsmerged[case], name = False)#new CAND is created
            CAND[next_id].buildnuc(OCC)
    del twordsmerged#we don't need it anymore

##########################
###### expression ########
########## and ###########
###### expansion #########
##########################
#
def exp_step(OCC, CAND, expression_threshold, expansion_threshold):
    for cand_id in CAND:
        expawin = CAND[cand_id].expa_window(OCC)# {t_word_pos: tuple_cand_positions)
        exprewhere, exprewhat = CAND[cand_id].expre_window(OCC)
        # expre_where{tuple(cand_id, nextcand_id): set of tuples(cand_positions)}
        # expre_what{tuple(cand_positions): tuple(occ_pos of the ptential expre)}

        #conflict management
        #first: check for forbidden positions, because valid expa
        expawinmerged  = useful.merge_egal_sple_dict(expawin)# {tuple(t_word_pos):tuple of (tuple_cand_positions)}
        forbid = set()
        for expa_twords_eq in expawinmerged:
            if len(expa_twords_eq) > expansion_threshold:
                forbid.add(set(expawinmerged[expa_twords_eq]))# forbid = set(tuple_cand_positions)
                #Build the cand by the way...
                where = set()
                for valid_tword in expa_twords_eq:# for t_word in the tuple of equivalent t_words
                    where.add(tuple(range(min(expawin[valid_tword]),valid_tword)))# tuple: all lintegers between  min of the cand positions and tword position
                next_id = max(CAND) + 1
                CAND[next_id] = Candidat(idi = next_id, where = where, name = False)#new CAND is created
                CAND[next_id].build(OCC)
        #second: remove the forbidden position from the expre_windows
        for couple in expre_where:
            if len(expre_where[couple]) > expression_threshold:# set of tuples(cand_positions). the other, not long enough are rejected
                for cand_positions in expre_where[couple]:#for each tuple of cand_positions
                    if cand_positions in not in forbid:
                        exprewin.setdefault(couple, set()).add(expre_what[cand_positions])#retrieve the whole expre pos from the single first cand_pos

        for couple in sorted(exprewin, key=lambda couple: len(exprewin[couple])):#the less occuring expre first
            if len(exprewin[couple]) > expression_threshold:
                next_id = max(CAND) + 1
                CAND[next_id] = Candidat(idi = next_id, where = exprewin[couple], name = False)#new CAND is created
                CAND[next_id].build(OCC)



#     #TODO ordre de traitement des expre et gérer les conflicts
#     #dans le cas A de chose B de truc C
#     # on a les couple AB et BC...
#     # d'abord ceux qui ont le  moins d'occurrences ou bien le contraire ??
#      pourquoi pas d'abord ceux qui ont le moins d'occurrence, dans la limite de ne pas empecher la formation de ceux qui en ont le plus!
