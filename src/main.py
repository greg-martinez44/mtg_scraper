import os
import sqlite3
import time

from src import models as m
from src.sqldb import SQLDatabase

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    event_table = m.scrape_data_from(URL)
    deck_data = m.scrape_event_data()
    save(
        {
            "event": event_table,
            "pilot": parse_pilots_from(deck_data),
            # "deck": deck_data
        }
    )

def save(data):
    with SQLDatabase() as sql_db:
        for table in data:
            sql_db.union_events(data[table], table)

def parse_pilots_from(deck_data):
    print("Parsing deck data...")
    player_table = []
    for item in deck_data:
        player_table.append(item[1].split(maxsplit=1))
    print("returning player_table: ", player_table)
    return player_table

if __name__ == "__main__":
    main()
