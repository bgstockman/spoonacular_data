import requests
import json
from sqlalchemy import create_engine

def get_recipes(number=5, token = ""):
    """Calls the 'Get random recipes' endpoint from the Spoonacular API.
    
    Args:
        number (int): specifies how many recipes to get
    
    Returns:
        Dictionary of recipe data"""
    url_prefix = "https://api.spoonacular.com/recipes/random?number="
    request_url = url_prefix + str(number)

    headers = {
        "Content-Type" : "application/json",
        "x-api-key" : token
    }
    r = requests.get(request_url, headers = headers)
    return r.json()


def write_recipes(recipe_dict, filename="recipes.txt", sort=False):
    """Pretty prints a json dictionary to a file"""
    with open(filename, "w") as write_file:
        json.dump(recipe_dict, write_file, indent=4, sort_keys=sort)


def read_dict(filename):
    """Reads a json file and returns the parsed json data
    
    Args: 
        filename (str): specifies the file to read

    Returns:
        JSON data from the file (list or dict)
    
    """
    with open(filename, "r") as read_file:
        data = json.load(read_file)
        return data


def get_recipe_ids(recipe_dict):
    """Reads a recipe dict and returns a dict of the IDs and names
    
    Args:
        recipe_dict (dict): dict of recipe info

    Returns:
        dict of recipe Ids and names (ID: name)
    """
    ID_dict = {}
    for recipe in recipe_dict["recipes"]:
        ID_dict[recipe["id"]] = recipe["title"]
    return ID_dict


def get_unique_ids(new_dict, old_dict):
    """Compares two dicts and returns a dict of the items unique to the new list

    Args:
        new_dict (dict): the new recipe dict to check
        old_dict (dict): the old dict to check against
    
    Returns:
        dict of recipe Ids and names
    """
    keys1 = list(new_dict.keys())
    keys2 = list(old_dict.keys())
    unique_ids = [x for x in keys1 + keys2 if x in keys1 and x not in keys2]
    unique_dict = {x : new_dict[x] for x in unique_ids} 
    return unique_dict


def get_df_dict(dict_list,keys):
    """Takes a list of dicts with the same keys and returns a dict in the 
    format {key : [key values]} for each dict in the list 
    
    Args:
        dict_list (list): a list of dicts
        keys (list): list of keys to include from the listed dicts

    Returns:
        dict (dict): a subet of the original dict
    """
    df_dict = {}
    for key in keys:
        data_list = []
        for dict in dict_list:
            data_list.append(dict[key])
        df_dict[key] = data_list
    return df_dict


def drop_existing_rows(df, column, list):
    """ Compares the values in a specified column of a dataframe, against the values
    in a given list. Drops rows from the dataframe whose column values
    already exist in the list.

    Args:
        df (DataFrame): the DataFrame to operate on
        column (str): the name of the DataFrame column to check
        list (list): list of values to compare against
    """ 
    index_list = []
    for index in df.index:
        if df[column][index] in list:
            index_list.append(index)
    new_df = df.drop(index_list)
    return new_df


def list_to_file(filename, list):
    """Appends the items of a list to the given file
    
    """
    with open(filename, "a") as file:
        for item in list:
            file.write(str(item)+"\n")


def file_to_list(filename):
    """Reads each line of a file into a list of integers and returns the list
    
    """
    with open(filename, "r") as file:
        list = []
        for line in file:
            list.append(int(line))
    return list

