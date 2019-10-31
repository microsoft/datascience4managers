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
import pq
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
DATA_DIR  = os.path.join(os.getcwd() ,'../../shared/') 
PARQUET_DIR = 'D:\\OneDrive - Microsoft\\data\\20news\\20news-bydate-train\\train_clean'
GLOB_PATTERN = 'language_selection_tests'


########################################################################
class CollectSplits(object):
    'Collect csv files from participants and aggregate.' 
    
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
class BinaryComparisons(object):
    'Randomly pair training cases to find words specific to each class.'
    def __init__(self,data_paths):
        self.full_df = pq.consolidate_parquet(data_paths)       # 'merge all training data'
        self.full_df.reset_index()
        

    def random_pairs(self, no_pairs):
        'Sample without replacement for pairwise item comparisons'
        pair_df = np.empty(shape=(0,6))
        for n0 in range(no_pairs):
            reps =0
            while reps < 100:
                pair = self.full_df.sample(2, replace=False)
                labels = pair['label'].values
                if labels[0] !=labels[1]:
                    break
            reps +=1
            print (reps, pair)
            # pair_df = pd.concat([pair_df, pd.concat([pair.iloc[0,], pair.iloc[1,]], axis=1)], axis=0)
            row = np.hstack([pair.iloc[0,].values, pair.iloc[1,].values]) 
            pair_df = np.vstack([pair_df, row])
        pair_df = pd.DataFrame(pair_df)
        pair_df.columns = ['label1', 'item1', 'msg1', 'label2', 'item2', 'msg2']
        return pair_df

    def embed_in_excel(self):
        'Export ss files that users '
########################################################################
class SplitClassifier (object):
    'Assemble the splits are run them with highest precision lowest coverage first.'

    def __init__(self, path):
        pass

###############################################################################
def main(input_dir, glob_pattern):

    # Test split pattern extraction
    # input_pattern= glob_pattern + '*.csv'
    cs = BinaryComparisons(PARQUET_DIR)
    print("train: ", cs.full_df.shape)
    pair_df = cs.random_pairs(6)
    print(pair_df)
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
