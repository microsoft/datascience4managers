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
import pprint
import re
import time
import pyarrow
import pandas as pd

### config constants 
VERBOSE = False
SAMPLES_DIR  = os.path.join(os.getcwd() ,'../../shared/') 
GLOB_PATTERN = '*'

########################################################################
class CreateNewsGroupsData(object):
    'Prune the newsgroups text to create a labelled table'

    def __init__(self, 
                data_path= 'D:/OneDrive - Microsoft/data/20news/20news-bydate-train/rec.motorcycles/', # Must end in /
                data_range=(104986, 105065)):
        self.train_df = []
        self.label = re.search(r'([^/]+)/$', data_path).group(1)
        self.save_path = re.sub(self.label+'/', '', data_path)
        for sample_file in range(data_range[0], data_range[1]):
            file_path = os.path.abspath(os.path.join(data_path, str(sample_file)))
            if os.path.exists(file_path):
                the_contents = open(file_path, 'r' ).readlines()
                pruned_contents = self.prune_contents(the_contents)
                if VERBOSE:
                    print('For msg: ', sample_file, ' Found', pruned_contents)
                if pruned_contents[0] > 1:
                    self.train_df.append((self.label, str(sample_file), pruned_contents[1]))
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

    def persist(self):
        print(f'\n{len(self.train_df)} records found.')
        the_df = pd.DataFrame(self.train_df)
        the_df.columns = ('label', 'item', 'msg')
        the_df.to_parquet(self.save_path + self.label + '.parquet')


###############################################################################
def main(input_dir, glob_pattern):

    # Test content extraction
    msg_ds = CreateNewsGroupsData(input_dir) 
    if VERBOSE: 
        pprint.pprint(msg_ds.train_df)
    msg_ds.persist()



########################################################################
if __name__ == '__main__':

    if '-v' in sys.argv:
        k = sys.argv.index('-v')
        VERBOSE = True

    ## Inputs
    if '-d' in sys.argv:
        d = sys.argv.index('-d')
        SAMPLES_DIR = sys.argv[d+1] # Assuming the path is relative to the user's home path 
    else:
        SAMPLES_DIR = os.path.abspath(SAMPLES_DIR)
    
    if '-g' in sys.argv:
        g = sys.argv.index('-g')
        GLOB_PATTERN = sys.argv[g+1]  


    main(SAMPLES_DIR, GLOB_PATTERN)
    print(sys.argv, "\nDone in ", 
            '%5.3f' % time.process_time(), 
            " secs! At UTC: ", 
            time.asctime(time.gmtime()), file=sys.stderr)