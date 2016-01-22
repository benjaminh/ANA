def merge_dicts(dict_list):
    result = {}
    for dictionary in dict_list:
        result.update(dictionary)
    return result

def merge_egal_sple_dict(*dict_args, OCC):
    '''
    the dicts should be "key: occurrence_position, value: whatever"
    return a dict key: shortest shape in soft_equality; value dict{"equal_key":set of (occurrence_position), "equal_values": tuple of (whatever)}
    the new key gathering all the merged keys (found in sple_egal) will be the most occurring one.
    Given any number of dicts, shallow copy and merge into a new dict,
    based on egal_sple fonction.
    '''
    if len(dict_args) > 1:
        merged = merge_dicts(dict_args)
    else:
        merged = dict_args[0]

    if len(merged) == 1: # faster if there is only one pair of (key, value) in the dict!
        return merged
    else:
        for key1 in merged:
            equal[key1] = set([key1])
            # equal_keys = (key1,)
            # equal_values = (merged[key1],)#tuple init, not set because maybe duplicates
            for key2 in merged:
                if key2 not in equal and OCC[key1].soft_equality(OCC[key2]):
                    equal[key1].add(key2)#equal[occ_pos] = set of occ_pos
        # now: FOAF style "les amis de mes amis sont mes amis..."
        # 1 degree only! should be enough
        z = {}
        seen = {}
        for key in equal:#equal[occ_pos] = set of occ_pos
            if key not in seen:
                seen.add(equal[key])
                z[key].add(equal[key])#copy of the equal[key] entry
                for key_eq in equal[key]:
                    z[key].add(equal[key_eq])# add all the foaf without duplication (in a set)
                    seen.add(equal[key_eq])# only one degree so we can don't want to rebuild the whole dict of relations.
        # now lets build the dict[equal_keys] = equal_values
        for key, key_eqs in z.items():
            for key_eq in key_eqs:
                final.setdefault(tuple(key_eqs), []).append(merged[key_eq])# retrieves the value of the original dict to merge in soft eq
        return final


def count_nuc_cases(merged):
#{merged[tuple of (occurrence_position)]: list of tuples(cand_id, link_word_type)}
# Four Cases!
    s1 = 0# s1: same linkword same CAND
    s2 = 0# s2: same linkword, different CAND
    s3 = 0# s3: different linkword, same CAND
    s4 = 0# s4: different linkword, different CAND
    for key_eq, value_eq in merged.items():#value_eq
        for feature in value_eq:#feature is tuple(cand_id, link_word_type)
            cand_id, link_word_type = feature
        #not able to count the seen ones because many times the same "feature" apears
        #TODO maybe a better solution than this one
            for feature2 in value_eq:
                cand_id2, link_word_type2 = feature2
                if cand_id2 == cand_id and link_word_type2 == link_word_type:
                    s1 += 1
                if cand_id2 != cand_id and link_word_type2 == link_word_type:
                    s2 += 1
                if cand_id2 == cand_id and link_word_type2 != link_word_type:
                    s3 += 1
                if cand_id2 != cand_id and link_word_type2 != link_word_type:
                    s4 += 1
    s1 = math.sqrt(s1)
    s2 = math.sqrt(s2)
    s3 = math.sqrt(s3)
    s4 = math.sqrt(s4)
    return (s1, s2, s3, s4)


def soft_equality_set(occ_pos_set, OCC, threshold):
    #should be a set of occ_pos
    #returns a set of tuple containing equals pos if there is more than "threshold" equalities
    seen= set()
    equals = set()
    for pos in occ_pos_set:
        seen.add(pos)
        eq = (pos,)
        for pos2 in occ_pos_set:
            if OCC[pos].soft_equality(pos2) and pos2 not in seen:
                eq += (pos2,)
        if len(eq) >= threshold:
            equals.add(eq)

def expre_shape(couple, CAND):
    #build the expre long_shape as CAND1 de CAND2
    return CAND[couple[0]].long_shape +  'de' + CAND[couple[1]].long_shape
