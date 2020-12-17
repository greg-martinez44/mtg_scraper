import os
import sqlite3
import time

from src import models as m
from src.sqldb import SQLDatabase

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    updater = m.Updater()
    updater.update_events(URL)
    updater.update_decks_and_players()
    updater.update_deck_lists()

if __name__ == "__main__":
    main()
