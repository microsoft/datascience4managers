
# Generalizing rules.

_In which we study a training dataset to learn patterns that relate features of the cases to their observed outcomes, and attempt to apply these patterns to a test dataset._

## Contents

- Start with the slides [Learning_vs_Coding.pdf](https://github.com/microsoft/datascience4managers/blob/master/Part_1/Learning_vs_Coding.pdf), then when you get to the Demo section, try the exercise on manualy constructing a text classifier. 
- The Demo has a web interface for you to create classification rules incrementally. You will see how performance changes as more rules are added. Finally you can compare the performance to a machine learning classifier trained on the same data.

## Exercise

In this exercise we will be trying to build a text classifier, that is, a program that can look at some textual data and decide what category it belongs to. You will be asked to examine a number of vintage newsgroup posts and identify terms or phrases that you think will be useful for identifying other posts in that same newsgroup. We will be using two web apps:

* the [rule authoring web app](https://marinchapp10.azurewebsites.net/) is where you can add your rules to the database. It shows you example posts (from the training set) and lets you pick phrases that you think are indicative of belonging to that newsgroup.

* the [rule performance webapp](https://ml4managers.shinyapps.io/evaluate_rules/) lets you see how the well the whole collection of rules works on a held-out test set
(see [Part 2](../Part_2) to learn about confusion matrixes and ROC curves, which are shown in this app).

Here are some examples of rules people have come up with previously:
```
talk.politics.guns,cops
talk.politics.guns,revolvers
talk.politics.guns,weapons
talk.politics.mideast,muslim
talk.politics.mideast,Justice
talk.politics.mideast,discrimination
talk.politics.mideast,second class citizens
```
A rule consists of a newsgroup name corresponding to a class, and a phrase meant to distiguish it from the other newsgroups. These examples mean that some users thought that the terms 'cops', 'revolvers', and 'weapons' can be taken as indicators that a post belongs to the `talk.politics.guns` newsgroup, and that the terms 'muslim', 'Justice', 'discrimination' and 'second class citizen' indicate that a post belongs to `talk.politics.mideast`. Note that a term doesn't need to be just a single word, it can be a phrase.

The plan is to incrementally apply all the rules you and your fellow participants come up with, and apply them to a test set of newsgroup posts to see how well they determine what newsgroup the post belongs to, just by looking at the content of the post. This kind of program is called a _classifier_ because it decides what group a post appears to belong to.

### Evaluation

The rules are tested by applying them to a hold-out set of posts. To apply the rules to a test post, we compute the fraction of all the rule patterns we have for each newsgroup that are present in the post. Whichever newsgroup has the highest fraction of rules matching the post is the one we predict it belongs to.

The test set has been kept separate from the group of posts users are shown when they pick the rules, so for fairness no rules have been created with knowledge of the posts in the test set. In other words, we will be evaluating the rules on their ability to *generalize* to new data.

The evaluation results are shown in the rule performance website as a confusion matrix over the 20 newsgroup-classes and by an ROC curve for each class against the remaining classes. 

### Comparing manual rules with an automated classifier's method

Now, you can probably think of a lot of ways we could improve this process:

* Can you think of any useful statistics that you could gather about how often various words appear in each newsgroup? 
* How many different words do you need to use to identify each newsgroup? 
* How much did each rule actually help with the classification? Should they all be given the same amount of influence?
* Are there better ways to measure how well the classifier works? 

If you go far enough down this path, you will basically be re-inventing Machine Learning.  In conclusion, you should note that the automated classifier example run on the same data consistently is more accurate than the combination of all manually created rules in the database. This is shown in the [ML_classifier_results.md](https://github.com/microsoft/datascience4managers/blob/master/Part_1/ML_classifier_results.md) document. 
