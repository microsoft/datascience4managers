import os, os.path, sys
import glob
import pprint
import re
import time
import pyarrow
import pandas as pd

PATH = 'D:\\OneDrive - Microsoft\\data\\20news\\20news-bydate-train\\rec.motorcycles.parquet'
try:
    adf = pd.read_parquet(PATH)
    print(adf.describe())
except Exception as e:
    print(f"for file {PATH} got exception {e}.")

