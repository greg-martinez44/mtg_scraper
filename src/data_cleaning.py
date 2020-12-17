import pandas as pd
from src.sqldb import SQLDatabase

with SQLDatabase() as sql_db:
    event_table = sql_db.get_dataframe_from("event")
    deck_table = sql_db.get_dataframe_from("deck")
    deck_list_table = sql_db.get_dataframe_from(;)
