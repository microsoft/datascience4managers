#!/usr/bin/python
# Oct 2019  JMA
# make_samples.py  Use the splits_aggregator module to create samples
'''
Write a short description of what the program does here. 

Usage:
$ ./make_samples.py [-v] [-d SAMPLES_DIR] [-g pattern]
    -v verbose output
    -d data directory to read from
    -g glob pattern for data files
''' 
import os, os.path, sys
import glob
import pprint
import re
import time
import pyarrow
import pandas as pd
import splits_aggregator as sa

### config constants 
VERBOSE = False
PARQUET_DIR  = 'D:/OneDrive - Microsoft/data/20news/20news-bydate-train', # Need not end in /
GLOB_PATTERN = '*'

########################################################################
class x(object):
    'Prune the newsgroups text to create a labelled table.'
    pass

###############################################################################
def main(input_dir, glob_pattern):

    cs = sa.BinaryComparisons(PARQUET_DIR)
    # if VERBOSE: 
    #     pprint.pprint(msg_ds.train_df)
    # msg_ds.persist()



########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        PARQUET_DIR = sys.argv[d+1] # Assuming the path is relative to the user's home path 
    else:
        PARQUET_DIR = os.path.abspath(PARQUET_DIR)
    
    if '-g' in sys.argv:
        g = sys.argv.index('-g')
        GLOB_PATTERN = sys.argv[g+1]  

    main(PARQUET_DIR, GLOB_PATTERN)

    print(sys.argv, "\nDone in ", 
            '%5.3f' % time.process_time(), 
            " secs! At UTC: ", 
            time.asctime(time.gmtime()), file=sys.stderr)