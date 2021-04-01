"""
Download and clean known bad data points for MTG standard tournament
scene inspection
"""

import json
import logging
import pandas as pd

from src.constants import (
    URL,
    ZENDIKAR_RELEASE,
    KALDHEIM_RELEASE,
    FULL_TABLE_COLUMNS
    )
import src.models as m
from src.sqldb import SQLDatabase

new_data = {
    "archetype_maps": {
        "id_map":{
            }
        },
    "category_maps": {
        "id_map":{
            }
        },
    "broken_code_map": {
        },
    "id_spec_map": {
        }
    }

def load_json_data():
    with open("/Users/gregmartinez/projects/mtg_scraper/src/data/maps.json", "r") as json_file:
        out = json.load(json_file)
    return out

def update_json_data(new_data):
    """Updates json file with new spot fixes for oddly defined decks"""

    with open("/Users/gregmartinez/projects/mtg_scraper/src/data/maps.json", "r") as json_file:
        current_data = json.load(json_file)

    current_data["archetype_maps"]["id_map"].update(new_data["archetype_maps"]["id_map"])
    current_data["category_maps"]["id_map"].update(new_data["category_maps"]["id_map"])
    current_data["broken_code_map"].update(new_data["broken_code_map"])
    current_data["id_spec_map"].update(new_data["id_spec_map"])

    with open("/Users/gregmartinez/projects/mtg_scraper/src/data/maps.json", "w") as json_file:
        json.dump(current_data, json_file)

def update(url):
    """Update tables from mtgtop8.com"""

    m.update_events(url)
    m.update_decks_and_players()
    m.update_deck_lists()

def clean_dates(df, dayfirst=True):
    """Cast date column to datetime objects"""

    df["date"] = pd.to_datetime(df["date"], dayfirst=dayfirst)

def rename_id_column(df, new_id, inplace=True):
    """Fix id column names"""

    df.rename(columns={"id": new_id}, inplace=inplace)

def add_card_id(table):
    "Adds a card id (number + name) to the card table"

    table["setNumber"] = table["setNumber"].str.zfill(3)
    table["cardId"] = table["setNumber"] + table["setName"]

def fix_deck_names(table, id_name_map):
    """Replaces weird deck names with sensical ones."""

    for deck_id, deck_name in id_name_map.items():
        table.loc[table["deckId"] == int(deck_id), "name"] = deck_name

def set_archetypes(table, archetype_map, **kwargs):
    """
    Add archetype based on either keywords in the name of the deck,
    the id, or specifc name.
    """

    for archetype, flags in archetype_map.items():
        for flag in flags:
            table.loc[
                table["name"].str.contains(flag, case=False),
                "archetype"
            ] = archetype
    if kwargs.get("id_archetype_map", None):
        logging.debug("Had to fix archetypes by id")
        for deck_id, archetype in kwargs["id_archetype_map"].items():
            table.loc[table["deckId"] == int(deck_id), "archetype"] = archetype
    if kwargs.get("name_archetype_map", None):
        logging.debug("Had to fix archetypes by deck name")
        for deck_name, archetype in kwargs["name_archetype_map"].items():
            table.loc[table["name"] == deck_name, "archetype"] = archetype

def set_categories(table, category_map, **kwargs):
    """Add category based on either keywords in the name of the deck or id."""

    for category, flags in category_map.items():
        for flag in flags:
            table.loc[
                table["name"].str.contains(flag, case=False),
                "category"
            ] = category
    if kwargs.get("id_category_map", None):
        logging.debug("Had to fix categories by deck id")
        for deck_id, category in kwargs["id_category_map"].items():
            table.loc[table["deckId"] == int(deck_id), "category"] = category

def fix_abu_codes(table, abu_map, inplace=True):
    """Fixes 'abu' codes in mtgtop8's HTML code."""

    table["cardId"].replace(to_replace=abu_map, inplace=inplace)

def fix_broken_codes(table, broken_code_map, inplace=True):
    """
    Some card codes in mtgtop8's HTML are from old sets;
    this fixes them to be more recent.
    """

    table["cardId"].replace(to_replace=broken_code_map, inplace=inplace)

def set_latest_release(table):
    """
    Adds a label column for which set was most recently released at
    the time of the event.
    """

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
        event_id = int(event_id)
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

    result = pd.merge(
        events_decks_pilots_deck_list,
        kwargs["card_table"],
        on="cardId",
        suffixes=[None, "_cards"]
        )

    return (
        result[FULL_TABLE_COLUMNS]
        .drop_duplicates()
        .sort_values(by=["eventId", "deckId", "slot"])
        .reset_index(drop=True)
        )

def fix_wrong_names(table, id_specs_map):
    """Spot fixes weird deck names"""

    for card_id, specs in id_specs_map.items():
        table.loc[table["cardId"] == card_id, "cardId"] = specs[0]
        table.loc[table["cardId"] == card_id, "name"] = specs[1]
        table.loc[table["cardId"] == card_id, "color"] = specs[2]

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
            bad_deck_id = row["deckId"]
            print(f"Deck ID {bad_deck_id} is missing an archetype.")
            print(f"Check https://www.mtgtop8.com/event{row['deckUrl']} for correct value.")
            new_value = input("Enter the correct archetype: ")
            new_data["archetype_maps"]["id_map"].update({bad_deck_id: new_value})



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
            bad_deck_id = row["deckId"]
            print(f"Deck ID {row['deckId']} is missing an category.")
            print(f"Check https://www.mtgtop8.com/event{row['deckUrl']} for correct value.")
            new_value = input("Enter the correct category: ")
            new_data["category_maps"]["id_map"].update({bad_deck_id: new_value})

def check_unmatched_card_ids(table, cards, decks):
    """
    Prints URLS for decks with cards that do not, for some reason,
    show up in the card table.
    """

    unmatched = table[~table["cardId"].isin(cards["cardId"])]
    if unmatched.empty:
        print("No unmatched cardIds.")
    else:
        for _, row in unmatched.iterrows():
            if row["cardId"] != "":
                bad_card_id = row["cardId"]
                bad_url = decks[decks["deckId"] == row["deckId"]]["deckUrl"]
                print(
                    f"Card ID {bad_card_id} is unmatched in the card table."
                )
                print(f"Check {bad_url} for the offending code.")
                new_value = input("Enter the correct cardId: ")
                new_data["broken_code_map"].update({bad_card_id: new_value})

def check_wrong_sets(table, a_deck_table):
    """
    Prints URLs for decks that have cards outside of the standard sets
    for spot checking.
    """

    standard_sets = "eld|thb|znr|iko|khm|m21"
    non_standard_sets = table[
        (~table["cardId"].str.contains(standard_sets, regex=True))
        & (table["date"] >= "2020-09-29")
        ][["cardId", "name", "deckId"]].drop_duplicates()
    if non_standard_sets.empty:
        print("All sets are correct.")
    if len(non_standard_sets) == 2 and  (
        (
            non_standard_sets
            .reset_index()
            ["name"]
            .values
            .tolist()
        ) == ["Midnight Reaper", "Murder"]
    ):
        print(
            "All sets are correct, besides the usual"
            "suspects (Midnight Reaper and Murder)."
        )
    else:
        for _, row in non_standard_sets.iterrows():
            bad_card_id = row["cardId"]
            urls_to_check = a_deck_table[
                a_deck_table["deckId"] == row["deckId"]
            ]["deckUrl"].values[0]
            print(
                f"The CardId {bad_card_id} needs further"
                f"investigation - https://www.mtgtop8.com/event{urls_to_check}"
            )
            new_value = eval(input(
                "Enter the corect values "
                "['new_card_id', 'Name', 'color or empty string']: ")
            )
            new_data["id_spec_map"].update({bad_card_id: new_value})

def main():
    """The main runner of the script"""

    logging.basicConfig(
        filename="main_output.log",
        level=logging.DEBUG,
        format="%(asctime)s %(message)s"
        )

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

    data_maps = load_json_data()

    fix_deck_names(deck_table, data_maps["id_names"])

    set_archetypes(
        deck_table,
        data_maps["archetype_maps"]["base_map"],
        id_archetype_map=data_maps["archetype_maps"]["id_map"],
        name_archetype_map=data_maps["archetype_maps"]["name_map"]
    )
    set_categories(
        deck_table,
        data_maps["category_maps"]["base_map"],
        id_category_map=data_maps["category_maps"]["id_map"]
    )

    fix_abu_codes(card_table, data_maps["abu_map"])
    fix_abu_codes(deck_list_table, data_maps["abu_map"])
    fix_broken_codes(deck_list_table, data_maps["broken_code_map"])


    fix_rankings(
        deck_table,
        data_maps["rank_map"]["base_map"],
        composite_ranks=data_maps["rank_map"]["composite_map"])

    full_table = make_full_table(
        event_table=event_table,
        deck_table=deck_table,
        pilot_table=pilot_table,
        deck_list_table=deck_list_table,
        card_table=card_table
        )

    fix_wrong_names(full_table, data_maps["id_spec_map"])

    check_missing_archetype(deck_table)
    check_missing_category(deck_table)
    check_unmatched_card_ids(deck_list_table, card_table, deck_table)
    check_wrong_sets(full_table, deck_table)

    save_to_disk(
        full_table=full_table,
        event_table=event_table,
        deck_table=deck_table,
        deck_list_table=deck_list_table,
        card_table=card_table,
        pilot_table=pilot_table
        )

    logging.info("All tables saved")

    update_json_data(new_data)

if __name__ == "__main__":
    main()
