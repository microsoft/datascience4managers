# Access rules web app
# JMA Nov 2019

import os
import sys
import numpy as np 
import pandas as pd 
from collections import namedtuple
import urllib.request

### config constants 
VERBOSE = False
RULES_URL = 'http://marinchapp10.azurewebsites.net/rules'
VANITY_URL = 'http://aka.ms/news-rules'
Rule = namedtuple('Rule', ['pattern', 'label', 'hits'])


def extract_rules():
    with urllib.request.urlopen(RULES_URL) as response:
        url = response.read()
    the_submissions = url.decode(errors='ignore').split('\n')
    # if VERBOSE:
    print('User submitted rules: ', len(the_submissions))

    the_rules = []
    for a_rule in the_submissions:
        pattern, lbl = clean_rule(a_rule)
        if pattern is not None:
            the_rules.append(Rule(pattern, lbl, 0))
            if VERBOSE:
                print(the_rules[-1])
    return the_rules

def clean_rule(a_rule):
        if (type(a_rule) is str) and ( len(a_rule) > 0):
            comma_loc = a_rule.find(',')
            period_loc = a_rule.find('.')
            # Well formed rule has a pattern at least of len 3, and a label
            # that contains a period
            if period_loc > 0 and comma_loc < len(a_rule)-3 and period_loc < comma_loc:
                lbl, pattern = a_rule.split(',')
                return pattern, lbl
            else: 
                return None, None
        else:
            return None, None

if __name__ == '__main__':
    extract_rules()
