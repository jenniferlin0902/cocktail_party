from testing import cocktailSVMClassifier
from trainerUtil import cocktailData
import random

TRAIN_DATA = 'cocktail_small.txt'

def run_classifier_test(train_data):
    test_data = train_data.generate_fake(100)
    clf = cocktailSVMClassifier(train_data)
    clf.train(verbose=1, validate=True)
    print clf.test(test_data)


train_data = cocktailData(TRAIN_DATA)
print "import {} recipe".format(train_data.n_recipe)
# print some stats for the train_data
count = 0
for k in train_data.ingredients:
    if len(train_data.ingredients[k][1]) > 1:
        #print k, train_data.ingredients[k]
        count += 1
print "got {} ingredients, {} ingredients have more than one unit".format(train_data.n_ingredient,count)

run_classifier_test(train_data)
