from testing import cocktailSVMClassifier
from trainerUtil import cocktailData
from trainerUtil import split_data
import matplotlib.pyplot as plt
import random

TRAIN_DATA = 'cocktail_all.txt'
TEST_DATA = 'mcd1-output.txt'


#print test_data.recipes
train_data = cocktailData(TRAIN_DATA)
small_traindata =
test_data = cocktailData(TEST_DATA, train_data.ingredients)
print test_data.n_recipe
tester = cocktailSVMClassifier(train_data)
tester.train(verbose=1, validate=True)

print tester.test(test_data)
print tester.test()
