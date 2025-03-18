import os
import sqlite3
import time

from src import models as m

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    m.update_events(URL)
    m.update_decks_and_players()
    m.update_deck_lists()

if __name__ == "__main__":
    main()
