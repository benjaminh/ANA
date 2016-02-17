#!/usr/bin/env python3
# encoding: utf-8
import useful
import extract
import logging
import time
import os


working_directory = '/home/matthieu/ownCloud/projets/1_corpora/XML-HDTCOL'#directory where the txt4ana is
txt4ana = working_directory + '/text4ana.txt'
bootstrap_file_path = working_directory + '/bootstrap'
extra_stopwords_file_path = working_directory + '/extra_stopwords.txt'
extra_emptywords_file_path = working_directory + '/extra_emptywords.txt'

whereami = os.path.dirname(os.path.abspath(__file__))
stopwords_file_path = whereami + '/french/stopwords_fr.txt'
linkwords_file_path = whereami + '/french/schema'
emptywords_file_path = whereami + '/french/emptywords_fr.txt'

nucleus_threshold = (3,3,3,4)
            #vector is tuple like this
            # s1: same linkword same CAND
            # s2: same linkword, different CAND
            # s3: different linkword, same CAND
            # s4: different linkword, different CAND
expansion_threshold = 4
expression_threshold = 4
recession_threshold = min(expansion_threshold, expression_threshold)

os.chdir(working_directory)
useful.setupfolder(working_directory)# mkir  the useful sub-forlders
logfilepath = os.path.join(working_directory, 'log', 'ana.log')
logging.basicConfig(filename='log/ana.log', format='%(levelname)s:%(message)s', level=logging.INFO)
starting = str(time.clock())
logging.info('Started at' + starting)

logging.info('### building the OCC dict ###')
OCC, CAND = useful.build_OCC(txt4ana, stopwords_file_path, extra_stopwords_file_path, emptywords_file_path, extra_emptywords_file_path, linkwords_file_path, bootstrap_file_path, working_directory)

for i in range(6):
    for j in range(3):
        logging.info('### NUCLEUS ### step '+ str(i)+'.'+ str(j))
        extract.nucleus_step(OCC, CAND, nucleus_threshold)
    logging.info('### EXPANSION & EXPRESSION ### step '+ str(i))
    extract.exp_step(OCC, CAND, expression_threshold, expansion_threshold)
    logging.info('### RECESSION ### step '+ str(i))
    extract.recession_step(OCC, CAND, recession_threshold)

ending = str(time.clock())
logging.info('Ended at' + ending)

for idi in CAND:
    shape = ''
    for occ_pos in CAND[idi].where:
        for e in occ_pos:
            shape += OCC[e].long_shape
            shape += ' '
        break
    if shape == '':
        print(idi)
    print(len(CAND[idi].where),',', shape)

# print('#########')
#
# for i in [8370, 8371, 8372, 8373, 8374, 8375, 8376, 8377, 8378, 8379]:
#     print(OCC[i].long_shape)
# # print(OCC[13945].long_shape)
#
# print('#########')
# for i in [8360, 8361, 8362, 8363, 8364, 8365, 8366, 8367, 8368, 8369, 8370, 8371, 8372, 8373, 8374, 8375, 8376, 8377, 8378, 8379]:
#     print(OCC[i].long_shape)
