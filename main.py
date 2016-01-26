#!/usr/bin/env python3
# encoding: utf-8
import useful
import logging
import time
import os

working_directory = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/testANA2'#directory where the txt4ana is
txt4ana = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/testANA2/txt4ana2.txt'
bootstrap_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/test4Haruspex/testANA2/bootstrap'
linkwords_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/ANA/french/schema'
stopwords_file_path = '/home/matthieu/MEGAsync/IRCCyN/projets/ANA/french/stoplist_Fr.txt'

os.chdir(working_directory)
useful.setupfolder(working_directory)
logfilepath = os.path.join(working_directory, 'log', 'ana.log')
logging.basicConfig(filename='log/ana.log', format='%(levelname)s:%(message)s', level=logging.INFO)
starting = str(time.clock())
logging.info('Started at' + starting)


OCC = useful.build_OCC(txt4ana, stopwords_file_path, linkwords_file_path, bootstrap_file_path, working_directory)
