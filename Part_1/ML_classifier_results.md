These plots show the results of training an ML model on the same training set used for selecting rules, and evaluating it on the same test set. The TF/IDF of the words from the posts taken one at a time (unigrams) or two at a time (bigrams) were used as generate features, which were run through a LogisticRegression classifier in the Python `slkearn` library.


![](images/figure-markdown_strict/ML_confusion_matrix.png)
![](images/figure-markdown_strict/ML_ROC_curves.png)
