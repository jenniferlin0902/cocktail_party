import ingredient2vec
from gensim.models import word2vec
from trainerUtil import cocktailData, generate_ingredient_dict
import collections
from mdp import weightedRandomChoice
import joblib, random

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

def trainBiGram(sequences, depth, vocabs, numPermute):
    # Generate a start key of the appropriate depth
    startKey = []
    for j in range (0, depth):
        startKey.append(START_CHAR)
    startKey = tuple(startKey)
    # first build vocab
    transprobs = {}
    lenprobs = collections.defaultdict(float)
    print "training {} gram on {} sequences".format(depth, len(sequences))
    for i in range(len(sequences)):
        # Run trainer on 5 different permutations of the recipe
        for _ in range(numPermute):
            sequence = random_permute(sequences[i])
            # Start each recipe with a tuple of blank characters
            prevWords = startKey
            for word in sequence:
                # Add nonexistent previous ingredient sequences to dicts
                if prevWords not in transprobs.keys():
                        transprobs[prevWords] = collections.defaultdict(float)
                # Count this ingredient
                transprobs[prevWords][word] += 1
                # Add this ingredient to ingredient history
                prevWords = list(prevWords)
                prevWords.append(word)
                # Forget the oldest ingredient
                prevWords.pop(0)
                prevWords = tuple(prevWords)
                lenprobs[len(sequence)] += 1
    return transprobs, lenprobs

def generateFromBiGram(transprob, lenprob, depth, numRecipes):
    outputs = []
    for _ in range(numRecipes):
        maxlength = weightedRandomChoice(lenprob)
        print "chose length {}".format(maxlength)
        output = []
        # Create starting key: a tuple of <depth> start characters
        startKey = []
        for j in range (0, depth):
            startKey.append(START_CHAR)
        startKey = tuple(startKey)
        word = startKey
        count = 0
        while count < maxlength:
            # Randomly choose the next ingredient
            try:
                nextWord = weightedRandomChoice(transprob[word])
            except:
                print "error"
                break
            if nextWord == END_CHAR:
                break
            output.append(nextWord)
            # Add this ingredient to ingredient history
            word = list(word)
            word.append(nextWord)
            # Forget oldest ingredient
            word.pop(0)
            word = tuple(word)
            count += 1   
        outputs.append(output)   
    return outputs

def cluster2recipe(cluster2ingredient, sequence, data):
    output = []
    for s in sequence:
        finding = 1
        while finding:
            if cluster2ingredient[s] == {}:
                print "Got empty cluster {}".format(s)
                break

            ingredient = weightedRandomChoice(cluster2ingredient[s])
            unit = random.choice(list(data.get_ingredient_unit(ingredient)))

            if ingredient not in output:
                output.append(str(unit[0]) + " " + unit[1] + " " + ingredient)
                finding = 0
    return output

def generateNGramRecipes(data, depth, numPermutations, numRecipes, tokenized_recipe, cluster2ingredient):
    T, L = trainBiGram(tokenized_recipe, depth, range(n_cluster + 1), numPermutations)
    print "---- Generating {} gram recipe -----".format(depth)
    cluster_recipe = generateFromBiGram(T, L, depth, numRecipes)
    recipes = []    
    for r in cluster_recipe:
        recipes.append(cluster2recipe(cluster2ingredient, r, data))
    return recipes



ALL_DATA = 'cocktail_all.txt'
TRAIN_DATA = "cocktail_train.txt"
TRAINING = 1
PERM_VECTOR = 8
VECTOR_SIZE = 10
N_CLUSTER = 50

master_ingredient = generate_ingredient_dict(ALL_DATA, 5) 
data = cocktailData(TRAIN_DATA, master_ingredient)

prefix = str(PERM_VECTOR) + "_" + str(VECTOR_SIZE) + TRAIN_DATA.strip(".txt")
if TRAINING:
    model = ingredient2vec.train_ingredient2vec(data, p_vector=8, vector_size=10, freq_threshold=1)
else:
    model = word2vec.Word2Vec.load("freq_6_word2vec_5_15cocktail_all")
    ingredient_cluster = joblib.load("cluster_dict")


ingredient_cluster = ingredient2vec.train_ingredientclusters(model, data, N_CLUSTER)
# joblib.dump(ingredient_cluster, "cluster_dict_20")
#print ingredient_cluster
# generate recipe with cluster tag
print "done clustering"

tokenized_recipe = []
for recipe in data.get_recipes_ingredient_only():
    r = []
    for ingredient in recipe:
        if ingredient in ingredient_cluster:
            cluster = ingredient_cluster[ingredient]
        else:
            # dump all rare ingredients to a cluster
            cluster = N_CLUSTER
        r.append(cluster)
    tokenized_recipe.append(r)

cluster2ingredient = collections.defaultdict(dict)
for ingredient in data.get_ingredient_list():
    if ingredient in ingredient_cluster:
        cluster2ingredient[ingredient_cluster[ingredient]][ingredient] = data.ingredients[ingredient][0]
    else:
        cluster2ingredient[N_CLUSTER][ingredient] = data.ingredients[ingredient][0]

for d in [2,3,4]:
    file = "cluster_dt{}_v2_perm20_cluster50.txt".format(d)
    f = open(file, 'w')
    clusted_mdp_recipe = generateNGramRecipes(data, d, 20, 50, tokenized_recipe, cluster2ingredient)
    for r in clusted_mdp_recipe:
        output = "TITLE: "+";".join(r)+"\n"
        f.write(output)
    f.close()




#tri_gram = trainNGram(tokenized_recipe, 3)
#print "---- Generate tri gram recipe ------"
#for i in range(10):
    #cluster_recipe = tri_gram.generate(5)
    #print ",".join(cluster2recipe(cluster2ingredient, cluster_recipe))



