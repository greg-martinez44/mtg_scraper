import os
import sqlite3
import time

from src import models as m
from src.sqldb import SQLDatabase

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    event_table = m.scrape_data_from(URL)
    # player
    # deck_data = m.scrape_event_data()
    
    save(
        {
            "event": event_table,
            # "pilot": parse_pilots_from(deck_table),
            # "deck": deck_table
        }
    )

def save(data):
    tables = data.keys()
    with SQLDatabase() as sql_db:
        for table in tables:
            sql_db.union_events(data[table], table)

def parse_pilots_from(deck_data):
    player_table = []
    for item in deck_data:
        player_table.append(item[1].split(maxsplit=1))
    
    return player_table

if __name__ == "__main__":
    main()
