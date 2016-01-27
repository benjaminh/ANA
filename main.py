#!/usr/bin/env python3
# encoding: utf-8
import useful
import extract
import logging
import time
import os


working_directory = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/test2_4ana2'#directory where the txt4ana is
txt4ana = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/test2_4ana2/text4ana.txt'
bootstrap_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/test2_4ana2/bootstrap'

linkwords_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/ANA/french/schema'
stopwords_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/ANA/french/stoplist_Fr.txt'
nucleus_threshold = (2,2,3,3)
            #vector is tuple like this
            # s1: same linkword same CAND
            # s2: same linkword, different CAND
            # s3: different linkword, same CAND
            # s4: different linkword, different CAND
expansion_threshold = 2
expression_threshold = 2
recession_threshold = min(expansion_threshold, expression_threshold, min(nucleus_threshold))

os.chdir(working_directory)
useful.setupfolder(working_directory)
logfilepath = os.path.join(working_directory, 'log', 'ana.log')
logging.basicConfig(filename='log/ana.log', format='%(levelname)s:%(message)s', level=logging.INFO)
starting = str(time.clock())
logging.info('Started at' + starting)

logging.info('### building the OCC dict ###')
OCC, CAND = useful.build_OCC(txt4ana, stopwords_file_path, linkwords_file_path, bootstrap_file_path, working_directory)

for i in range(5):
    logging.info('### EXPANSION & EXPRESSION ### step '+ str(i))
    extract.exp_step(OCC, CAND, expression_threshold, expansion_threshold)
    logging.info('### NUCLEUS ### step '+ str(i))
    extract.nucleus_step(OCC, CAND, nucleus_threshold)
    logging.info('### RECESSION ### step '+ str(i))
    extract.recession_step(OCC, CAND, recession_threshold)

ending = str(time.clock())
logging.info('Ended at' + ending)

# print(OCC[13945].long_shape)
