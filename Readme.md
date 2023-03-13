# spoonacular_data

## Overview

The purpose of this project is to gather recipe data from Spoonacular.com.  Spoonacular is a project that gathers and catalogues online recipes. Their collected data is made available on their website, and can also be accessed through their API. They offer API access at several different tier levels, including a free tier that allows for the fetching up several hundred recipes per day. More information can be found on the Spoonacular site [here](https://spoonacular.com/food-api).

This project uses the Get Random Recipes endpoint, which allows for fetching up to 100 random recipes per call. The recipe data is returned as a JSON object, which is then run through some cleaning steps to organize the data into pandas dataframes, which are then exported to Postgres. Part of the processing checks the recipes that were fetched and removes any that have already been added to the database.

The extracted recipe data can then be organized and displayed in dashboards, such as these ones available on [Tableau Public](https://public.tableau.com/app/profile/brian.g.stockman/viz/TopRecipes/TopperCategory).


## Dependencies

- Python (>= 3.10)
- Python modules:
    - OS
    - Pandas
    - SQLalchemy
    - hashable_df
    - time
    - datetime
    - requests
- Postgres (or similar database)


## Usage

### spoon.py

This module contains functions that are used in the main.py script in this project. This include a functon to call the "Get Random Recipes" endpoint from the Spoonacular API, and functions to clean and organize the returned data.

### postgresToCsv.py

This script connects to a database that has tables "recipes", "ingredients", and "recipe-ingredients" and extracts all data from those tables into pandas dataframes. It then writes that data to csv files.

This requires access to a database as described above, with the connection string to that database stored in the environmental variable 'CONN_STRING'.

### main.py

This script gets 100 random recipes from spoonacular, parses the data and exports it to a database that has tables "recipes", "ingredients", and "recipe-ingredients". It is set to loop 30 times since that will pull the maximum amount of daily recipe data that is allowed by the free tier of the Spoonacular API.

This requires access to a database as described above, with the connection string to that database stored in the environmental variable 'CONN_STRING'.
