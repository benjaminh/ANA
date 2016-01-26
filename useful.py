#!/usr/bin/env python3
# encoding: utf-8
import os
import logging
import re
import objects
import json

def setupfolder(working_directory):
    if not os.path.exists('output/'):
        os.makedirs('output/')#keywords, what_in_page, where_keyword...
    if not os.path.exists('log/'):
        os.makedirs('log/')#log, stuff
    elif os.path.isfile('log/ana.log'):
        os.remove('log/ana.log')
    if not os.path.exists('intra/'):
        os.makedirs('intra/')#mapping, pages_pos,

def merge_dicts(dict_list):
    result = {}
    for dictionary in dict_list:
        result.update(dictionary)
    return result

def merge_egal_sple_dict(OCC, *dict_args):
    '''
    input dict {key: occurrence_position, value: whatever}
    output dict {key: tuple of equal_keys, values: list of equal values}
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
        for feature, i in enumerate(value_eq):#feature is tuple(cand_id, link_word_type)
            cand_id, link_word_type = feature
            seen.add(i)
            for feature2, i2 in enumerate(value_eq):
                if i2 not in seen:
                    cand_id2, link_word_type2 = feature2
                    if cand_id2 != cand_id and link_word_type2 == link_word_type:
                        s2 += 1
                    elif cand_id2 == cand_id and link_word_type2 == link_word_type:
                        s1 += 1
                    elif cand_id2 == cand_id and link_word_type2 != link_word_type:
                        s3 += 1
                    elif cand_id2 != cand_id and link_word_type2 != link_word_type:
                        s4 += 1
    return (s1, s2, s3, s4)


# def soft_equality_set(occ_pos_set, OCC, threshold):
#     #should be a set of occ_pos
#     #returns a set of tuple containing equals pos if there is more than "threshold" equalities
#     seen= set()
#     equals = set()
#     for pos in occ_pos_set:
#         seen.add(pos)
#         eq = (pos,)
#         for pos2 in occ_pos_set:
#             if OCC[pos].soft_equality(pos2) and pos2 not in seen:
#                 eq += (pos2,)
#         if len(eq) >= threshold:
#             equals.add(eq)

def build_bootdict(bootstrap_file_path):
    with open(bootstrap_file_path, 'r', encoding='utf8') as bootstrapfile:
        text = bootstrapfile.read()
        cands = re.split('\W+', text)
        bootstrap = {}
        for i, cand in enumerate(cands):
            if cand:
                bootstrap[i] = objects.Occurrence(long_shape = cand, cand = 0, cand_pos = set(), date = False, linkword = 0, tword = True)
        return bootstrap

def build_stopset(stopword_file_path):
    with open(stopword_file_path, 'r', encoding='utf8') as stopwordfile:
        lines = stopwordfile.readlines()
        return set([re.sub(r'\n', '', s) for s in lines])

def build_linkdict(linkwords_file_path):# basicaly in french {de:1, du:1, des:1, d:1, au:2, aux:2, en:3}
    with open(linkwords_file_path, 'r', encoding = 'utf8') as linkwordsfile:
        lines = linkwordsfile.readlines()
        linkwords = {}
        for i, line in enumerate(lines):
            line = re.sub('\s+$', '', line)
            line = re.split('\W+', line)
            for linkword in line:
                linkwords[linkword] = i
        return linkwords

# #ecrire log
# def write_log(working_directory, indication):
#     log_file_path = os.path.join(working_directory, 'log', 'ana.log')
#     with open(log_file_path, 'a', encoding = 'utf8') as logfile:
#         logfile.write(indication + '\n')

#jsonpagespos_path is to store the position of the markers spliting the original pages in the concatenated txt4ana.txt
def build_OCC(txt4ana, stopwords_file_path, linkwords_file_path, bootstrap_file_path, working_directory):
    bootstrap = build_bootdict(bootstrap_file_path)
    occ2boot = {}
    propernouns = {}
    stopwords = build_stopset(stopwords_file_path)
    linkwords = build_linkdict(linkwords_file_path)
    Rsplitermark = re.compile(r'wxcv[\d|_]*wxcv')#TODO build a splitermark regex
    Rwordsinline = re.compile(r'(\w+[’|\']?|[.,!?;])(?siu)')
    Rdate = re.compile(r'(1\d\d\d|20\d\d)')
    Rnumeral = re.compile(r'(\b\d+\b)')
    Rponctuation = re.compile(r'[,!?;]')
    dotahead = False
    index = 0
    page_id = None#initial state to catch the first marker (see below)
    pages_pos = {}# dict {key:id of the page, value: tuple(begin_occ_pos, end_occ_pos)
    OCC = {}
    CAND = {}
    with open(txt4ana, 'r', encoding = 'utf8') as txtfile:
        for line in txtfile:
            words = Rwordsinline.findall(line)
            for word in words:
                index += 1
                if Rsplitermark.match(word):
                    #TODO page_id = get the id of the splitmarker, or build it
                    if page_id:#the first markers of the page will have no "last used page_id"
                        pages_pos[page_id] += (index,)#last used page_id is still valid and close the last
                    page_id = re.findall(r'([\_|\d]+)', word)[0]#get the new page id
                    pages_pos[page_id] = (index+1,)#begining of the next page
                elif word in linkwords:
                    OCC[index] = objects.Occurrence(long_shape = word, linkword = linkwords[word])
                    dotahead = False
                elif re.match(r'\.', word):
                    OCC[index] = objects.Occurrence(long_shape = word)
                    dotahead = True
                elif Rdate.match(word):#IDEA is it interesting to have dates as tword?
                    OCC[index] = objects.Occurrence(long_shape = word, date = True, tword = True)
                    dotahead = False
                elif word.lower() in stopwords or Rnumeral.match(word) or Rponctuation.match(word):
                    OCC[index] = objects.Occurrence(long_shape = word)
                    dotahead = False
                else:
                    OCC[index] = objects.Occurrence(long_shape = word, tword = True)
                    for indice in bootstrap:#bootstrap is a dict Occurrences objects
                        if OCC[index].soft_equality(bootstrap[indice]):
                            occ2boot.setdefault(indice, set()).add(tuple([index]))
                            continue
                    if dotahead == False and word[0].isupper() and words.index(word) != 0:#no dot before and uppercase and not begining of a newline -> it is a propernoun
                        propernouns.setdefault(word, set()).add(tuple([index]))
        pages_pos[page_id] += (index,)#closing the last page
        for indice in occ2boot:# building the cand from the all the occ matching with bootstrap words
            try:
                next_id = max(CAND)+1
            except ValueError:#this means it is the first cand, there is no value for max
                next_id = 0
            CAND[next_id] = objects.Candidat(idi = next_id, where = occ2boot[indice])
            CAND[next_id].build(OCC, CAND)
        for propernoun in propernouns:
            next_id = max(CAND)+1
            CAND[next_id] = objects.Candidat(idi = next_id, where = propernouns[propernoun], protected = True)
            CAND[next_id].build(OCC, CAND)
        #writing a file mapping the concatenated file with their start_po end_pos in the OCC dict
        jsonpagespos_path = os.path.join(working_directory, 'intra', 'pages_pos.json')
        with open(jsonpagespos_path, 'w') as jsonpages:#TODO ok pour un JSON file? il fera le lien entre le mots clef et les noeuds neo4j?
            json.dump(pages_pos, jsonpages, ensure_ascii=False, indent=4)
    return OCC, CAND
                #TODO build the cands protected
                #FIXME how to build Atelier et Chantier if Atelier and Chantier are allready cands -> no linkword, nothing helps to build it!
                #TODO build neo4j nods corresponding to the pages. (should have been done before, in preANA step)


#TODO function to build a long shape for the cand at the end
#maybe some option for this shape building?
#maybe the user can choose one among others
