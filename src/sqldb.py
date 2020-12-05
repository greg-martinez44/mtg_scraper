import os
import pandas as pd
import sqlite3


class SQLDatabase:
    """API for interacting with SQL database."""

    def __init__(self, db_name=None):
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
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self._connection.close()

    def union_events(self, data, table):
        for item in data:
            self.add_new(item, table)
        self._connection.commit()

    def add_new(self, item, table):
        if table == "event":
            try:
                self._cursor.execute(
                    """
                    INSERT INTO event (name, link, date)
                    VALUES (?, ?, ?)
                    """, item
                )
            except sqlite3.IntegrityError:
                pass

        elif table == "pilot":
            if len(item) == 1:
                item += [""]
            try:
                self._cursor.execute(
                    """
                    INSERT INTO pilot (firstName, lastName)
                    values (?, ?)
                    """, item
                )
            except sqlite3.IntegrityError:
                pass

        elif table == "deck":
            query = """
            INSERT INTO deck (eventId, pilotId, deckUrl, name, rank)
            VALUES (?, ?, ?, ?, ?)
            """
            event_id = self._cursor.execute("""
                SELECT id
                FROM event
                WHERE link = ?
                """, (item[0], )
            ).fetchone()[0]
            pilot_id = self._cursor.execute("""
                SELECT id
                FROM pilot
                WHERE (firstName || lastName) = ?
                """, ("".join(item[1].split(maxsplit=1)),)
            ).fetchone()[0]
            items_to_insert = item[2:]
            try:
                self._cursor.execute(
                    query, (event_id, pilot_id) + items_to_insert)
            except sqlite3.IntegrityError:
                pass

        elif table == "decklist":
            query = """
            INSERT INTO deckList (cardId, deckId, count, slot)
            VALUES (?, ?, ?, ?)
            """
            try:
                self._cursor.execute(query, item)
            except sqlite3.IntegrityError:
                pass

        elif table == "card":
            query = """
            INSERT INTO card (setNumber, setName, name, cmc, color, standardLegality, oracle_text, mana_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            try:
                self._cursor.execute(query, item)
            except sqlite3.IntegrityError:
                pass

    def get_dataframe_from(self, table):
        query = f"SELECT * FROM {table}"
        result = pd.read_sql(query, self._connection)
        if "date" in result.columns.tolist():
            result["date"] = pd.to_datetime(result["date"], dayfirst=True)
        return result


if __name__ == "__main__":
    print(os.path.abspath("dbs/links.db"))
