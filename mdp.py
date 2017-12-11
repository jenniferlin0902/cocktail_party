# -*- coding: utf-8 -*-
"""
Implements ingredient-base Markov chain for cocktail recipe generator

@author: Suzannah
"""
import copy
import numpy as np
import trainerUtil
import collections
import random

np.random.seed(0)

startChar = 'RECIPE_START'
endChar = 'RECIPE_END'
recipeData = trainerUtil.cocktailData('cocktail_train.txt')

# Function: Weighted Random Choice (from CS221 Homework 7 Util)
# --------------------------------
# Given a dictionary of the form element -> weight, selects an element
# randomly based on distribution proportional to the weights. Weights can sum
# up to be more than 1. 
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(weightDict[elem])
        elems.append(elem)
    total = sum(weights)
    key = random.uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    raise Exception('Should not reach here')
    
def trainMDP(data, depth):
    # Probabilities of transition from an ingredient history to the next ingredient
    transprobs = {}
    # Probability that a given ingredient will have the given units
    unitprobs = {}
    # Probability that a recipe will have a given length
    lenprobs = collections.defaultdict(float)
    # All ingredients
    ingredients = data.get_ingredient_list()
    # Create starting key: a tuple of start characters
    startKey = []
    for j in range (0, depth):
        startKey.append(startChar)
    startKey = tuple(startKey)
    #transprobs[startChar] = collections.defaultdict(float)
    for ingredient in ingredients:
        #transprobs[ingredient] = collections.defaultdict(float)
        unitprobs[ingredient] = collections.defaultdict(float)
    for i in range(0, data.n_recipe):
        length = 0
        prevIngredients = startKey
        for ingredient, (amt, unit) in data.raw_data[i].iteritems():
            # Add this ingredient history to the dictionary
            if prevIngredients not in transprobs.keys():
                transprobs[prevIngredients] = collections.defaultdict(float)
            # Increase probability of this ingredient sequence/these units
            transprobs[prevIngredients][ingredient] += 1
            unitprobs[ingredient][(amt, unit)] += 1
            # Add this ingredient to the ingredient history
            prevIngredients = list(prevIngredients)
            prevIngredients.append(ingredient)
            # Forget the oldest ingredient
            prevIngredients.pop(0)
            prevIngredients = tuple(prevIngredients)
            length += 1
        # Add this ingredient history to the dictionary
        if prevIngredients not in transprobs.keys():
            transprobs[prevIngredients] = collections.defaultdict(float)
        # Add to probability that the recipe ends after this ingredient
        transprobs[prevIngredients][endChar] += 1
        # Add to probability that a randomly generated recipe has the same
        # length as this one
        lenprobs[length] += 1
    return transprobs, unitprobs, lenprobs

def bucketTrain(data, depth):
    # Probabilities of transition from an ingredient history to the next ingredient
    transprobs = {}
    # Probability that a recipe will have a given length
    lenprobs = collections.defaultdict(float)
    # Create starting key: a tuple of start characters
    startKey = []
    for j in range (0, depth):
        startKey.append(startChar)
    startKey = tuple(startKey)
    #transprobs[startChar] = collections.defaultdict(float)
    recipes, bucket_conversion = data.get_recipe_bucketed()
    for recipe in recipes:
        length = 0
        prevIngredients = startKey
        for ingredient in recipe.keys():
            # Add this ingredient history to the dictionary
            if prevIngredients not in transprobs.keys():
                transprobs[prevIngredients] = collections.defaultdict(float)
            # Increase probability of this ingredient sequence/these units
            transprobs[prevIngredients][(ingredient, recipe[ingredient])] += 1
            # Add this ingredient to the ingredient history
            prevIngredients = list(prevIngredients)
            prevIngredients.append((ingredient, recipe[ingredient]))
            # Forget the oldest ingredient
            prevIngredients.pop(0)
            prevIngredients = tuple(prevIngredients)
            length += 1
        # Add this ingredient history to the dictionary
        if prevIngredients not in transprobs.keys():
            transprobs[prevIngredients] = collections.defaultdict(float)
        # Add to probability that the recipe ends after this ingredient
        transprobs[prevIngredients][(endChar,0)] += 1
        # Add to probability that a randomly generated recipe has the same
        # length as this one
        lenprobs[length] += 1
    return transprobs, bucket_conversion, lenprobs

def mdpGenerate(data, depth, outputFile, numOutputs):
    transprobs, unitprobs, lenprobs = trainMDP(data, depth)
    f = open(outputFile, 'w')
    # Create starting key: a tuple of <depth> start characters
    startKey = []
    for j in range (0, depth):
        startKey.append(startChar)
    startKey = tuple(startKey)
    for i in range(0, numOutputs): 
        outputStr = 'TITLE: '
        currentIngredients = startKey
        maxlength = weightedRandomChoice(lenprobs)
        length = 0.0
        nextRecipe = False
        while not nextRecipe:
            nextIngredient = weightedRandomChoice(transprobs[currentIngredients])
            if nextIngredient == endChar or length == maxlength:
                nextRecipe = True
            else:
                nextAmt, nextUnit = weightedRandomChoice(unitprobs[nextIngredient])
                outputStr = outputStr + ' ' + str(nextAmt) + ' ' + nextUnit + ' ' + nextIngredient + ';'
                # Add this ingredient to the ingredient history
                currentIngredients = list(currentIngredients)
                currentIngredients.append(nextIngredient)
                # Forget the oldest ingredient
                currentIngredients.pop(0)
                currentIngredients = tuple(currentIngredients)
                length += 1
        f.write(outputStr + '\n')
    f.close()

def bucketMDP(data, depth, outputFile, numOutputs):
    transprobs, bucket_conversion, lenprobs = bucketTrain(data, depth)
    print "Bucket data trained"
    f = open(outputFile, 'w')
    # All ingredients
    ingredients = data.get_ingredient_list()
    # Create starting key: a tuple of <depth> start characters
    startKey = []
    for j in range (0, depth):
        startKey.append(startChar)
    startKey = tuple(startKey)
    for _ in range(0, numOutputs): 
        outputStr = 'TITLE: '
        currentIngredients = startKey
        maxlength = weightedRandomChoice(lenprobs)
        length = 0.0
        nextRecipe = False
        while not nextRecipe:
            nextIngredient, nextBucket = weightedRandomChoice(transprobs[currentIngredients])
            if nextIngredient == endChar or length == maxlength:
                nextRecipe = True
            else:
                ingredient = ingredients[nextIngredient]
                qty, unit = random.choice(bucket_conversion[ingredient][nextBucket])
                outputStr = outputStr + ' ' + str(qty) + ' ' + unit + ' ' + ingredient + ';'
                # Add this ingredient to the ingredient history
                currentIngredients = list(currentIngredients)
                currentIngredients.append((nextIngredient, nextBucket))
                # Forget the oldest ingredient
                currentIngredients.pop(0)
                currentIngredients = tuple(currentIngredients)
                length += 1
            print "Recipe generated!"
        f.write(outputStr + '\n')
    f.close()