#!/usr/bin/env python3
# encoding: utf-8
import re
import os
import errno

#enlève les sauts de ligne entre acolades ouvertes et fermée
def AcoladeClose(origin_file_path):
    with open(origin_file_path, 'r', encoding = 'utf8') as origin_file:
        textstep0 = origin_file.readlines()
        file_step1 = origin_file_path + 'BeinClean.step1'
        with open(file_step1, 'w', encoding = 'utf8') as filestep1:
            line_num = 0
            for ligneO in textstep0:
                if "\end{document}" not in textstep0[line_num]:
                    line_num += 1
                    ligneO = textstep0[line_num]
                    if "{" in ligneO:
                        compteur = len(re.findall("{", ligneO))
                        compteurF = len(re.findall("}", ligneO))
                        while compteur > compteurF:
                            textstep0[line_num] = re.sub("\n", " ", textstep0[line_num]) #texte[line_num] = ligne (la première fois)
                            #print (texte[i])
                            filestep1.write(textstep0[line_num]) # écrit cette ligne sans le \n
                            compteur += len(re.findall("{", textstep0[line_num+1])) #incrémente le compteur avec ce qu'il trouve dans la ligne suivante
                            compteurF += len(re.findall("}", textstep0[line_num+1]))
                            line_num += 1 # passe à la ligne suivante
                    filestep1.write(textstep0[line_num])
            filestep1.close()
            origin_file.close()


def wo_markup(origin_file_path):
    file_step1 = origin_file_path + 'BeinClean.step1'
    with open(file_step1, "r", encoding = 'utf8') as filestep1:
        textstep1 = filestep1.readlines()
        file_step2 = origin_file_path + '.cleaned'
        with open(file_step2, "w", encoding = 'utf8') as filestep2:
            i = 0
            for line in textstep1:
                i+=1
                nb_brace = len(re.findall(r'{', line))
                if nb_brace == 0:
                    clean_line = line
                else:
                    regex = r'\\[^s|p| ][^\}]*}' + (nb_brace-1)*r'.[^\}]*}'
                    pattern = re.compile(regex)
                    clean_line = re.sub(pattern, '', line)
                if '\\' in clean_line:
                    clean_line = re.sub('\\\clearpage', ' ', clean_line)
                    clean_line = re.sub(r'\\footnotemark{}', ' ', clean_line)
                    clean_line = re.sub(r'\\bigskip', ' ', clean_line)
                    clean_line = re.sub('\\\centering', ' ', clean_line)
                    clean_line = re.sub('\\\ ', '', clean_line)
                if '\\bibliographystyle' in line:
                    break
                filestep2.write(clean_line)
            filestep1.close()
            filestep2.close()



def silentremove(origin_file_path):
    file2remove = origin_file_path + 'BeinClean.step1'
    try:
        os.remove(file2remove)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


###############################################
###############################################
origin_file_path = 'test/txt.txt'
AcoladeClose(origin_file_path) # remove '\n' to close the opened braces in a single line
wo_markup(origin_file_path) # remove the markup strings in the text
silentremove(origin_file_path) # remove the filestep1 (that is a temporary file)
