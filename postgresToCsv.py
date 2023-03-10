## run a query "select * from recipes" on postgres server
## bring that data into a dataframe then write to csv
import os
import pandas as pd
import sqlalchemy

conn_string = os.environ.get('CONN_STRING')

engine = sqlalchemy.create_engine(conn_string, echo=True)
conn = engine.connect()

recipes_query = sqlalchemy.text("""select * from recipes;""")
ingredients_query = sqlalchemy.text("""select * from ingredients;""")
ri_query = sqlalchemy.text("""select * from recipeingredients;""")

recipes_df = pd.read_sql_query(recipes_query, conn)
ingredients_df = pd.read_sql_query(ingredients_query, conn)
ri_df = pd.read_sql_query(ri_query, conn)

recipes_df.to_csv("postgres_recipes.csv")
ingredients_df.to_csv("postgres_ingredients.csv")
ri_df.to_csv("postgres_recipeingredients.csv")