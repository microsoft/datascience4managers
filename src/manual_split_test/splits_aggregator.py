#!/usr/bin/python
# Oct 2019  JMA
# splits_aggregator.py  write scale events to mongoDB
'''
Write a short description of what the program does here. 

Usage:
$ ./splits_aggregator.py [-v] [-d data_dir] [-g pattern]
    -v verbose output
    -d data directory to read from
    -g glob pattern for data files
''' 
import os, os.path, sys
import glob
import math
import pprint
import subprocess
import sys
import re
import string
import time
import numpy as np
import pandas as pd
import bokeh as bk
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
from bokeh.plotting import figure
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
DATA_DIR  = os.path.join(os.getcwd() ,'../../shared/') 
GLOB_PATTERN = 'language_selection_tests'

########################################################################
class CreateNewsGroupsData(object):
    'Prune the newsgroups text to create a labelled table'

    def __init__(self, 
                data_path= 'D:/OneDrive - Microsoft/data/20news/20news-bydate-train/rec.motorcycles/', # Must end in /
                data_range=(104986, 105065)):
        self.train_df = []
        label = re.search(r'([^/]+)/$', data_path).group(1)
        for sample_file in range(data_range[0], data_range[1]):
            file_path = os.path.abspath(os.path.join(data_path, str(sample_file)))
            if os.path.exists(file_path):
                the_contents = open(file_path, 'r' ).readlines()
                pruned_contents = self.prune_contents(the_contents)
                if VERBOSE:
                    print('For msg: ', sample_file, ' Found', pruned_contents)
                if pruned_contents[0] > 1:
                    self.train_df.append((label, str(sample_file), pruned_contents[1]))
            else:
                if VERBOSE: 
                    print('No file found: ', file_path)

    def prune_contents(self, msg_txt):
        'Iterate by lines, to remove the header and find the first multi line paragraph.'
        pruned_content = [] # A list of strings. 
        in_header = True
        in_quotes = True
        para_ln_cnt = 0
        for ln in msg_txt:
            #ln = ln.trim()
            if not in_header and not in_quotes:
                if not ln.strip():  # Blank line => End of section
                    break
                else:             # We want this content
                    para_ln_cnt +=1
                    pruned_content.append(ln)
            elif not in_header and in_quotes:
                if self.quoted_line(ln):  # consume until content
                    continue
                else:
                    in_quotes = False
                    para_ln_cnt =1
                    pruned_content.append(ln)                    
            else: # in header
                if not ln.strip():  # blank line always ends the header
                    in_header = False
                    continue
        return (para_ln_cnt, pruned_content)

    def quoted_line(self, ln):
        if re.match(r'^\W', ln):     # None alphanumeric first char, e.g. > 
            return True
        elif re.search(r'^In|writes\W$|wrote\W$', ln):
            return True
        elif not ln.strip():
            return True
        else:
            return False

########################################################################
class CollectSplits(object):
    'Collect csv files of daily customer logs and aggregate into one dataframe.' 
    
    def __init__(self, glob_pattern, cvs_dir):
        self.tst_lbls = []
        self.as_df = None
        for data_file in glob.glob(os.path.abspath(os.path.join(cvs_dir, glob_pattern))):
            try:
                self.add_file(data_file)
            except Exception as err:
                print(f"{err}\nSkipping file: {data_file} Cannot load it.", file=sys.stderr)


    def add_file(self, the_fname):
        self.as_df = pd.read_csv(the_fname, header=None )
        self.tst_lbls.append((self.as_df.iloc[5,3], self.as_df.iloc[5,4]))
        print("Data dim: ", self.as_df.shape)

########################################################################
class SplitClassifier (object):
    'Module names and class names can be the same.'

    def __init__(self, db="metric_db"):
        pass
        # self.metric_json = self.convert2json(db)

###############################################################################
def main(input_dir, glob_pattern):

    # Test content extraction
    msg_ds = CreateNewsGroupsData() 
    pprint.pprint(msg_ds.train_df)

    # Test split pattern extraction
    input_pattern= glob_pattern + '*.csv'
    cs = CollectSplits(input_pattern, DATA_DIR)
    print("tsts: ", cs.tst_lbls)
    return 0

########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        DATA_DIR = os.path.abspath(sys.argv[d+1]) # Assuming the path is relative to the user's home path 
    else:
        DATA_DIR = os.path.abspath(DATA_DIR)
    
    if '-g' in sys.argv:
        g = sys.argv.index('-g')
        GLOB_PATTERN = sys.argv[g+1]  


    main(DATA_DIR, GLOB_PATTERN)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF
