from testing import cocktailSVMClassifier
from trainerUtil import cocktailData
from trainerUtil import split_data, generate_ingredient_dict
import matplotlib.pyplot as plt
import random

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
count = []
for v in train_data.ingredients.values():
    count.append(v[0])
print len(count)
plt.hist(count, bins=20)

plt.title("histogram of ingredient frequencies")
plt.xlabel("ingredient count")
plt.ylabel("frequency")
plt.show()
print "import {} recipe".format(train_data.n_recipe)
# print some stats for the train_data
count = 0
for k in train_data.ingredients:
    if len(train_data.ingredients[k][1]) > 1:
        #print k, train_data.ingredients[k]
        count += 1
print "got {} ingredients, {} ingredients have more than one unit".format(train_data.n_ingredient,count)

print "got {} train data".format(train_data.n_recipe)

classifier = cocktailSVMClassifier(train_data)
classifier.train(train_data)

fake_test_data = train_data.generate_fake(500)
print "{} : test accuracy = {}".format(TEST_DATA, classifier.test(test_data))
fake_x = []
fake_y = []
for x, y in fake_test_data:
	fake_x.append(x)
	fake_y.append(y)
print "test accuracy on 500 fake data = {}".format(classifier.test(fake_x, y=fake_y))

print "----- testing raw mdp data -----"
test_recipes = ["dt2.txt", "dt3.txt", "dt4.txt", "dt5.txt"]
for test_file in test_recipes:
	test_data = cocktailData(test_file, master_ingredient)
	print "{} : test accuracy = {}".format(test_file, classifier.test(test_data))

print "----- testing cluster mdp data -----" 
test_recipes = ["cluster_dt2.txt", "cluster_dt3.txt", "cluster_dt4.txt", "cluster_dt5.txt"]
for test_file in test_recipes:
	test_data = cocktailData(test_file, master_ingredient)
	print "{} : test accuracy = {}".format(test_file, classifier.test(test_data))

#run_classifier_test(train_data)
