#!/usr/bin/python
# Oct 2019  JMA
# splits_aggregator.py  write scale events to mongoDB
'''
Run a simulation of interactive incremental classification.

Usage:
$ ./splits_aggregator.py [-v] [-d root_dir] [-g pattern]
    -v verbose output (more than normal)
    -d root directory to read from
    -q quiet output (less than normal)
    -r rules per sample (how deep into the sample sorted words)
    -p Rule pairs 
''' 
import os
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
# import bokeh as bk
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
import metric_graphics as mg
import pq
__author__ = 'John Mark Agosta john-mark.agosta@microsoft.com'

### config constants 
VERBOSE = False
ROOT_DIR = Path('D:/OneDrive - Microsoft/data/20news')
QUIET = True
RULES_PER_SAMPLE = 1
RULE_PAIRS =400

Rule = namedtuple('Rule', ['pattern', 'label', 'hits'])
ss = dict(group1 = (4,3), group2=(4,4), pattern1=(5,3), pattern2=(5,4), sample1=(7,3), sample2=(7,4))


########################################################################
class CollectSplits(object):
    'Collect csv files from participants and aggregate.' 
    
    def __init__(self, cvs_dir, glob_pattern = '*.csv'):
        self.user_rules = []
        #self.as_df = None
        for k, data_file in enumerate(cvs_dir.glob( glob_pattern)):
            print(k,':', end = ' ')
            try:
                self.add_file(data_file)
            except Exception as err:
                print(f"{err}\nSkipping file: {data_file} Cannot load it.", file=sys.stderr)


    def add_file(self, the_fname):
        'convert ss to rule'
        self.as_df = pd.read_csv(the_fname, header=None )
        #patterns = (self.as_df.iloc[ss['pattern1']], self.as_df.iloc[ss['pattern2']])  # comp.iloc[ss["group1"]]
        # Create rules out of the pattens. 
        try:
            rule1 = Rule(self.get_cell('pattern1'),  self.get_cell('group1'), 0)
            self.user_rules.append(rule1)
            rule2 = Rule(self.get_cell('pattern2'),  self.get_cell('group2'), 0)
            self.user_rules.append(rule2)
            if VERBOSE: 
                print("Rule patterns: ", rule1, rule2)
        except ValueError:
            print(the_fname, " corrupt contents", file=sys.stderr)

    def get_cell(self, cell_name):
        cell = self.as_df.iloc[ss[cell_name]]
        if (type(cell) is str) and (len(cell) > 2):
            cell =  cell.strip('"\'')
            return cell
        else:
            raise ValueError


########################################################################

########################################################################
class BinaryComparisons(object):
    'Randomly pair training cases to find words specific to each class.'
    def __init__(self, input_dir):
        self.patterns_dir  = input_dir / 'patterns'
        self.rules_dir = input_dir / 'rules'
        # check that the shared and rules directories have been created. 
        if not self.patterns_dir.exists():
            self.patterns_dir.mkdir()
        if not self.rules_dir.exists():
            self.rules_dir.mkdir()
        self.full_df = pq.reload_parquet(input_dir / 'train_clean')       # 'merge all training data'
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
            # Create rules out of the first RULES_PER_SAMPLE words
            for k in range(RULES_PER_SAMPLE):
            # Check if the word appears in the opposite sample and fail if it does. 
                if len(w1) > 0 and not (w1[k] in msg2.split()):
                    selection_rules.append(Rule(w1[k], lbl1, 0))
                else:
                    print('Failed selection rule ', lbl2, ':', w1[k], file=sys.stderr)
                if len(w2) and not (w2[k]  in msg1.split()):
                    selection_rules.append(Rule(w2[k], lbl2, 0))
                else:
                    print('Failed selection rule ', lbl1, ':', w2[k], file=sys.stderr)
        # if not QUIET: 
        print(len(selection_rules), " selection rules.")
        return selection_rules


    def embed_in_excel(self, pairs, groups_template = Path('../../template/pairwise_comparisions.csv')):
        'Export ss files with examples of pair-wise comparisons that users can fill in and submit. '
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
            case_fn = self.patterns_dir / (str(a_pair["item1"]) + '-' + str(a_pair["item2"]) + '.csv')
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
            if not QUIET: print(f'\n{j}:{a_rule.pattern} Match {match}, miss {miss}, hits {hits[j]}.')
        print(f'\n============\nMatch {match}, miss {miss}, TOT {match+miss}.')
        # TODO Sort by most specific rules first. 


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
        true_y = list(full_df["label"])
        class_names = list(set(true_y))
        cm = confusion_matrix(true_y, predicted_labels, class_names) 
        # Accuracy
        diagonal = sum([cm[x,x] for x in range(len(class_names))])
        totals = sum(sum(cm))
        print("Accuracy on matches =", diagonal, ' / ', totals, ' = ', diagonal/totals)
        cm = pd.DataFrame(cm, index=class_names)
        print(cm) 
        prfs = precision_recall_fscore_support(true_y, predicted_labels, labels=class_names)
        prfs_df = pd.DataFrame.from_dict(dict(prec= prfs[0],recall=prfs[1],F=prfs[2], sup=prfs[3], nms=class_names) )
        # Compute macro averages
        colsums = np.sum(prfs_df.values, axis=0)
        colavgs = list(colsums[0:4]/len(prfs_df))
        colavgs.append("AVGS")
        prfs_df = prfs_df.append(pd.DataFrame([colavgs], columns= ['prec', 'recall', 'F', 'sup', 'nms']))# 
        prfs_df.set_index('nms', inplace=True)
        print(prfs_df)
        # mg.matrix_heatmap(prfs_df)
        return [diagonal/totals, colavgs[0], colavgs[1]]# dict(accuracy=diagonal/totals, precision=colavgs[0], recall=colavgs[1]) 


###############################################################################
def main(input_dir):

    # Test split pattern extraction

    cs = BinaryComparisons(input_dir)
    pair_df = cs.random_pairs(RULE_PAIRS)
    the_rules = cs.simulate_splits(pair_df)  # Creates simulated rules. 
    if VERBOSE: pprint.pprint(the_rules)
    learner = SplitClassifier(the_rules)
    # learner.order_by_hits(cs.full_df)
    learner.compute_confusion(cs.full_df)
    # Do the same for the test data
    test_df = pq.reload_parquet(input_dir / 'test_clean')
    learner.compute_confusion(test_df)
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
    #     ROOT_DIR = Path(DATA_DIR)
    
    if '-q' in sys.argv:
        q = sys.argv.index('-q')
        QUIET = True

    if '-r' in sys.argv:
        r = sys.argv.index('-r')
        RULES_PER_SAMPLE = int(sys.argv[r+1])

    if '-p' in sys.argv:
        p = sys.argv.index('-p')
        RULE_PAIRS = int(sys.argv[p+1])

    np.set_printoptions(linewidth=100)
    main(ROOT_DIR)
    print(sys.argv, "\nDone in ", '%5.3f' % time.process_time(), " secs! At UTC: ", time.asctime(time.gmtime()), file=sys.stderr)

#EOF
