# Convert parquet to csv dataframes. 
import os, os.path, sys
import glob
import pprint
import re
import time

PARQUET_PATH = 'D:\\OneDrive - Microsoft\\data\\20news\\20news-bydate-train\\train_clean'
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

def consolidate_parquet(PATH):
    full_df = pd.DataFrame()
    for a_file in glob.glob(os.path.join(PATH, '*.parquet')):
        try:
            adf = pd.read_parquet(a_file)
        except Exception as e:
            print(f"for file {a_file} got exception {e}.")
        full_df = pd.concat([full_df, adf])
    print("Full df:", full_df.shape)
    return full_df

# consolidate_parquet(PARQUET_PATH)
