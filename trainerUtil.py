# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 13:17:38 2017

Utilities for use in developing cocktail recipe generator

@author: Suzannah
"""
import re
import random
import os
import numpy as np

TOTAL_DATA_SIZE = 5568
bucket_threshold = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]

def qty2bucket(qty):
    for i, threshold in enumerate(bucket_threshold):
        if qty < threshold:
            return i + 1
    return len(bucket_threshold) + 1

def retrieveData(inputFile, useTitles = 0, simplifyIngredients = 1, removeBranding = 1):
    """
    Reads a text file and identifies ingredients, quantities, and titles. Gives
    options to remove branding (e.g., read only Bourbon, not Bulleit Bourbon),
    remove recipe title, and remove quantity.
    """
    print "Importing data from {}".format(inputFile)
    # List of all recipes to be returned at the end
    recipes = []
    f = open(inputFile, 'r')
    lines = f.readlines()
    f.close()
    for i, line in enumerate(lines):
        # Remove items between parentheses to simplify tokenization
        if simplifyIngredients == 1:
            line = re.sub("([\(\[]).*?([\)\]])", "", line)
        # Dictionary defining just this recipe
        recipe = {}
        colonseparation = line.split(':')
        title = colonseparation[0]
        colonseparation.pop(0)
        text = ':'.join(colonseparation)
        if useTitles == 1:
            recipe['TITLE'] = title
        # Recipes are scraped with semicolons separating ingredients
        ingredients = text.split(';')
        for j in range(0,len(ingredients)):
            # The list may shrink as it's corrected. This ensures we don't 
            # overrun the list length.
            if j > len(ingredients) - 1: break
            # Some semicolons appear inside parentheses and are intended as
            # part of the ingredient. Join accidentally separated ingredients.
            if ('(' in ingredients[j]) and (')' not in ingredients[j]):
                ingredients[j] = ingredients[j] + ';' + ingredients[j+1]
                ingredients.pop(j+1)
        # Trim the newline character
        ingredients.pop(len(ingredients)-1)
        for ingredient in ingredients:
            if removeBranding == 1:
                branding = ingredient.split(',')
                if '(' in branding[0] and ')' not in branding[0]:
                    ingredient = ','.join(branding)
                else:
                    ingredient = branding[0]
            ingredientwords = ingredient.split(' ')
            if ("" in ingredientwords) or (" " in ingredientwords):
                ingredientwords = [x for x in ingredientwords if (x != "") and x != " "]
            try:
                amt = float(ingredientwords[0])
                ingredientwords.pop(0)
            except ValueError:
                amt = 1

            key = ' '.join(ingredientwords[1:]).lower().rstrip().lstrip()
            recipe[key] = (amt, ingredientwords[0])# ingredient : (amt, unit)
        recipes.append(recipe)
    return recipes

def split_data():
    '''
    helper function to split up recipe text file
    '''
    n_classifier = 500
    all = range(TOTAL_DATA_SIZE)
    random.shuffle(all)
    classifier = all[:n_classifier]
    count = 0
    test_out = open("cocktail_test.txt", "w")
    train_out = open("cocktail_train.txt", "w")

    with open("cocktail_all.txt") as f:
        for line in f:
            if count in classifier:
                test_out.write(line)
            else:
                train_out.write(line)
            count += 1


def vector_to_recipe(vector, ingredient_list):
    '''
    helper function to convert an ingredient vector to a list of ingredient
    '''
    recipe = []
    for i, a in enumerate(vector):
        if a > 0:
            recipe.append(ingredient_list[i])
    return recipe


class cocktailData:
    '''
    cocktail recipe data class

    @param
    self.n_recipe - number of recipes
    self.raw_data - list of recipe dictionary [{ingredient name:(unit, qty)}]
    self.n_ingredient - total number of distinct ingredient
    self.ingredients - {ingredient: (frequency, set(unit)}
    self.recipes - list of recipe ingredient vector
    '''
    def __init__(self, file, ingredients=None):
        FREQ_THRESHOLD = 5
        self.big_unit = ["q", "pt", "gal"]
        self.small_unit = ["ds", "twst", "pn", "twst", "lf",
                      "spg", "dr", "rinse", "cube", "wdg", "sli", "spl",
                      "\xc2\xa0", "sh"]
        self.oz_conversion = {"t": 0.5, "bsp": 1 / float(12), "T": 0.5, "pt": 16, "c": 8, "jig": 1.5, "q": 32, "gal": 128,
                         "gl": 128}
        if not os.path.exists(file):
            print "ERROR: training data file {} does not exist".format(file)
            self.raw_data = None
        else:
            raw_data = retrieveData(file, useTitles = 0, simplifyIngredients = 1, removeBranding = 1)
            if ingredients == None:
                self.ingredients = generate_ingredient_dict(file, FREQ_THRESHOLD)
            else:
                self.ingredients = ingredients
            
            self.n_ingredient = len(self.ingredients.keys())
            self.recipes = []
            print "converting recipe to {} ingredients".format(self.n_ingredient)
            err = 0
            self.raw_data = []
            for recipe in raw_data:
                recipe_vector = [0] * self.n_ingredient
                remove = False
                for l in recipe:
                    try:
                        recipe_vector[self.ingredients.keys().index(l)] = 1
                    except:
                        err += 1
                        #print "found rare ingredient {}, remove recipe!".format(err, l)
                        remove = True
                        break
                if not remove:
                    self.recipes.append((recipe_vector, 1))
                    self.raw_data.append(recipe)

            self.n_recipe = len(self.recipes)

    def get_ingredient_list(self):
        # return a copy in case someone modify this
        return list(self.ingredients.keys())

    def get_recipe_raw(self, id):
        return self.raw_data[id]

    def get_recipes_ingredient_only(self):
        result = []
        for recipe in self.raw_data:
            result.append(recipe.keys())
        return result

    def get_recipes_binary(self):
        return list(self.recipes)

    def get_recipes_binary_x(self):
        return list([r[0] for r in self.recipes])

    def generate_fake(self, n, binary=True):
        num_ingredients = [3,4,5,6]
        fakes = []
        buckets = range(1, len(bucket_threshold)+2)
        for _ in range(n):
            n_ingredient = random.choice(num_ingredients)
            recipe_vector = [0] * self.n_ingredient
            for i in range(n_ingredient):
                if binary:
                    recipe_vector[random.choice(range(self.n_ingredient))] = 1
                else:
                    recipe_vector[random.choice(range(self.n_ingredient))] = random.choice(buckets)
            fakes.append(recipe_vector)
        return fakes

    def get_recipe_bucketed(self):
        bucketed_recipes = []
        ingredient_list = self.get_ingredient_list()
        for r in self.raw_data:
            normalize = 1
            bucketed_recipe = {}
            for i, ingredient in enumerate(r):
                qty, unit = r[ingredient]
                if unit in self.big_unit:
                    normalize = self.oz_conversion[unit] / 1.5  # assume 1.5 oz for standard drink
                if unit == "oz" or unit in self.oz_conversion:
                    # convert to oz
                    if unit != "oz":
                        qty = qty * self.oz_conversion[unit] / normalize
                    else:
                        qty = qty / normalize
                    bucket = qty2bucket(qty)
                elif unit in self.small_unit:
                    bucket = 1
                bucketed_recipe[ingredient_list.index(ingredient)] = bucket
            bucketed_recipes.append(bucketed_recipe)
        return bucketed_recipes

    def get_ingredient_unit(self, ingredient):
        return self.ingredients[ingredient][1]

def generate_ingredient_dict(file, thereshold):
    FREQ_THRESHOLD = 5
    if not os.path.exists(file):
        print "ERROR: training data file {} does not exist".format(file)
        raw_data = None
    else:
        raw_data = retrieveData(file, simplifyIngredients=1, removeBranding=1)
        # fist, parse ingredients
        temp_ingredients = {}
        for recipe in raw_data:
            for k, v in recipe.iteritems():
                if k not in temp_ingredients:
                    temp_ingredients[k] = [0, set()] #(count, unit list)
                        # otherwise, increment count, and keep track of unit
                temp_ingredients[k][0] += 1
                temp_ingredients[k][1].add(v)
                # remove stuff that is under thereshold
        ingredients = {}
        for ingredient in temp_ingredients:
            if temp_ingredients[ingredient][0] >= FREQ_THRESHOLD:
                ingredients[ingredient] = temp_ingredients[ingredient]
        print "Got {} ingredient".format(len(ingredients))
        return ingredients
            # or import from a trained data set
       
