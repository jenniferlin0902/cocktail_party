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

