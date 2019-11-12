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
#from colorama import init, Fore, Back, Style
import colorama as cl
import pandas as pd
import splits_aggregator as sa
import pq 
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
RULES_PER_SAMPLE = 1
RULE_PAIRS =100
SS_SUFFIX = '*.csv'
ROOT_DIR = Path('D:/OneDrive - Microsoft/data/20news')
INTERACTIVE_RULE_PAIRS = 0     # Create this many templates for usersy. 
INTERACTIVE = True


###############################################################################
def main(root_dir, run_interactive):

    # Test split pattern extraction
    # input_pattern= glob_pattern + '*.csv'
    rules_dir = root_dir / "rules"
    cs = sa.BinaryComparisons(root_dir)
    pair_df = cs.random_pairs(INTERACTIVE_RULE_PAIRS) # 
    # Save pairs to shared directory 
    cs.embed_in_excel(pair_df)
    # Seed the model with a few auto-generated splits
    seed_df = cs.random_pairs(RULE_PAIRS)
    the_rules = cs.simulate_splits(seed_df)  # Creates simulated rules. 
    # While running interactively load new excel splits and add them to the rules
    # Load the test set
    test_df = pq.reload_parquet(root_dir / 'test_clean') 
    cl.init()
    summary_df = pd.DataFrame(columns = ['Train_acc','Train_pr', 'Train_rcl', 'Test_acc', 'Test_pr', 'Test_rcl'])
    user_rule_cnt = -1
    Reset = False 
    while run_interactive:
        # Check if the rules directory has any new files, then continue. 
        new_rule_cnt = len(list(rules_dir.glob( SS_SUFFIX)))
        if new_rule_cnt > user_rule_cnt:
            Reset = False
            users = sa.CollectSplits(rules_dir, SS_SUFFIX)
            the_rules.extend(users.user_rules)  # combine lists
            if VERBOSE: pprint.pprint(the_rules)
            # Evaluate the ruleset and display. 
            learner = sa.SplitClassifier(the_rules)
            # TODO run this on both train and test sets. 
            # learner.order_by_hits(cs.full_df)  # Don't need to tune the rules 
            summary_train = learner.compute_confusion(cs.full_df)
            # Do the same for the test data
            summary_test = learner.compute_confusion(test_df)
            summary_train.extend(summary_test)
            next_episode = pd.DataFrame([summary_train])
            next_episode.columns = ['Train_acc','Train_pr', 'Train_rcl', 'Test_acc', 'Test_pr', 'Test_rcl']
            summary_df = summary_df.append(next_episode, ignore_index=True)
            user_rule_cnt = new_rule_cnt
        else:
            time.sleep(2.0)
            if not Reset:
                print(cl.Fore.YELLOW + cl.Style.BRIGHT + 'Summary') 
                print(summary_df)
                print(cl.Fore.RESET)
                Reset = True
            # else:
    summary_df.to_csv(Path(root_dir)/'summary.csv', header=True, index=False)
    return 0

########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        ROOT_DIR = Path(sys.argv[d+1]) # Assuming the path is relative to the user's home path 
    # else:
    #     ROOT_DIR = Path(DATA_DIR) # TODO  no DATA_DIR!!
    
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
    main(ROOT_DIR, INTERACTIVE)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF