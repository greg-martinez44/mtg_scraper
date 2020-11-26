import os
import sqlite3
import time

from src import models as m
from src.sqldb import SQLDatabase

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    result = m.scrape_data_from(URL)
    save(result)

def save(data):
    with SQLDatabase() as sql_db:
        sql_db.union_events(data, "event")



if __name__ == "__main__":
    main()
