# cocktail_party

# Overview
This repository contains modules and scripts to analyze and genearte new
cocktail recipes.

tranerUtil.py contains helper functions for file I/O. In particular, cocktailData
class will be the data manipulate interface for all other modules in the
repository.

mdp.py and mdp_cluster.py contains functions to generate cocktail recipes using
n-depth mdps.

ingredient2vec.py contains functions to convert an ingredient to a n-diemsional
word embedding vector and ingredient categorization functions.

testing.py contains classifier that can classify a good (similar to a human generated)
and bad (randomly generated) recipe.

test_script.py usees SVMClassifier in testing.py to test recipes.

category.py

# Dependencies
sklearn - classifier, ingredient/recipe clustering, data processing
gensim - ingredient2vec

# Quick start
1. Import data:
   Note that to enforce the same ingredient id across all data classes, one should
   generate ingredient dict by calling `trainerUtil.generate_ingredient_dict(file, threshold), where
   file contains all cocktail recipes`
   Different data set can then be imported by using `trainerUtil.cocktailData(file, ingredients)``
   For example
   ```
   master_ingredient = trainerUtil.generate_ingredient_dict(ALL_DATA, 5)
   train_data = trainerUtil.cocktailData(TRAIN_DATA, master_ingredient)
   ```
2. Ingredient clustering:
   Train ingredient2vec model
   ```
   model = ingredient2vec.train_ingredient2vec(data, p_vector=8, vector_size=10, freq_threshold=1)
   ```
   `train_ingredient2vec()` return a dictionary of ingredient vector, keyed by ingredient name.
   Convert an ingredient to a cluster
   ```
   ingredient_cluster = ingredient2vec.train_ingredientclusters(model, data, n_cluster)
   ```
   `ingredient_cluster` is a dictionary of cluster number, keyed by ingredient name.

3. Testing:
   use 'testing.cocktailSVMClassifier' to test a given cocktail recipe.
   The recipe need to be imported by `cocktailData`. There are two available
   classifier: binary classifier that uses each ingredient as a binary feature,
   combinational classifier that uses discretized qty + combinations of ingredients
   as features.

   For example, the following code will train a classifier
   ```
   comb_classifier = testing.cocktailSVMClassifier(train_data)
   comb_classifier.train_clf_comb()
   ```

4. Generating new recipe:
   Run `python cluster_mdp.py`. This will generate cocktail recipe to text files using
   mdp trained clustered ingredient with different depth.
   You may want to adjust `PERM_VECTOR`, `VECTOR_SIZE` and `N_CLUSTER` for different results.

