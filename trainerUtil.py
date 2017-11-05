# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 13:17:38 2017

Utilities for use in developing cocktail recipe generator

@author: Suzannah
"""
import re

def retrieveData(inputFile, useTitles = 0, simplifyIngredients = 1, removeBranding = 1):
    """
    Reads a text file and identifies ingredients, quantities, and titles. Gives
    options to remove branding (e.g., read only Bourbon, not Bulleit Bourbon),
    remove recipe title, and remove quantity.
    """
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
        for j in range (0,len(ingredients)):
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
            try:
                amt = float(ingredientwords[0])
                ingredientwords.pop(0)
            except ValueError:
                amt = 1
            key = ' '.join(ingredientwords)
            recipe[key] = amt
        recipes.append(recipe)
    return recipes