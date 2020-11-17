import csv
import os
import sqlite3
import time

from src import models as m

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    result = m.scrape_data_from(URL)
    save(result)

def save(data):
    union_events("links.db", data, "event")

def union_events(db, data, table):
    conn = sqlite3.connect(os.path.abspath("dbs/links.db"))
    cursor = conn.cursor()

    for event in data:
        add_new(cursor, table, event)
    conn.commit()
    conn.close()

def add_new(cursor, table, data):
    """New events are added to the sqlite3 table; Unique constraint on event ensures that no repeats are added."""
    if table == "event":
        try:
            cursor.execute(
                """
                INSERT INTO event (name, link, date)
                VALUES (?, ?, ?)
                """, (data)
                )
        except sqlite3.IntegrityError:
            pass
    elif table == "player":
        try:
            cursor.execute(
                """
                INSERT INTO player (firstName, lastName)
                VALUES (?, ?)
                """, data
                )
        except sqlite3.IntegrityError:
            pass
    elif table == "deck":
        pass
    elif table == "decklist":
        pass
    elif table == "card":
        pass


if __name__ == "__main__":
    main()
