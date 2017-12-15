from trainerUtil import cocktailData, split_data
from sklearn.decomposition import NMF, pca
from sklearn.cluster import KMeans
import random
import logging
import matplotlib.pyplot as plt
from gensim.models import word2vec
from matplotlib.colors import ListedColormap
import seaborn as sns

PERM_VECTOR = 5
VECTOR_SIZE = 2
FREQ = 1
TRAIN_DATA = 'cocktail_all.txt'

'''
This file contains function that trains ingredient2vec and use a trained ingredient2vec
model to cluster ingredients
'''

def random_permute(target):
    permute = list(target)
    for i in range(len(target)-1):
        j = random.randint(0, len(target)-i-1)
        swap = permute[i]
        permute[i] = permute[i + j]
        permute[i+j] = swap
    return permute

class iter_permutation:
    def __init__(self, vector):
        self.vector = vector
        self.p_index = 0
        self.v_index = 0
        self.max_permutate = PERM_VECTOR
    def __iter__(self):
        return self
    def next(self):
        # if reach end of p
        if self.p_index == self.max_permutate:
            self.v_index += 1
            self.p_index = 0
            #print "iterating {} recipe, total {} recipe".format(self.v_index, len(self.vector))

            if self.v_index == len(self.vector):
                self.v_index = 0
                raise StopIteration()

        result = random_permute(self.vector[self.v_index])
        self.p_index += 1
        return result


def print_recipe(r):
    print r.keys()

def train_ingredient2vec(train_data, p_vector=PERM_VECTOR, vector_size=VECTOR_SIZE, freq_threshold=FREQ):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    train_matrix = train_data.get_recipes_ingredient_only()

    print "Importing {} recipes with {} ingredients".format(train_data.n_recipe, train_data.n_ingredient)

    prefix = str(p_vector) + "_" + str(vector_size) + TRAIN_DATA.strip(".txt")

    model = word2vec.Word2Vec(iter_permutation(train_matrix),size=vector_size, workers=5, min_count=p_vector*freq_threshold)
    model.save("freq_{}_word2vec_".format(freq_threshold) + prefix)
    return model

def train_ingredientclusters(ingredient2vec, data, k):
    kmeans = KMeans(k)
    ingredients = data.get_ingredient_list()
    word_vector = {}
    for i in ingredients:
        word_vector[i] = ingredient2vec[i]
    ingredient_cluster = kmeans.fit_predict(word_vector.values())
    return dict(zip(word_vector.keys(), ingredient_cluster))




