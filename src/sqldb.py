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
            print("Start of 'player' clause")
            if len(item) == 1:
                item += [""]
            try:
                print("try to insert: ", item)
                self._cursor.execute(
                    """
                    INSERT INTO pilot (firstName, lastName)
                    values (?, ?)
                    """, item
                )
            except sqlite3.IntegrityError:
                print("Integrity Error raised")
                pass
        elif table == "deck":
            for thing in item:
                query = """
                INSERT INTO deck (eventId, pilotId, url, name, rank)
                values (?, ?, ?, ?, ?)
                """
                event_id = self._cursor.execute("""
                    SELECT id
                    FROM event
                    WHERE link = ?
                    """, thing[0])
                pilot_id = self._cursor.execute("""
                    SELECT id
                    FROM pilot
                    WHERE (firstName || lastName) = ?
                    """, "".join(thing[1].split()))
                try:
                    self._cursor.execute(query, [event_id, pilot_id] + thing)
                except sqlite3.IntegrityError:
                    pass
        elif table == "decklist":
            pass
        elif table == "card":
            pass

    def get_dataframe_from(self, table):
        query = f"SELECT * FROM {table}"
        return pd.read_sql(query, self._connection)

if __name__ == "__main__":
    print(os.path.abspath("dbs/links.db"))
