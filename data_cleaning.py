"""
Download and clean known bad data points for MTG standard tournament scene inspection
"""
import pandas as pd

from src.constants import (
    URL,
    ZENDIKAR_RELEASE,
    KALDHEIM_RELEASE,
    ID_NAME_MAP,
    ARCHETYPE_MAP,
    NAME_ARCHETYPE_MAP,
    ID_ARCHETYPE_MAP,
    CATEGORY_MAP,
    ID_CATEGORY_MAP,
    ABU_MAP,
    BROKEN_CODE_MAP,
    RANK_MAP,
    COMPOSITE_RANK_MAP,
    FULL_TABLE_COLUMNS,
    ID_SPEC_MAP
    )
import src.models as m
from src.sqldb import SQLDatabase

def update(url):
    """Update tables from mtgtop8.com"""
    updater = m.Updater()
    updater.update_events(url)
    updater.update_decks_and_players()
    updater.update_deck_lists()

def clean_dates(df, dayfirst=True):
    """Cast date column to datetime objects"""
    df["date"] = pd.to_datetime(df["date"], dayfirst=dayfirst)

def rename_id_column(df, new_id, inplace=True):
    """Fix id column names"""
    df.rename(columns={"id": new_id}, inplace=inplace)

def add_card_id(card_table):
    "Adds a card id (number + name) to the card table"
    card_table["setNumber"] = card_table["setNumber"].str.zfill(3)
    card_table["cardId"] = card_table["setNumber"] + card_table["setName"]

def fix_deck_names(deck_table, id_name_map):
    """Replaces weird deck names with sensical ones."""
    for deck_id, deck_name in id_name_map.items():
        deck_table.loc[deck_table["deckId"] == deck_id, "name"] = deck_name

def set_archetypes(deck_table, archetype_map, **kwargs):
    """Add archetype based on either keywords in the name of the deck, the id, or specifc name."""
    for archetype, flags in archetype_map.items():
        for flag in flags:
            deck_table.loc[
                deck_table["name"].str.contains(flag, case=False),
                "archetype"
            ] = archetype
    if kwargs.get("id_archetype_map", None):
        for deck_id, archetype in kwargs["id_archetype_map"].items():
            deck_table.loc[deck_table["deckId"] == deck_id, "archetype"] = archetype
    if kwargs.get("name_archetype_map", None):
        for deck_name, archetype in kwargs["name_archetype_map"].items():
            deck_table.loc[deck_table["name"] == deck_name, "archetype"] = archetype

def set_categories(deck_table, category_map, **kwargs):
    """Add category based on either keywords in the name of the deck or id."""
    for category, flags in category_map.items():
        for flag in flags:
            deck_table.loc[deck_table["name"].str.contains(flag, case=False), "category"] = category
    if kwargs.get("id_category_map", None):
        for deck_id, category in kwargs["id_category_map"].items():
            deck_table.loc[deck_table["deckId"] == deck_id, "category"] = category

def fix_abu_codes(table, abu_map, inplace=True):
    """Fixes 'abu' codes in mtgtop8's HTML code."""
    table["cardId"].replace(to_replace=abu_map, inplace=inplace)

def fix_broken_codes(table, broken_code_map, inplace=True):
    """Some card codes in mtgtop8's HTML are from old sets; this fixes them to be more recent"""
    table["cardId"].replace(to_replace=broken_code_map, inplace=inplace)

def set_latest_release(table):
    """Adds a label column for which set was most recently released at the time of the event."""
    table.loc[table["date"] < ZENDIKAR_RELEASE, "latest_set"] = "Ikoria"
    table.loc[
        (table["date"] >= ZENDIKAR_RELEASE)
        & (table["date"] < KALDHEIM_RELEASE),
        "latest_set"
    ] = "Zendikar Rising"
    table.loc[table["date"] >= KALDHEIM_RELEASE, "latest_set"] = "Kaldheim"

def fix_rankings(table, ranking_map, composite_ranks=None):
    """Replaces point systems with rough approximations of the player's rank."""
    for event_id, rank_conversion in ranking_map.items():
        for pts, rank in rank_conversion:
            table.loc[
                (table["rank"] == pts)
                & (table["eventId"] == event_id),
                "rank"
                ] = rank
    if composite_ranks:
        for place_range, rank in composite_ranks.items():
            table.loc[table["rank"] == place_range, "rank"] = rank

def make_full_table(**kwargs):
    """Merges all tables into one 'full table'"""
    events_and_decks = pd.merge(
        kwargs["event_table"],
        kwargs["deck_table"],
        on="eventId",
        suffixes=["_event", "_deck"]
        ).drop_duplicates()

    events_decks_pilots = pd.merge(
        events_and_decks,
        kwargs["pilot_table"],
        on="pilotId",
        suffixes=[None, "_pilot"]
        ).drop_duplicates()

    events_decks_pilots_deck_list = pd.merge(
        events_decks_pilots,
        kwargs["deck_list_table"],
        on="deckId",
        suffixes=[None, "_decklist"]
        ).drop_duplicates()

    full_table = pd.merge(
        events_decks_pilots_deck_list,
        kwargs["card_table"],
        on="cardId",
        suffixes=[None, "_cards"]
        )

    return (
        full_table[FULL_TABLE_COLUMNS]
        .drop_duplicates()
        .sort_values(by=["eventId", "deckId", "slot"])
        .reset_index(drop=True)
        )

def fix_wrong_names(table, id_specs_map):
    """Spot fixes weird deck names"""
    for card_id, specs in id_specs_map.items():
        table.loc[table["cardId"] == card_id, "name"] = specs[1]
        table.loc[table["cardId"] == card_id, "color"] = specs[2]
        table.loc[table["cardId"] == card_id, "cardId"] = specs[0]

def save_to_disk(**kwargs):
    """Saves all tables to separate csv files"""
    for table in kwargs:
        kwargs[table].to_csv(f"flat_files/{table}.csv", index=False)

def check_missing_archetype(table):
    """
    Reports any decks that did not get assigned an archetype.
    The deckUrl is printed so that the correct archetype can be added through
    either the ID_ARCHETYPE_MAP or NAME_ARCHETYPE_MAP
    """
    missing = table[table["archetype"].isna()]
    if missing.empty:
        print("No missing archetypes.")
    else:
        for _, row in missing.iterrows():
            print(f"Deck ID {row['deckId']} is missing an archetype.")
            print(f"Check {row['deckUrl']} for correct value.")


def check_missing_category(table):
    """
    Reports any decks that did not get assigned an category.
    The deckUrl is printed so that the correct archetype can be added through
    either the ID_CATEGORY_MAP.
    """
    missing = table[table["category"].isna()]
    if missing.empty:
        print("No missing categories.")
    else:
        for _, row in missing.iterrows():
            print(f"Deck ID {row['deckId']} is missing an category.")
            print(f"Check {row['deckUrl']} for correct value.")

def check_unmatched_card_ids(table, card_table, deck_table):
    """Prints URLS for decks with cards that do not, for some reason, show up in the card table."""
    unmatched = table[~table["cardId"].isin(card_table["cardId"])]
    if unmatched.empty:
        print("No unmatched cardIds.")
    else:
        for _, row in unmatched.iterrows():
            if row["cardId"] != "":
                bad_url = deck_table[deck_table["deckId"] == row["deckId"]]["deckUrl"]
                print(f"Card ID {row['cardId']} is unmatched in the card table.")
                print(f"Check {bad_url} for the offending code.")

def check_wrong_sets(table):
    """Prints URLs for decks that have cards outside of the standard sets for spot checking."""
    standard_sets = "eld|thb|znr|iko|khm|m21"
    non_standard_sets = table[
        (~table["cardId"].str.contains(standard_sets, regex=True))
        & (table["date"] >= "2020-09-29")
        ][["cardId", "name"]].drop_duplicates()
    if non_standard_sets.empty:
        print("All sets are correct.")
    if len(non_standard_sets) == 2 and \
    (non_standard_sets.reset_index()["name"] == pd.Series(["Midnight Reaper", "Murder"])).all():
        print("All sets are correct, besides the usual suspects (Midnight Reaper and Murder).")
    else:
        for _, row in non_standard_sets:
            print(f"The CardId {row['cardId']} needs further investigation - {row['deckUrl']}")



if __name__ == "__main__":
    update(URL)

    with SQLDatabase() as sql_db:
        event_table = sql_db.get_dataframe_from("event")
        deck_table = sql_db.get_dataframe_from("deck")
        deck_list_table = sql_db.get_dataframe_from("deckList")
        card_table = sql_db.get_dataframe_from("card")
        pilot_table = sql_db.get_dataframe_from("pilot")

    clean_dates(event_table)
    rename_id_column(event_table, "eventId")
    rename_id_column(deck_table, "deckId")
    rename_id_column(pilot_table, "pilotId")

    set_latest_release(event_table)

    add_card_id(card_table)

    fix_deck_names(deck_table, ID_NAME_MAP)

    set_archetypes(
        deck_table,
        ARCHETYPE_MAP,
        id_archetype_map=ID_ARCHETYPE_MAP,
        name_archetype_map=NAME_ARCHETYPE_MAP
    )
    set_categories(
        deck_table,
        CATEGORY_MAP,
        id_category_map=ID_CATEGORY_MAP
    )

    fix_abu_codes(card_table, ABU_MAP)
    fix_abu_codes(deck_list_table, ABU_MAP)
    fix_broken_codes(deck_list_table, BROKEN_CODE_MAP)


    fix_rankings(deck_table, RANK_MAP, composite_ranks=COMPOSITE_RANK_MAP)

    full_table = make_full_table(
        event_table=event_table,
        deck_table=deck_table,
        pilot_table=pilot_table,
        deck_list_table=deck_list_table,
        card_table=card_table
        )

    fix_wrong_names(full_table, ID_SPEC_MAP)

    check_missing_archetype(deck_table)
    check_missing_category(deck_table)
    check_unmatched_card_ids(deck_list_table, card_table, deck_table)
    check_wrong_sets(full_table)

    save_to_disk(
        full_table=full_table,
        event_table=event_table,
        deck_table=deck_table,
        deck_list_table=deck_list_table,
        card_table=card_table,
        pilot_table=pilot_table
        )
