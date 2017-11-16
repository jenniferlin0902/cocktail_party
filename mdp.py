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
    
def trainData(data):
    transprobs = {}
    unitprobs = {}
    lenprobs = collections.defaultdict(float)
    ingredients = data.get_ingredient_list()
    transprobs[startChar] = collections.defaultdict(float)
    for ingredient in ingredients:
        transprobs[ingredient] = collections.defaultdict(float)
        unitprobs[ingredient] = collections.defaultdict(float)
    for i in range(0, data.n_recipe):
        length = 0
        prevIngredient = startChar
        for ingredient, (amt, unit) in data.raw_data[i].iteritems():
            transprobs[prevIngredient][ingredient] += 1
            unitprobs[ingredient][(amt, unit)] += 1
            prevIngredient = ingredient
            length += 1
        transprobs[prevIngredient][endChar] += 1
        lenprobs[length] += 1
    return transprobs, unitprobs, lenprobs

def generateData(data):
    transprobs, unitprobs, lenprobs = trainData(data)
    maxlength = weightedRandomChoice(lenprobs)
    ingredient = startChar
    length = 0.0
    outputStr = ''
    while True:
        nextIngredient = weightedRandomChoice(transprobs[ingredient])
        if nextIngredient == endChar or length == maxlength:
            return outputStr
        else:
            nextAmt, nextUnit = weightedRandomChoice(unitprobs[nextIngredient])
            outputStr = outputStr + ' ' + str(nextAmt) + ' ' + nextUnit + ' ' + nextIngredient + ';'
            length += 1.0