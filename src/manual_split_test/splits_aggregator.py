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
from collections import namedtuple
import numpy as np
import pandas as pd
import bokeh as bk
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
from bokeh.plotting import figure
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
import pq
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
DATA_DIR  = Path('../../shared/')  # ?! TODO
SHARED_DIR  = '../../shared/'
# GLOB_PATTERN = 'language_selection_tests'

Rule = namedtuple('Rule', ['pattern', 'label', 'hits'])


########################################################################
class CollectSplits(object):
    'Collect csv files from participants and aggregate.' 
    
    def __init__(self, glob_pattern, cvs_dir):
        self.tst_lbls = []
        self.as_df = None
        for data_file in Path(cvs_dir).glob( glob_pattern):
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
        self.full_df = pq.reload_parquet(data_paths)       # 'merge all training data'
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
            # if VERBOSE: print (reps, pair)
            row = np.hstack([pair.iloc[0,].values, pair.iloc[1,].values]) 
            pair_df = np.vstack([pair_df, row])
        pair_df = pd.DataFrame(pair_df)
        pair_df.columns = ['label1', 'item1', 'msg1', 'label2', 'item2', 'msg2']
        return pair_df

    def simulate_splits(self, pair_df):
        'Find pairs of words that distinguish the pair. '
        selection_rules = []
        for r in range(len(pair_df)):
            row = pair_df.iloc[r,]
            msg1 = row[2]
            lbl1 = row[0]
            msg2 = row[5]
            lbl2 = row[3]
            # Cheap heuristic - use the longest word as a candidate classifiers
            w1 = sorted(msg1.split(), key= lambda w: len(w), reverse=True)
            w2 = sorted(msg2.split(), key= lambda w: len(w), reverse=True)
            # Check if the word appears in the opposite sample and fail if it does. 
            if not (w1[0] in msg2.split()):
               selection_rules.append(Rule(w1[0], lbl1, 0))
            else:
                print('Failed selection rule ', lbl2, ':', w1[0])
            if not (w2[0]  in msg1.split()):
               selection_rules.append(Rule(w2[0], lbl2, 0))
            else:
                print('Failed selection rule ', lbl1, ':', w2[0])
            if not (w1[1] in msg2.split()):
               selection_rules.append(Rule(w1[1], lbl1, 0))
            else:
                print('Failed selection rule ', lbl2, ':', w1[1])
            if not (w2[1]  in msg1.split()):
               selection_rules.append(Rule(w2[1], lbl2, 0))
            else:
                print('Failed selection rule ', lbl1, ':', w2[1])
        return selection_rules


    def embed_in_excel(self, pairs, groups_template = Path('../../template/pairwise_comparisions.csv')):
        'Export ss files with examples of pair-wise comparisons that users can fill in and submit. '
        ss = dict(group1 = (4,3), group2=(4,4), pattern1=(5,3), pattern2=(5,4), sample1=(7,3), sample2=(7,4))
        if groups_template.exists():
            the_template= pd.read_csv(groups_template, header=None )
        else:
            print(groups_template, " not found", file=sys.stderr)
            return None
        for k in range(len(pairs)):
            comp = copy.copy(the_template)
            a_pair = pairs.iloc[k,]
            comp.iloc[ss["group1"]] = a_pair['label1'] # ['label1', 'item1', 'msg1', 'label2', 'item2', 'msg2']
            comp.iloc[ss["group2"]] = a_pair['label2']
            comp.iloc[ss["sample1"]] = a_pair['msg1']
            comp.iloc[ss["sample2"]] = a_pair['msg2']
            if VERBOSE:
                for vals in ss.values():
                    print(comp.iloc[vals])
            case_fn = Path(SHARED_DIR) / (str(a_pair["item1"]) + '-' + str(a_pair["item2"]) + '.csv')
            comp.to_csv(case_fn, header=False, index=False )

########################################################################
class SplitClassifier (object):
    'Assemble the splits are run them with highest precision lowest coverage first.'

    def __init__(self, rules):
        self.rules = rules

    def order_by_hits(self, full_df):
        'Run each rule over all msgs, counting msgs that fire the rule.'
        # TODO count the number of hits over all samples for each rule. 
        hits = [0] * len(self.rules)
        match = 0
        miss = 0
        for j, a_rule in enumerate(self.rules):
            for k, v in enumerate(full_df['msg']):
                if a_rule.pattern in v:
                    # Add a count of how many times the rule matches
                    hits[j] += 1  
                    if a_rule.label == full_df['label'].iloc[k]:
                        if VERBOSE: print(k,'-', a_rule.label, ':',a_rule.pattern)
                        match +=1
                    else:
                        #print(a_rule.label, ':',full_df['label'].iloc[k] , end = ' ')
                        miss +=1
            print(f'\n{j}:{a_rule.pattern} Match {match}, miss {miss}, hits {hits[j]}.')
        print(f'\n============\nMatch {match}, miss {miss}.')
        # Sort by most specific rules first. 


    def compute_confusion(self, full_df):
        'Return the confusion matrix and stats for this classifier.'
        # Run the ruleset over the sample item until a rule fires
        # Then record the class of the rule.
        predicted_labels = len(full_df)*["None"]
        for k, content in enumerate(full_df['msg']):
            for j, a_rule in enumerate(self.rules):
                if a_rule.pattern in content:
                    predicted_labels[k] = a_rule.label
                    break
        # print("compute_confusion", len([x for x in predicted_labels if x is not None]), len(full_df))
        true_y = list(full_df["label"])
        class_names = list(set(true_y))
        #class_names.append("None")
        cm = confusion_matrix(true_y, predicted_labels, class_names) 
        #cm = cm[0:19,0:19]
        print(cm) 
        print(class_names)
        diagonal = sum([cm[x,x] for x in range(len(class_names))])
        totals = sum(sum(cm))
        print("Accuracy=", diagonal, ' / ', totals, ' = ', diagonal/totals)
        prfs = precision_recall_fscore_support(true_y, predicted_labels, labels=class_names)
        prfs_df = pd.DataFrame.from_dict(dict(prec= prfs[0],recall=prfs[1],F=prfs[2], sup=prfs[3], nms=class_names) )
        prfs_df.set_index('nms', inplace=True)
        print(prfs_df)


###############################################################################
def main(input_dir):

    # Test split pattern extraction
    # input_pattern= glob_pattern + '*.csv'
    cs = BinaryComparisons(PARQUET_DIR)
    # print("train: ", cs.full_df.shape)
    pair_df = cs.random_pairs(350)
    the_splits = cs.simulate_splits(pair_df)  # Creates simulated rules. 
    # pprint.pprint(the_splits)
    learner = SplitClassifier(the_splits)
    learner.order_by_hits(cs.full_df)
    learner.compute_confusion(cs.full_df)
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
    
    # if '-g' in sys.argv:
    #     g = sys.argv.index('-g')
    #     GLOB_PATTERN = sys.argv[g+1]

    np.set_printoptions(linewidth=100)
    main(DATA_DIR)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF
