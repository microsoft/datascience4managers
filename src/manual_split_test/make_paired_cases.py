#!/usr/bin/python
# Oct 2019  JMA
# make_samples.py  Use the splits_aggregator module to create samples
'''
Write a short description of what the program does here. 

Usage:
$ ./make_samples.py [-v] [-d ROOT_DIR] [-c pair_cnt]
    -v verbose output
    -d data directory to read from
    -c number of randomly paired cases to generate
''' 
import os, sys
import glob
import pprint
import re
import time
from pathlib import Path
import pyarrow
import pandas as pd
import splits_aggregator as sa

### config constants 
VERBOSE = False
ROOT_DIR = Path('D:/OneDrive - Microsoft/data/20news')

PAIR_CNT = 1

########################################################################
class x(object):
    ''
    pass

###############################################################################
def main(input_dir, pair_cnt):

    cs = sa.BinaryComparisons(input_dir)
    pairs_df = cs.random_pairs(pair_cnt)
    if VERBOSE:
        print("Pairs: ", pairs_df.shape)
    cs.embed_in_excel(pairs_df)


########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        ROOT_DIR = Path(sys.argv[d+1])
 #   else:

    
    if '-c' in sys.argv:
        g = sys.argv.index('-c')
        PAIR_CNT= int(sys.argv[g+1]) 

    main(ROOT_DIR, PAIR_CNT)

    print(sys.argv, "\nDone in ", 
            '%5.3f' % time.process_time(), 
            " secs! At UTC: ", 
            time.asctime(time.gmtime()), file=sys.stderr)