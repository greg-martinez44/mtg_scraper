"""
Methods for interacting with SQL database
"""

import os
import sqlite3
import pandas as pd


def query(table):
    """Returns a dataframe with data in a sql table"""
    with SQLDatabase() as sql_database:
        return sql_database.get_dataframe_from(table)


def commit(data, table):
    """Adds data to a sql table"""
    with SQLDatabase() as sql_db:
        sql_db.union_events(data, table)


class SQLDatabase:
    """API for interacting with SQL database."""

    def __init__(self, db_name=None):
        """Establishes connection to the sql table"""
        if db_name is None:
            _path_to_db = os.path.abspath("dbs/links.db")
        else:
            _path_to_db = db_name
        try:
            self._connection = sqlite3.connect(_path_to_db)
            self._cursor = self._connection.cursor()
        except:
            raise ValueError("Bad Connection")

    def __enter__(self):
        """Method for entering SQLDatabase object as context manager"""
        return self

    def __exit__(self, *args):
        """Method for closing the SQL connection as context manager"""
        self.close()

    def close(self):
        """Closes the SQL connection"""
        self._connection.close()

    def union_events(self, data, table):
        """Adds items to a table"""
        for item in data:
            self.add_new(item, table)
        self._connection.commit()

    def add_new(self, item, table):
        """Factory for building correct sql calls to the appropriate table"""
        if table == "event":
            self.add_events(item)

        if table == "pilot":
            self.add_pilots(item)

        if table == "deck":
            self.add_decks(item)

        if table == "decklist":
            self.add_deck_lists(item)

        if table == "card":
            self.add_cards(item)

    def add_events(self, item):
        """Adds events to the events table"""
        try:
            self._cursor.execute(
                """
                INSERT INTO event (name, link, date)
                VALUES (?, ?, ?)
                """, item
                )
        except sqlite3.IntegrityError:
            pass

    def add_pilots(self, item):
        """
        Add pilots to the sql table.
        If only one name is provided (e.g. an Arena username), add a second element ot
        the list to match lastName.
        """
        if len(item) == 1:
            item += [""]
        try:
            self._cursor.execute(
                """
                INSERT INTO pilot (firstName, lastName)
                VALUES (?, ?)
                """, item
                )
        except sqlite3.IntegrityError:
            pass

    def add_decks(self, item):
        """Adds decks to the deck table"""
        event_id = self.get_event_id(item[0])
        pilot_id = self.get_pilot_id(item[1])
        items_to_insert = item[2:]
        try:
            self._cursor.execute(
                """
                INSERT INTO deck (eventId, pilotId, deckUrl, name, rank)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_id, pilot_id) + items_to_insert
                )
        except sqlite3.IntegrityError:
            pass

    def get_event_id(self, link):
        """
        Returns event ids from event table.
        Used to get foreign key for deck table.
        """
        return self._cursor.execute(
            """
            SELECT id
            FROM event
            WHERE link = ?
            """, (link,)
            ).fetchone()[0]

    def get_pilot_id(self, name):
        """
        Returns pilot ids from pilot table.
        Used to get foreign key for deck table.
        """
        first_last = "".join(name.split(maxsplit=1))
        return self._cursor.execute(
            """
            SELECT id
            FROM pilot
            WHERE (firstName || lastName) = ?
            """, (first_last,)
            ).fetchone()[0]

    def add_deck_lists(self, item):
        """Adds deck lists to the deck list table"""
        try:
            self._cursor.execute(
                """
                INSERT INTO deckList (cardId, deckId, count, slot, cardName)
                VALUES (?, ?, ?, ?, ?)
                """, item
                )
        except sqlite3.IntegrityError:
            pass

    def add_cards(self, item):
        """Adds cards to the cards table."""
        try:
            self._cursor.execute(
                """
                INSERT INTO card (
                    setNumber,
                    setName,
                    name,
                    cmc,
                    color,
                    standardLegality,
                    oracle_text,
                    mana_cost,
                    image_uri
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, item
                )
        except sqlite3.IntegrityError:
            pass

    def get_dataframe_from(self, table):
        """Grabs all the data from a table and returns a dataframe"""
        result = pd.read_sql(f"SELECT * FROM {table}", self._connection)
        if "date" in result.columns.tolist():
            result["date"] = pd.to_datetime(result["date"], dayfirst=True)
        return result


if __name__ == "__main__":
    print(os.path.abspath("dbs/links.db"))
