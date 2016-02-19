#!/usr/bin/env python3
# encoding: utf-8
import useful
import extract
import logging
import time
import os
import json

working_directory = '/home/matthieu/ownCloud/projets/1_corpora/test2_4ana2'#directory where the txt4ana is



# config = json.loads(open(os.path.join(sys.argv[1],'ana_config.json')).read())
config = json.loads(open(os.path.join(working_directory,'ana_config.json')).read())

#GLOBAL LANG CONFIG
whereami = os.path.dirname(os.path.abspath(__file__))
stopwords_file_path = whereami + '/french/stopwords_fr.txt'#config['stopwords_file_path']
linkwords_file_path = whereami + '/french/schema'#config['linkwords_file_path']
emptywords_file_path = whereami + '/french/emptywords_fr.txt'#config['emptywords_file_path']


#####################
####LOCAL CONFIG#####
#####################
os.chdir(working_directory)
useful.setupfolder(working_directory)# mkir  the useful sub-forlders

# TEXT
txt4ana = config['txt4ana']
bootstrap_file_path = config['bootstrap']
extra_stopwords_file_path = config['extra_stopwords']
extra_emptywords_file_path = config['extra_emptywords']
match_propernouns = config['propernouns']

#SEUILS
nucleus_threshold = config['nucleus_threshold']
    #nuc threshold is tuple like this
    # s1: same linkword same CAND
    # s2: same linkword, different CAND
    # s3: different linkword, same CAND
    # s4: different linkword, different CAND
expansion_threshold = int(config['expansion_threshold'])
expression_threshold = int(config['expression_threshold'])
recession_threshold = int(config['recession_threshold'])

#STEPS
global_steps = int(config['global_steps'])
nucleus_steps = int(config['nucleus_nestedsteps'])
automaticsteps = config['automaticsteps'] # True ou False

#LOG INITIALIZE
logfilepath = os.path.join(working_directory, 'log', 'ana.log')
logging.basicConfig(filename=logfilepath, format='%(levelname)s:%(message)s', level=logging.INFO)
starting = str(time.clock())
logging.info('Started at' + starting)

logging.info('### building the OCC dict ###')
OCC, CAND = useful.build_OCC(txt4ana, stopwords_file_path, extra_stopwords_file_path, emptywords_file_path, extra_emptywords_file_path, linkwords_file_path, bootstrap_file_path, match_propernouns, working_directory)


#PROCESS CALL
stop = False
nb_passe = 0
while not stop:
    nb_passe += 1
    global_steps -= 1
    old_len_cands = len(CAND)
    for j in range(nucleus_steps):
        logging.info('\n### NUCLEUS ### step '+ str(nb_passe)+'.'+ str(j))
        extract.nucleus_step(OCC, CAND, nucleus_threshold)
    logging.info('\n### EXPANSION & EXPRESSION ### step '+ str(nb_passe))
    extract.exp_step(OCC, CAND, expression_threshold, expansion_threshold)
    logging.info('\n### RECESSION ### step '+ str(nb_passe) + '\n\n')
    extract.recession_step(OCC, CAND, recession_threshold)
    diff = len(CAND)-old_len_cands
    print('Variation du nombre de candidats :', diff)
    #stop conditions:
    if automaticsteps and diff == 0:
        automaticsteps = False #out ouf this loop next time, for 2 more rounds
        if time.clock() < 100:#if it is a short process (less than 100 sec)
            global_steps = 2#run 2 more times after having stoped discoverring cands. (-> building long xpre and xpa?)
        elif time.clock() < 1000:
            global_step = 1# run one more time after having stoped discoverring cands.
        else:
            stop = True
    elif not automaticsteps and global_steps == 0:
        stop = True

#WRITE OUTPUT
ending = str(time.clock())
logging.info('Ended at' + ending)
with open('output/keywords.csv', 'w') as keyfile:
    for idi in CAND:
        shape = ''
        for occ_pos in CAND[idi].where:
            for e in occ_pos:
                shape += OCC[e].long_shape
                shape += ' '
            break
        if shape == '':
            print(idi)
        keyfile.write(str(len(CAND[idi].where))+','+ shape+'\n')
