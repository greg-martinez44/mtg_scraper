"""
Saving functionality for data scrapped from mtgtop8.com
"""
import time
import requests
from bs4 import BeautifulSoup

from src.constants import SETS, URL
from src.scraper import Scraper
from src.sqldb import query, commit
from src.data_assertions import (
    is_up_to_date,
    is_malformed,
    is_a_link,
    should_be_skipped,
    is_points,
    is_rank,
    are_equal_length,
    check_new_players
    )

def update_events(url):
    """
    Gets a list from the Sqlite file with all the events from the most recent update.
    This list is used to determine how far the EventScraper object needs to go
    to get all the new events from mtgtop8. It then commits the new events to the Sqlite table.
    """
    currently_saved_events = query("event")
    latest_events = list(
        currently_saved_events.loc[
            currently_saved_events["date"] == currently_saved_events["date"].max(
            )
        ]["link"]
    )
    scraper = EventScraper(url, latest_events)
    new_events = scraper.update()
    commit(new_events, "event")

def update_cards():
    """
    Updates all the card definitions from scryfall.
    This is a fresh update of all data every time it is run,
    since older cards are not entirely static.
    Run this sparingly - in the case of a new ban, a new set release, or rotation.

    """
    scraper = CardScraper()
    new_cards = scraper.update()
    commit(new_cards, "card")

def update_decks_and_players():
    """
    Grabs the new data (where the event id is not in the deck table)
    and makes a DeckPlayer scraper to retrieve it.
    These two are combined because 'Players' and 'Decks' are scraped
    from the same locaiton, at the same time.
    """
    currently_saved_events = query("event")
    currently_saved_decks = query("deck")
    currently_saved_players = query("pilot")
    new_events = list(
        currently_saved_events.loc[
            ~(currently_saved_events["id"].isin(
                currently_saved_decks["eventId"]))
        ]["link"]
    )
    scraper = DeckPlayerScraper(new_events, currently_saved_players)
    new_decks, new_players = scraper.update()
    commit(new_players, "pilot")
    commit(new_decks, "deck")

def update_deck_lists():
    """Gets all the new decks from recent update and scrapes the deck lists."""
    currently_saved_decks = query("deck")
    currently_saved_deck_lists = query("decklist")
    new_links = currently_saved_decks.loc[
        ~(currently_saved_decks["id"].isin(
            currently_saved_deck_lists["deckId"]))
    ]
    scraper = DeckListScraper(new_links)
    new_deck_lists = scraper.update()
    commit(new_deck_lists, "decklist")

def get_page(scraper):
    """Gets the page data from mtgtop8"""
    events = scraper.get_all_by(
        "xpath",
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
    )
    dates = scraper.get_all_by(
        "xpath",
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//td[@class='S10']"
    )
    return [
        (event.text, event.get_attribute("href"), date.text)
        for event, date in zip(events, dates)
    ]

def get_winners(body):
    """
    Gets first place deck/pilot; mtgtop8 has different tags for the winner
    when you navigate to a new event page
    """
    try:
        winner_rank = body.find_all("div", class_="W12")[1].text
        winner_name = body.find_all("div", class_="W14")[0].find("a").text
        winner_link = body.find_all("div", class_="W14")[
            0].find("a").get("href")
    except (IndexError, AttributeError):
        winner_rank = body.find_all("div", class_="W14")[0].text
        winner_name = body.find_all("div", class_="W14")[1].find("a").text
        winner_link = body.find_all("div", class_="W14")[
            1].find("a").get("href")
    return [winner_name], [winner_rank], [winner_link]

def get_players(body, names):
    """Gets all the players from the page"""
    result = []
    for player in body.find_all("div", class_="G11")[:len(names)]:
        result.append(player.find("a").text)
    return result

def add_other_decks(body, has_points=False):
    """Gets the rest of the deck/pilot data from the event page"""
    names = []
    ranks = []
    links = []
    if has_points:
        for name in body.find_all("div", class_="S14")[:-3]:
            assert not is_malformed(
                name.text), "Bad name - " + name.text
            names.append(name.text.strip())
            this_link = name.find("a").get("href")
            assert is_a_link(this_link), "Bad link - " + this_link
            links.append(this_link)
        for points in body.find_all("div", class_="S12"):
            if not should_be_skipped(points.text):
                assert is_points(points.text), "Malformed Points " + \
                    points.text
                ranks.append(points.text.strip())
    else:
        for idx, result in enumerate(body.find_all("div", class_="S14")[:-3]):
            if idx % 2 == 0:
                if not is_rank(result.text):
                    break
                ranks.append(result.text.strip())
            else:
                assert not is_malformed(
                    result.text), "Bad name - " + result.text
                names.append(result.text.strip())
                this_link = result.find("a").get("href")
                assert is_a_link(
                    this_link), "Bad link - " + this_link
                links.append(this_link)
    return names, ranks, links

def get_html_body(session, link):
    """Get data from link's html"""
    html = session.get(link)
    soup = BeautifulSoup(html.text, features="lxml")
    return soup.body, html.url

def get_json_body(session, url):
    "Gets data from link's json response"
    response = session.get(url)
    json = response.json()
    data = json["data"]

    while json["has_more"]:
        next_page = json["next_page"]
        response = session.get(next_page)
        json = response.json()
        data.extend(json["data"])

    return data

class PageScraper:
    """Abstract base class for scraper objects"""

    def update(self):
        """To be overwritten with specific update function."""
        return

    def check_previous(self, new_data):
        """Checks if scrapped data is new or old"""
        return new_data


class EventScraper(PageScraper):
    """Handles updating Events"""

    def __init__(self, url, latest_events):
        self.url = url
        self.latest_events = latest_events

    def update(self):
        """Traverse the mtgtop8 page and get new events."""
        with Scraper(self.url) as scraper:
            page = 0
            result = get_page(scraper)
            next_page = True
            up_to_date = False
            while next_page and not up_to_date:
                print("Updating next page...")
                page += 1
                scraper.execute("PageSubmit", page)
                time.sleep(2)
                result.extend(get_page(scraper))
                time.sleep(2)
                next_page = "Nav_PN_no" not in str(scraper)
                up_to_date = self.check_previous(result)
            return result

    def check_previous(self, new_data):
        """
        Returns True if the second page should be looked at, otherwise
        the update ends.
        """
        return is_up_to_date(new_data, self.latest_events)


class DeckPlayerScraper(PageScraper):
    """Handles updating Deck and Pilot"""

    def __init__(self, new_events, currently_saved_players):
        self.new_events = new_events
        self.currently_saved_players = currently_saved_players

    def update(self):
        result = []
        new_players = []
        with requests.Session() as this_session:
            for link in self.new_events:
                print("updating " + link)
                body, url = get_html_body(this_session, link)

                names, ranks, links = get_winners(body)

                has_points = False
                if is_points(ranks[0]):
                    has_points = True

                other_names, other_ranks, other_links = add_other_decks(
                    body, has_points)
                names.extend(other_names)
                ranks.extend(other_ranks)
                links.extend(other_links)

                players = get_players(body, names)
                new_players.extend(self.check_previous(players))

                assert are_equal_length(names, ranks, players), \
                    "names: " + str(len(names)) \
                    + ", ranks: " + str(len(ranks)) \
                    + ", players: " + str(len(players)) \
                    + ", links: " + str(len(links)) \
                    + " at " + url
                assert are_equal_length(
                    list(zip(names, ranks, players, links)), names, ranks, players, links)

                result.extend(
                    [
                        (url, player, link, name, rank)
                        for (player, link, name, rank)
                        in zip(players, links, names, ranks)
                    ]
                )

            return result, new_players

    def check_previous(self, new_data):
        """
        Returns players that are not new list of players.
        """
        return check_new_players(new_data, self.currently_saved_players)

class CardScraper(PageScraper):
    """Handles updating Card table from Scryfall"""

    def __init__(self):
        # Definition of all the sets to capture
        self.sets = SETS

    def update(self):
        card_table = []
        with requests.Session() as this_session:
            for card_set in self.sets:
                set_url = (
                    "https://api.scryfall.com/cards/search?order=set&unique=prints&q=set%3A"
                    + f"'{card_set}'+lang%3A'en'"
                )

                card_data = get_json_body(this_session, set_url)

                for card in card_data:
                    this_card = (
                        card["collector_number"],
                        card["set"],
                        card["name"],
                        int(card["cmc"]),
                        "".join(card["color_identity"]),
                        card["legalities"]["standard"]
                    )

                    # Oracle text & Mana costs are different for cards with two faces...
                    try:
                        oracle_text = card["oracle_text"]
                    except KeyError:
                        oracle_text = " // ".join(face["oracle_text"]
                                                  for face in card["card_faces"])

                    try:
                        mana_cost = card["mana_cost"]
                    except KeyError:
                        mana_cost = " // ".join(face["mana_cost"]
                                                for face in card["card_faces"])
                        if mana_cost == " // ":
                            mana_cost = ""

                    this_card += (oracle_text, mana_cost)
                    card_table.append(this_card)

        return card_table


class DeckListScraper(PageScraper):
    """Handles updating DeckList"""

    def __init__(self, new_links):
        self.new_links = new_links
        root_url = URL.replace("format?f=ST", "event")
        self.urls = root_url + self.new_links["deckUrl"]

    def update(self):
        assert len(list(self.new_links["id"])) == len(
            self.urls), "Mismatched list of decks to urls"
        deck_lists = []
        with requests.Session() as this_session:
            for url, deck_id in zip(self.urls, self.new_links["id"]):
                deck_list_body, deck_url = get_html_body(this_session, url)

                for item in deck_list_body.find_all("td", class_="G14"):
                    this_card = item.text.strip().split(maxsplit=1)
                    count = this_card[0]
                    assert count.isdigit(), "Count is not a digit - " + \
                        deck_url + " - " + this_card

                    this_id = item.find_all("span", class_="L14")[
                        0].get("id")[:-2]
                    slot = this_id[:2]
                    set_name = this_id[2:5]
                    collector_number = this_id[5:]
                    if set_name == "10m":
                        set_name = "m10"
                    if set_name == "11m":
                        set_name = "m11"
                    if set_name == "12m":
                        set_name = "m12 "
                    if set_name == "13m":
                        set_name = "m13"
                    if set_name == "14m":
                        set_name = "m14"
                    if set_name == "15m":
                        set_name = "m15"

                    card_name = item.find_all("span", class_="L14")[0].text
                    deck_lists.append(
                        (collector_number+set_name, deck_id, count, slot, card_name )
                    )

        return deck_lists
