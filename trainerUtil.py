# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 13:17:38 2017

Utilities for use in developing cocktail recipe generator

@author: Suzannah
"""
import re
import random
import os

TOTAL_DATA_SIZE = 5568

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
    n_classifier = 1000
    all = range(TOTAL_DATA_SIZE)
    random.shuffle(all)
    classifier = all[:n_classifier]
    count = 0
    test_out = open("cocktail_medium_random.txt", "w")
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
        if not os.path.exists(file):
            print "ERROR: training data file {} does not exist".format(file)
            self.raw_data = None
        else:
            self.raw_data = retrieveData(file, simplifyIngredients=1, removeBranding=1)
            # fist, parse ingredients
            if ingredients == None:
                self.ingredients = {}
                for recipe in self.raw_data:
                    for k, v in recipe.iteritems():
                        if k not in self.ingredients:
                            self.ingredients[k] = [0, set([v[1]])] #(count, unit list)
                        else:
                        # otherwise, increment count, and keep track of unit
                            self.ingredients[k][0] += 1
                            self.ingredients[k][1].add(v[1])
            # or import from a trained data set
            else:
                self.ingredients = dict(ingredients)
            self.n_recipe = len(self.raw_data)
            self.n_ingredient = len(self.ingredients.keys())
            self.recipes = []
            err = 0
            for recipe in self.raw_data:
                recipe_vector = [0] * self.n_ingredient
                for l in recipe:
                    try:
                        recipe_vector[self.ingredients.keys().index(l)] = 1
                    except:
                        err += 1
                        print "found weird ingredient {} {}".format(err, l)
                self.recipes.append((recipe_vector, 1))

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

    def generate_fake(self, n):
        num_ingredients = [3,4,5,6]
        fakes = []
        for _ in range(n):
            n_ingredient = random.choice(num_ingredients)
            recipe_vector = [0] * self.n_ingredient
            for i in range(n_ingredient):
                recipe_vector[random.choice(range(self.n_ingredient))] = 1
            fakes.append((recipe_vector, 0))
        return fakes

    def get_ingredient_unit(self, ingredient):
        return self.ingredients[ingredient][2]