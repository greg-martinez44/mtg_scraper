import pandas as pd

from src.constants import *
import src.models as m
from src.sqldb import SQLDatabase

def update(url):
    updater = m.Updater()
    updater.update_events(URL)
    updater.update_decks_and_players()
    updater.update_deck_lists()

def clean_dates(df, dayfirst=True):
    df["date"] = pd.to_datetime(df["date"], dayfirst=dayfirst)

def rename_id_column(df, new_id, inplace=True):
    df.rename(columns={"id": new_id}, inplace=inplace)

def add_card_id(card_table):
    card_table["setNumber"] = card_table["setNumber"].str.zfill(3)
    card_table["cardId"] = card_table["setNumber"] + card_table["setName"]

def fix_deck_names(deck_table, id_name_map):
    for deck_id, deck_name in id_name_map.items():
        deck_table.loc[deck_table["deckId"] == deck_id, "name"] = deck_name

def set_archetypes(deck_table, archetype_map, **kwargs):
    for archetype, flags in archetype_map.items():
        for flag in flags:
            deck_table.loc[deck_table["name"].str.contains(flag, case=False), "archetype"] = archetype
    if kwargs.get("id_archetype_map", None):
        for deck_id, archetype in kwargs["id_archetype_map"].items():
            deck_table.loc[deck_table["deckId"] == deck_id, "archetype"] = archetype
    if kwargs.get("name_archetype_map", None):
        for deck_name, archetype in kwargs["name_archetype_map"].items():
            deck_table.loc[deck_table["name"] == deck_name, "archetype"] = archetype

def set_categories(deck_table, category_map, **kwargs):
    for category, flags in category_map.items():
        for flag in flags:
            deck_table.loc[deck_table["name"].str.contains(flag, case=False), "category"] = category
    if kwargs.get("id_category_map", None):
        for deck_id, category in kwargs["id_category_map"].items():
            deck_table.loc[deck_table["deckId"] == deck_id, "category"] = category

def fix_abu_codes(table, abu_map, inplace=True):
    table["cardId"].replace(to_replace=abu_map, inplace=inplace)

def fix_broken_codes(table, broken_code_map, inplace=True):
    table["cardId"].replace(to_replace=broken_code_map, inplace=inplace)

def set_latest_release(table):
    table.loc[table["date"] < ZENDIKAR_RELEASE, "latest_set"] = "Ikoria"
    table.loc[(table["date"] >= ZENDIKAR_RELEASE) & (table["date"] < KALDHEIM_RELEASE), "latest_set"] = "Zendikar Rising"
    table.loc[table["date"] >= KALDHEIM_RELEASE, "latest_set"] = "Kaldheim"

def fix_rankings(table, ranking_map, composite_ranks=None):
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
    for card_id, specs in id_specs_map.items():
        table.loc[table["cardId"] == card_id, "name"] = specs[1]
        table.loc[table["cardId"] == card_id, "color"] = specs[2]
        table.loc[table["cardId"] == card_id, "cardId"] = specs[0]

def save_to_disk(**kwargs):
    for table in kwargs:
        kwargs[table].to_csv(f"flat_files/{table}.csv", index=False)

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

    set_archetypes(deck_table, ARCHETYPE_MAP, id_archetype_map=ID_ARCHETYPE_MAP, name_archetype_map=NAME_ARCHETYPE_MAP)
    set_categories(deck_table, CATEGORY_MAP, id_category_map=ID_CATEGORY_MAP)

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

    save_to_disk(
        full_table=full_table,
        event_table=event_table,
        deck_table=deck_table,
        deck_list_table=deck_list_table,
        card_table=card_table,
        pilot_table=pilot_table
        )
