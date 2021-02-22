"""
Loaded data objects for visuals.
"""

from os.path import join
import pandas as pd

from src.constants import FLAT_FILE_DIR


LANDS = ["Island", "Mountain", "Forest", "Plains", "Swamp"]

full_table = pd.read_csv(join(FLAT_FILE_DIR, "full_table.csv"))
event_table = pd.read_csv(join(FLAT_FILE_DIR, "event_table.csv"))
deck_list_table = pd.read_csv(join(FLAT_FILE_DIR, "deck_list_table.csv"))
pilot_table = pd.read_csv(join(FLAT_FILE_DIR, "pilot_table.csv"))
deck_table = pd.read_csv(join(FLAT_FILE_DIR, "deck_table.csv"))
card_table = pd.read_csv(join(FLAT_FILE_DIR, "card_table.csv"))

illegal_deck_ids = full_table[
    ~full_table["cardId"].isin(
        card_table["standardLegality"] == "legal"]["cardId"]
        )
    ]["deckId"]

first_place_decks = deck_table[
    (deck_table["rank"] == 1)
    & (~deck_table["deckId"].isin(illegal_deck_ids))
    ].copy()

main_decks = full_table[
    (~full_table["name"].isin(LANDS))
    & (full_table["slot"] == "md")
    & (~fulll_table["deckId"].isin(illegal_deck_ids))
    ].copy()

