import os
import pandas as pd
import re
import requests
import sqlite3
import time
from bs4 import BeautifulSoup

from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

def scrape_data_from(url):
    """Uses webdriver to populate event table from mtgtop8.com"""
    result = []
    with Scraper(url) as scraper:
        page = 1
        result = _get_page(scraper)
        next_page = True
        while next_page:
            page += 1
            scraper.execute("PageSubmit", page)
            time.sleep(2)
            result.extend(_get_page(scraper))
            time.sleep(2)
            next_page = "Nav_PN_no" not in str(scraper)
        return result

def _get_page(scraper):
    events = _get_events_from(scraper)
    dates = _get_dates_from(scraper)
    result = _get_info_for(events, dates)
    return result

def _get_events_from(scraper):
    result = scraper.get_all_by(
        "xpath",
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
    )
    return result

def _get_dates_from(scraper):
    result = scraper.get_all_by(
        "xpath",
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//td[@class='S10']"
        )
    return result

def _get_info_for(events, dates):
    return [
        (event.text, event.get_attribute("href"), date.text)
        for event, date in zip(events, dates)
    ]



def get_deck_table():
    """Opens event table and gets deck data from each liink in event table"""
    event_df = _open_sql("event")
    results = []
    for link, event in zip(event_df["link"], event_df["name"]):
        html = requests.get(link)
        soup = BeautifulSoup(html.text, features="lxml")
        body = soup.body
        

        names, ranks = _get_winners(body)

        has_points = False
        if _is_points(ranks[0]):
            has_points = True

        other_names, other_ranks = _add_other_decks(body, has_points)
        names.extend(other_names)
        ranks.extend(other_ranks)

        players = _get_players(body, names)

        assert _are_equal_length(names, ranks, players), \
            "names: " + str(len(names)) \
            + ", ranks: " + str(len(ranks)) \
            + ", players: " + str(len(players)) \
            + " at " + html.url
        assert _are_equal_length(
            list(zip(names, ranks, players)), names, ranks, players)

        results.extend(
            [
                (event, player, name, rank)
                for (player, name, rank)
                in zip(players, names, ranks)
            ]
        )

    return results


def _open_sql(table):
    db = "dbs/links.db"
    
    conn = sqlite3.connect(db)
    result = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return result


def _get_winners(body):
    try:
        winner_rank = body.find_all("div", class_="W12")[1].text
        winner_name = body.find_all("div", class_="W14")[0].find("a").text
    except (IndexError, AttributeError):
        winner_rank = body.find_all("div", class_="W14")[0].text
        winner_name = body.find_all("div", class_="W14")[1].find("a").text
    finally:
        return [winner_name], [winner_rank]


def _add_other_decks(body, has_points=False):
    names = []
    ranks = []
    if has_points:
        for name in body.find_all("div", class_="S14")[:-3]:
            assert not _is_malformed(
                name.text), "Bad name - " + name.text
            names.append(name.text.strip())
        for points in body.find_all("div", class_="S12"):
            if not should_be_skipped(points.text):
                assert _is_points(points.text), "Malformed Points " + \
                    points.text
                ranks.append(points.text.strip())
    else:
        for idx, result in enumerate(body.find_all("div", class_="S14")[:-3]):
            if idx % 2 == 0:
                if not _is_rank(result.text):
                    break
                ranks.append(result.text.strip())
            else:
                assert not _is_malformed(
                    result.text), "Bad name - " + result.text
                names.append(result.text.strip())
    return names, ranks


def _get_players(body, names):
    result = []
    for player in body.find_all("div", class_="G11")[:len(names)]:
        result.append(player.find("a").text)
    return result


def _is_malformed(name):
    return re.match("^\$[0-9]*\ \(.*\)$", name) or re.match("^[0-9]*\ TIX$", name)


def should_be_skipped(rank):
    return rank == "close" or rank == "Companion card"


def _is_points(rank):
    return re.match("^[0-9]*\ pts$", rank)


def _is_rank(rank):
    return re.match("^[0-9]*-[0-9]*$", rank) or re.match("^[0-9]*$", rank)


def _are_equal_length(*args):
    equal = True
    length1 = len(args[0])
    for arg in args:
        if len(arg) != length1:
            equal = False
    return equal

def _save(data):
    for player, name, rank in data:
        _union(db, player, "player")
        _union(db, (name, rank), "deck")

def _save_events(data):
    pass

def _save_players(data):
    pass

def _save_decks(data):
    pass

def _save_decklists(data):
    pass

def _save_cards(data):
    pass
