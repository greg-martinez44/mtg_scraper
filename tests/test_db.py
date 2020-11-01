import unittest

import os
import sqlite3

DB_FILE = os.path.abspath('dbs/links.db')

def make_dummy_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dummy_table (
        dummy_name TEXT NOT NULL,
        dummy_link TEXT UNIQUE NOT NULL,
        dummy_date DATE NOT NULL
        )
        """
        )

class TestDB_IO(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(DB_FILE)

    def tearDown(self):
        self.conn.close()

    def test_create_table(self):
        cursor = self.conn.cursor()
        make_dummy_table(cursor)
        cursor.execute("DROP TABLE dummy_table")

    def test_insert_data(self):
        cursor = self.conn.cursor()
        make_dummy_table(cursor)
        dummy_vars = ('one name', 'one link', 'this date')
        cursor.execute(
            """
            INSERT INTO dummy_table (dummy_name, dummy_link, dummy_date)
            VALUES (?, ?, ?)
            """, (dummy_vars)
            )

        inserted_name = cursor.execute("SELECT dummy_name FROM dummy_table").fetchone()
        self.assertEqual(inserted_name[0], 'one name')
        cursor.execute("DROP TABLE IF EXISTS dummy_table")
