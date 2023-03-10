import os
import spoon
import pandas as pd
from sqlalchemy import create_engine
from hashable_df import hashable_df
import time
from datetime import datetime


recipe_keys = ["id", "title", "vegetarian", "glutenFree", "dairyFree","lowFodmap","aggregateLikes","pricePerServing","healthScore","sourceName","spoonacularSourceUrl","sourceUrl","readyInMinutes", "extendedIngredients"]
ingredient_keys = ["id","nameClean","aisle"]

## Read conn string and API token from environmental variables
# API key for my Spoonacular API
TOKEN = os.environ.get('API_KEY')
# connection string for a local Postgres database
conn_string = os.environ.get('CONN_STRING')

## API limits to 100 random recipes per call,
## can make 30 such calls per day on free tier
counter = 0
if __name__ == "__main__":
    while(counter < 5):
        counter += 1
        time.sleep(1)
        ### pull data from API
        recipe_dict = spoon.get_recipes(100, token=TOKEN)

        # for recipes, create a dict that can be converted to a dataframe
        # be sure to use recipe_dict["recipes"], to specify the list of dicts
        # and not the main dict that is returned from the API call
        recipe_df_dict = spoon.get_df_dict(recipe_dict["recipes"], recipe_keys)

        # create dataframe dict from the ingredients list of sub-dict
        # this will not relate ingredients to recipe, but will just keep a separate table of all ingredients
        ingredient_df_dict = dict.fromkeys(ingredient_keys)
        for ingredient_dict_list in recipe_df_dict["extendedIngredients"]:
            temp_dict = spoon.get_df_dict(ingredient_dict_list, ingredient_keys)
            for key in temp_dict.keys():
                    for x in temp_dict[key]:
                        if ingredient_df_dict[key] == None:
                            ingredient_df_dict[key] = [x]
                        else:
                            ingredient_df_dict[key].append(x)

        #  create a df dict for the recipe-ingredient table
        # this table will track which ingredients each recipe has
        recipeingredient_df_dict = {"recipeID": [], "ingredientID": []}
        for recipe in recipe_dict["recipes"]:
            for ingredient_dict in recipe["extendedIngredients"]:
                recipeingredient_df_dict["recipeID"].append(recipe["id"])
                recipeingredient_df_dict["ingredientID"].append(ingredient_dict["id"])

        # create dataframes from dicts
        recipe_df = pd.DataFrame(recipe_df_dict, columns=recipe_keys)
        ingredient_df = pd.DataFrame(ingredient_df_dict, columns=ingredient_keys)
        recipeingredient_df = pd.DataFrame(recipeingredient_df_dict,columns=recipeingredient_df_dict.keys())
        
        ### Clean and organize the data
        # rename id columns to recipeID and ingredientID
        recipe_df = recipe_df.rename(columns={"id": "recipeID"})
        ingredient_df = ingredient_df.rename(columns={"id": "ingredientID"})

        # remove duplicates from DFs
        # need to use hashable_df 
        # else drop_duplicates() won't work on a df that contains a dict
        recipe_df = hashable_df(recipe_df).drop_duplicates()
        ingredient_df = hashable_df(ingredient_df).drop_duplicates()
        recipeingredient_df = hashable_df(recipeingredient_df).drop_duplicates()

        # drop the extendedIngredients column from recipe_df
        recipe_df = recipe_df.drop(columns="extendedIngredients")

        ## check IDs against lists
        # get list of IDs from the current recipe set
        recipeIDs_list = recipe_df["recipeID"].values.tolist()
        # get the master list of IDs that have already been imported
        recipeIDs_master = spoon.file_to_list("recipeIDsmaster.txt")
        # update recipe_df to only keep rows with new recipe IDs
        recipe_df = spoon.drop_existing_rows(recipe_df, "recipeID", recipeIDs_master)
        # for recipe-ingredients just need to compare recipeIDs to master
        recipeingredient_df = spoon.drop_existing_rows(recipeingredient_df, "recipeID", recipeIDs_master)
        # get a list of the new recipe IDs
        new_recipe_IDs = recipe_df["recipeID"].values.tolist()
        # append the new recipeIDs to the list
        spoon.list_to_file("recipeIDsmaster.txt", new_recipe_IDs)

        # same process as above for ingredient_df
        ingredientIDs_list = ingredient_df["ingredientID"].values.tolist()
        ingredientIDs_master = spoon.file_to_list("ingredientIDsmaster.txt")
        ingredient_df = spoon.drop_existing_rows(ingredient_df, "ingredientID", ingredientIDs_master)
        new_ingredient_IDs = ingredient_df["ingredientID"].values.tolist()
        spoon.list_to_file("ingredientIDsmaster.txt", new_ingredient_IDs)
        
        ### Load to database

        # create a connection to the postgres db
        conn = create_engine(conn_string, echo=True)
        # insert the recipe data into postgres
        recipe_df.to_sql("recipes", con=conn, if_exists="append", index=False)
        ingredient_df.to_sql("ingredients", con=conn, if_exists="append", index=False)
        recipeingredient_df.to_sql("recipeingredients", con=conn, if_exists="append", index=False)
        ### write to log file 
        new_recipe_count = len(new_recipe_IDs)
        with open("spoon_logs.txt", "a") as write_file:
            print(f"{datetime.now()}: {new_recipe_count} recipes added.\n", file=write_file)