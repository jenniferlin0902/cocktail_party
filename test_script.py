from testing import cocktailSVMClassifier
from trainerUtil import cocktailData
from trainerUtil import split_data, generate_ingredient_dict
import matplotlib.pyplot as plt
import random
import joblib

'''
This test scripts run SVM classifier against the generated cocktail recipes.
'''

ALL_DATA = 'cocktail_all.txt'
TRAIN_DATA = 'cocktail_train.txt'
TEST_DATA = 'cocktail_test.txt'

def run_classifier_test(train_data):
    test_data = train_data.generate_fake(100)
    clf = cocktailSVMClassifier(train_data)
    clf.train(verbose=1, validate=True)
    print clf.test(test_data)


master_ingredient = generate_ingredient_dict(ALL_DATA, 5)
train_data = cocktailData(TRAIN_DATA, master_ingredient)
test_data = cocktailData(TEST_DATA, master_ingredient)

classifier = cocktailSVMClassifier(train_data)
classifier.train(train_data)
comb_classifier = cocktailSVMClassifier(train_data)
comb_classifier.train_clf_comb()
joblib.dump(comb_classifier, "comb_classifier")
#comb_classifier = joblib.load("comb_classifier")
test_acc = comb_classifier.test_comb(test_data)
print "got test_acc = {}".format(test_acc)

# Test with single feature SVM
'''
print "----- testing raw mdp data -----"
test_recipes = ["dt2.txt", "dt3.txt", "dt4.txt", "dt5.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, classifier.test(test_data))

print "----- testing cluster mdp data -----" 
test_recipes = ["cluster_dt2_v2_perm5.txt", "cluster_dt3_v2_perm5.txt", "cluster_dt4_v2_perm5.txt", "cluster_dt5_v2_perm5.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, classifier.test(test_data))

print "----- testing cluster mdp data -----" 
test_recipes = ["cluster_dt2_v2_perm5_cluster50.txt", "cluster_dt3_v2_perm5_cluster50.txt", "cluster_dt4_v2_perm5_cluster50.txt", "cluster_dt5_v2_perm5_cluster50.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, classifier.test(test_data))

#run_classifier_test(train_data)


print "----- testing btd mdp data ---"
test_recipes = ["btd1.txt", "btd2.txt", "btd3.txt", "btd4.txt", "btd5.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, comb_classifier.test_comb(test_data))
'''

# Testing with combination feature SVM
print "----- testing raw mdp data -----"
test_recipes = ["cluster_dt2_v2_perm5_cluster50.txt", "cluster_dt3_v2_perm5_cluster50.txt", "cluster_dt2_v2_perm20_cluster50.txt", "cluster_dt3_v2_perm20_cluster50.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, comb_classifier.test_comb(test_data))

print "----- testing cluster mdp data -----"
test_recipes = ["cluster_dt2_v2_perm5.txt", "cluster_dt3_v2_perm5.txt", "cluster_dt4_v2_perm5.txt", "cluster_dt5_v2_perm5.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, comb_classifier.test_comb(test_data))

print "----- testing cluster mdp data -----"
test_recipes = ["cluster_dt2_v2_perm5_cluster50.txt", "cluster_dt3_v2_perm5_cluster50.txt", "cluster_dt4_v2_perm5_cluster50.txt", "cluster_dt5_v2_perm5_cluster50.txt"]
for test_file in test_recipes:
    test_data = cocktailData(test_file, master_ingredient)
    print "{} : test accuracy = {}".format(test_file, comb_classifier.test_comb(test_data))
