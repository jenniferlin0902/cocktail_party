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
FREQ = 6
TRAIN_DATA = 'cocktail_all.txt'
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
            print "iterating {} recipe, total {} recipe".format(self.v_index, len(self.vector))

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

    prefix = str(PERM_VECTOR) + "_" + str(VECTOR_SIZE) + TRAIN_DATA.strip(".txt")

    model = word2vec.Word2Vec(iter_permutation(train_matrix),size=vector_size, workers=5, min_count=p_vector*freq_threshold)
    model.save("freq_{}_word2vec_".format(freq_threshold) + prefix)
    return model

def train_ingredientclusters(ingredient2vec, data, k):
    kmeans = KMeans(k)
    ingredients = data.get_ingredient_list()
    word_vector = {}
    for i in ingredients:
        try:
            word_vector[i] = ingredient2vec[i]
        except:
            print "found rare ingredient {}".format(i)
    ingredient_cluster = kmeans.fit_predict(word_vector.values())
    return dict(zip(word_vector.keys(), ingredient_cluster))

TRAINING = 0
data = cocktailData(TRAIN_DATA)
prefix = str(PERM_VECTOR) + "_" + str(VECTOR_SIZE) + TRAIN_DATA.strip(".txt")

if TRAINING:
    model = train_ingredient2vec(data)
else:
    model = word2vec.Word2Vec.load("freq_6_word2vec_5_15cocktail_all")

ingredient_cluster = train_ingredientclusters(model, data, 10)

cat = {}
for k, v in ingredient_cluster.iteritems():
    if v not in cat:
        cat[v] = []
    cat[v].append(k)

cat_fd = open("cat_" + prefix + ".txt", 'w')
for category in cat:
    cat_fd.write("-------- Category {} --------\n".format(category))
    cat_fd.write(", ".join(cat[category]) + "\n")
cat_fd.close()

my_cmap = ListedColormap(sns.color_palette(sns.color_palette("Set1", 20)).as_hex())
pca_model = pca.PCA(n_components=2)
word_vector = {}
for i in data.get_ingredient_list():
    try:
        word_vector[i] = model[i]
    except:
        pass

pca_result = pca_model.fit_transform(word_vector.values())
plt.scatter(pca_result[:, 0], pca_result[:, 1], c=ingredient_cluster.values())
plt.title("pca clustering " + prefix)

plt.savefig("pca_" + prefix)





