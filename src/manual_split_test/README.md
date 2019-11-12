# README.md - Setup

Setting up the interactive demonstration from the original 20news train and test sets. For the first session in the lab. We start by walking through the process of trying to build a 'topic classifier', that is, a program that can look at some textual data and decide what topci thread it belongs to, using traditional hard-coded logic. ? For individual rules you may create, did the new rule you added to your classifier program make it better? As we show, machine learning is basically just automating this type of process. 

## Directory structure

In ROOT_DIR, e.g. "OneDrive - Microsoft/data/20news"

    - 20_news-bydate-test
    - 20_news_bydate-train
    - test_clean
    - train_clean
    - patterns
    - rules


## Create the clean samples as parquet files - one for each class folder, for test and train. 

`make_samples.py`

- create csv copies of each sample parquet file (they are easier to read)

- create a consolidated file `full_df.parquet` in both `test_clean` and `train_clean` directories

## Create random pairs of test samples and save as csv files. 

`make_paired_cases.py`

## Run test and train using crude rule heuristic

`splits_aggregator.py`

## Run the interactive session using patterns that users fill in of random pairs

`interact.py`



