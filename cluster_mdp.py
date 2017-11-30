import ingredient2vec
from gensim.models import word2vec
from trainerUtil import cocktailData
import collections
from mdp import weightedRandomChoice
import joblib, random

TRAIN_DATA = "cocktail_all.txt"
TRAINING = 0
PERM_VECTOR = 5
VECTOR_SIZE = 2
FREQ = 6
TRAIN_DATA = 'cocktail_all.txt'
data = cocktailData(TRAIN_DATA)
prefix = str(PERM_VECTOR) + "_" + str(VECTOR_SIZE) + TRAIN_DATA.strip(".txt")

if TRAINING:
    model = ingredient2vec.train_ingredient2vec(data)
else:
    model = word2vec.Word2Vec.load("freq_6_word2vec_5_15cocktail_all")
    ingredient_cluster = joblib.load("cluster_dict")

START_CHAR = "START"
END_CHAR = "END"

def random_permute(target):
    permute = list(target)
    for i in range(len(target)-1):
        j = random.randint(0, len(target)-i-1)
        swap = permute[i]
        permute[i] = permute[i + j]
        permute[i+j] = swap
    return permute

def trainBiGram(sequences, vocabs):
    # first build vocab
    transprobs = {}
    lenprobs = collections.defaultdict(float)
    transprobs[START_CHAR] = collections.defaultdict(float)
    for v in vocabs:
        transprobs[v] = collections.defaultdict(float)
    for i in range(len(sequences)):
        for _ in range(5):
            sequence = random_permute(sequences[i])
            prevWord = START_CHAR
            for word in sequence:
                transprobs[prevWord][word] += 1
                prevWord = word
        lenprobs[len(sequence)] += 1
    return transprobs, lenprobs

def generateFromBiGram(transprob, lenprob):
    maxlength = weightedRandomChoice(lenprob)
    print "chose length {}".format(maxlength)
    output = []
    word = START_CHAR
    count = 0
    while count < maxlength:
        nextWord = weightedRandomChoice(transprob[word])
        if nextWord == END_CHAR:
            break
        output.append(nextWord)
        word = nextWord
        count += 1
    return output

def cluster2recipe(cluster2ingredient, sequence):
    output = []
    for s in sequence:
        finding = 1
        while finding:
            ingredient = random.choice(cluster2ingredient[s])
            if ingredient not in output:
                output.append(ingredient)
                finding = 0
    return output

n_cluster = 20
ingredient_cluster = ingredient2vec.train_ingredientclusters(model, data, n_cluster)
joblib.dump(ingredient_cluster, "cluster_dict_20")
#print ingredient_cluster
# generate recipe with cluster tag
tokenized_recipe = []
for recipe in data.get_recipes_ingredient_only():
    r = []
    for ingredient in recipe:
        if ingredient in ingredient_cluster:
            cluster = ingredient_cluster[ingredient]
        else:
            # dump all rare ingredients to a cluster
            cluster = n_cluster
        r.append(cluster)
    tokenized_recipe.append(r)

cluster2ingredient = collections.defaultdict(list)
for ingredient in data.get_ingredient_list():
    if ingredient in ingredient_cluster:
        cluster2ingredient[ingredient_cluster[ingredient]].append(ingredient)
    else:
        cluster2ingredient[n_cluster].append(ingredient)


T, L = trainBiGram(tokenized_recipe, range(n_cluster + 1))

print "---- Generating bi gram recipe -----"
for i in range(10):
    cluster_recipe = generateFromBiGram(T, L)
    print ",".join(cluster2recipe(cluster2ingredient, cluster_recipe))

#tri_gram = trainNGram(tokenized_recipe, 3)
#print "---- Generate tri gram recipe ------"
#for i in range(10):
    #cluster_recipe = tri_gram.generate(5)
    #print ",".join(cluster2recipe(cluster2ingredient, cluster_recipe))



