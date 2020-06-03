
# Generalizing rules.

_In which we study a training dataset to learn patterns that relate features of the cases to their observed outcomes, and attempt to apply these patterns to a test dataset._

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
These rules mean that some users thought that the terms 'cops', 'revolvers', and 'weapons' can be taken as indicators that a post belongs to the `talk.politics.guns` newsgroup, and that the terms 'muslim', 'Justice', 'discrimination' and 'second class citizen' indicate that a post belongs to `talk.politics.mideast`. Note that a term doesn't need to be just a single word, it can be a phrase.

The plan is to collect all the rules you and your fellow participants come up with, and apply them to a test set of newsgroup posts to see how well they let us figure out what newsgroup the post belongs to, just by looking at the content of the post. This kind of program is called a _classifier_ because it decides what group a post appears to belong to.

The test set has been kept separate from the group of posts users are shown when they pick the rules, so no rules have been created specifically to identify the posts in the test set. In other words, we will be evaluating the rules on their ability to *generalize* to new data.

To apply the rules to a test post, we compute the fraction of all the rule patterns we have for each newsgroup that are present in the post. Whichever newsgroup has the highest fraction of rules matching the post is the one we predict it belongs to.

Now, you can probably think of a lot of ways we could improve this process:

* Can you think of any useful statistics that you could gather about how often various words appear in each newsgroup? 
* How many different words do you need to use to identify each newsgroup? 
* How much did each rule actually help with the classification? Should they all be given the same amount of influence?
* Are there better ways to measure how well the classifier works? 

If you go far enough down this path, you will basically be re-inventing Machine Learning.
