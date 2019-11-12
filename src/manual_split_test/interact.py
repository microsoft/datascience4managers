#!/usr/bin/python
# Oct 2019  JMA
# interact.py  ds4mgrs tutorial on incremental classification 
'''
Collect user rules and rule them against test data. 

Usage:
$ ./interact.py [-v] [-d data_dir] [-g pattern]
    -v verbose output (more than normal)
    -d data directory to read from
    -q quiet output (less than normal)
    -r rules per sample (how deep into the sample sorted words)
    -p Rule pairs 
''' 
import os, sys
import copy
import glob
import math
import pprint
import subprocess
import sys
import re
import string
import time
from pathlib import Path
import pandas as pd
import splits_aggregator as sa
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
RULES_PER_SAMPLE = 1
RULE_PAIRS =40

INTERACTIVE_RULE_PAIRS = 0     # Create this many templates for users
SHARED_DIR  = Path('../../shared/')    # Users grab a file from here
INTERACTION_DIR  = Path('../../rules/')  # .. and copy their ss to this directory. 
INTERACTIVE = True

###############################################################################
def main(rules_dir, run_interactive):

    # Test split pattern extraction
    # input_pattern= glob_pattern + '*.csv'
    cs = sa.BinaryComparisons(PARQUET_DIR)
    pair_df = cs.random_pairs(INTERACTIVE_RULE_PAIRS) # 
    # Save pairs to shared directory 
    cs.embed_in_excel(pair_df)
    # Seed the model with a few auto-generated splits
    seed_df = cs.random_pairs(RULE_PAIRS)
    the_rules = cs.simulate_splits(seed_df)  # Creates simulated rules. 
    # While running interactively load new excel splits and add them to the rules
    # Load the test set
    # full_ds = pq.reload_parquet(data_paths) 
    summary_df = pd.DataFrame()
    while run_interactive:
        users = sa.CollectSplits(rules_dir)
        the_rules.extend(users.user_rules)  # combine lists
        if VERBOSE: pprint.pprint(the_rules)
        # Evaluate the ruleset and display. 
        learner = sa.SplitClassifier(the_rules)
        # TODO run this on both train and test sets. 
        learner.order_by_hits(cs.full_df)
        summary = learner.compute_confusion(cs.full_df)
        summary_df = summary_df.append(pd.DataFrame([summary]))
        # Check if the rules directory has any new files, then continue. 
        run_interactive = False
    print(summary_df)
    return 0

########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        PARQUET_DIR = Path(sys.argv[d+1]) # Assuming the path is relative to the user's home path 
    else:
        PARQUET_DIR = Path(DATA_DIR)
    
    if '-q' in sys.argv:
        q = sys.argv.index('-q')
        QUIET = True

    if '-r' in sys.argv:
        r = sys.argv.index('-r')
        RULES_PER_SAMPLE = int(sys.argv[r+1])

    if '-p' in sys.argv:
        p = sys.argv.index('-p')
        RULE_PAIRS = int(sys.argv[p+1])

    # np.set_printoptions(linewidth=100)
    main(INTERACTION_DIR, INTERACTIVE)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF