# Convert parquet to csv dataframes. 
import os, os.path, sys
import glob
import pprint
import re
import time

PATH = 'D:\\OneDrive - Microsoft\\data\\20news\\20news-bydate-train\\rec.motorcycles.parquet'
import pyarrow
import pandas as pd

def cnvt2csv(PATH):
    try:
        adf = pd.read_parquet(PATH)
        print(adf.describe())
    except Exception as e:
        print(f"for file {PATH} got exception {e}.")
    new_name = PATH.replace('parquet', 'csv')
    adf.to_csv(new_name)
    print('wrote ', new_name)

for a_file in glob.glob('*.parquet'):
    print('For ', a_file, end='\t')
    cnvt2csv(a_file)

