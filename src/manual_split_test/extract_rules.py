# Access rules web app
# JMA Nov 2019

import os
import sys
import numpy as np 
import pandas as pd 
from collections import namedtuple
import urllib.request

### config constants 
VERBOSE = True
RULES_URL = 'http://marinchapp10.azurewebsites.net/rules'
VANITY_URL = 'http://aka.ms/news-rules'
Rule = namedtuple('Rule', ['pattern', 'label', 'hits'])

SIMULATE_RULE_SETS = 10

class RuleExtraction(object):

    def __init__(self):
        self.cycle = 0
        self.selected_rules = 0
        self.total_rules = 0

    def extract_rules(self):
        with urllib.request.urlopen(RULES_URL) as response:
            url = response.read()
        self.the_submissions = url.decode(errors='ignore').split('\n')
        self.total_rules = len(self.the_submissions)
        if VERBOSE:
            print('User submitted rules: ', self.total_rules)

    def cycle_rules(self):
        'Grab an additional set of rules'
        self.cycle += 1
        if SIMULATE_RULE_SETS == 0:
            use_these_rules = self.the_submissions
        else:
            previous_size = self.selected_rules
            self.selected_rules = min(self.total_rules, self.selected_rules+SIMULATE_RULE_SETS)
            use_these_rules = self.the_submissions[previous_size:(self.selected_rules)]
            if VERBOSE:
                print('Selected', self.selected_rules)
        the_rules = []
        for a_rule in use_these_rules:
            pattern, lbl = self.clean_rule(a_rule)
            if pattern is not None:
                the_rules.append(Rule(pattern, lbl, 0))
                #if VERBOSE:
                #    print(the_rules[-1])
        return the_rules

    def clean_rule(self, a_rule):
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
    re = RuleExtraction()
    for k in range(10):
        re.extract_rules()
        print(len(re.cycle_rules()))

