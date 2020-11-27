import pandas as pd
import re
import requests
import time
from bs4 import BeautifulSoup

from src.Scraper import Scraper
from src.sqldb import SQLDatabase

URL = "https://www.mtgtop8.com/format?f=ST"
SCRYFALL = "https://api.scryfall.com/cards/search?q=set%3A"
SETS = [
    "eld",
    "thb",
    "iko",
    "m21",
    "znr"
]

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

def scrape_event_data():
    """Opens event table and gets deck data from each link in event table"""
    event_df = _open_sql("event")
    results = []
    for link in event_df["link"]:
        html = requests.get(link)
        soup = BeautifulSoup(html.text, features="lxml")
        body = soup.body

        names, ranks, links = _get_winners(body)

        has_points = False
        if _is_points(ranks[0]):
            has_points = True

        other_names, other_ranks, other_links = _add_other_decks(body, has_points)
        names.extend(other_names)
        ranks.extend(other_ranks)
        links.extend(other_links)

        players = _get_players(body, names)

        assert _are_equal_length(names, ranks, players), \
            "names: " + str(len(names)) \
            + ", ranks: " + str(len(ranks)) \
            + ", players: " + str(len(players)) \
            + ", links: " + str(len(links)) \
            + " at " + html.url
        assert _are_equal_length(
            list(zip(names, ranks, players, links)), names, ranks, players, links)

        results.extend(
            [
                (html.url, player, link, name, rank)
                for (player, link, name, rank)
                in zip(players, links, names, ranks)
            ]
        )

    return results

def _open_sql(table):
    with SQLDatabase() as sql_db:
        return sql_db.get_dataframe_from(table)


def _get_winners(body):
    try:
        winner_rank = body.find_all("div", class_="W12")[1].text
        winner_name = body.find_all("div", class_="W14")[0].find("a").text
        winner_link = body.find_all("div", class_="W14")[0].find("a").get("href")
    except (IndexError, AttributeError):
        winner_rank = body.find_all("div", class_="W14")[0].text
        winner_name = body.find_all("div", class_="W14")[1].find("a").text
        winner_link = body.find_all("div", class_="W14")[1].find("a").get("href")
    finally:
        return [winner_name], [winner_rank], [winner_link]


def _add_other_decks(body, has_points=False):
    names = []
    ranks = []
    links = []
    if has_points:
        for name in body.find_all("div", class_="S14")[:-3]:
            assert not _is_malformed(name.text), "Bad name - " + name.text
            names.append(name.text.strip())
            this_link = name.find("a").get("href")
            assert _is_a_link(this_link), "Bad link - " + this_link
            links.append(this_link)
        for points in body.find_all("div", class_="S12"):
            if not _should_be_skipped(points.text):
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
                assert not _is_malformed(result.text), "Bad name - " + result.text
                names.append(result.text.strip())
                this_link = result.find("a").get("href")
                assert _is_a_link(this_link), "Bad link - " + this_link
                links.append(this_link)
    return names, ranks, links


def _get_players(body, names):
    result = []
    for player in body.find_all("div", class_="G11")[:len(names)]:
        result.append(player.find("a").text)
    return result


def _is_malformed(name):
    return re.match("^\$[0-9]*\ \(.*\)$", name) or re.match("^[0-9]*\ TIX$", name)

def _is_a_link(link):
    return re.match("^\?e=.*&d=.*&f=ST", link)

def _should_be_skipped(rank):
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

def update_card_table():
    card_table = []
    for card_set in SETS:
        set_url = f"https://api.scryfall.com/cards/search?q=set%3A'{card_set}'"

        card_data_response = requests.get(set_url)
        card_data_json = card_data_response.json()
        card_data = card_data_json["data"]

        while card_data_json["has_more"]:
            next_page = card_data_json["next_page"]
            card_data_response = requests.get(next_page)
            card_data_json = card_data_response.json()
            card_data.extend(card_data_json["data"])
    
        for card in card_data:
            this_card = (
                card["collector_number"],
                card["set"],
                card["name"],
                int(card["cmc"]),
                "".join(card["color_identity"]),
                card["legalities"]["standard"]
            )

            try:
                oracle_text = card["oracle_text"]
            except KeyError:
                oracle_text = " // ".join(face["oracle_text"] for face in card["card_faces"])

            try:
                mana_cost = card["mana_cost"]
            except KeyError:
                mana_cost = " // ".join(face["mana_cost"] for face in card["card_faces"])
                if mana_cost == " // ":
                    mana_cost = ""

            this_card += (oracle_text, mana_cost)
            card_table.append(this_card)

    return card_table
