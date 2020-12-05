import pandas as pd
import re
import requests
import time
from bs4 import BeautifulSoup

from src.Scraper import Scraper
from src.sqldb import query, commit

URL = "https://www.mtgtop8.com/format?f=ST"
SETS = [
    "eld", "thb", "iko", "m21", "znr",
    "war", "rna", "grn", "m20", "mor",
    "frf", "m11", "m12", "m10", "m13",
    "m19", "m14", "m15", "aer", "akh",
    "bng", "chk", "dar", "dis", "dka",
    "dom", "emn", "gtc", "hou", "ice",
    "inv", "isd", "jou", "ktk", "leg",
    "mbs", "mh1", "mrd", "ogw", "ori",
    "rav", "rix", "roe", "rtr", "sha",
    "soi", "som", "ths", "tsp", "xln",
    "zen"
]


class Updater:
    def __init__(self):
        pass

    def update_events(self, url):
        scraper = EventScraper(url)
        new_events = scraper.update()
        commit(new_events, "event")

    def update_cards(self):
        pass

    def update_decks_and_players(self):
        scraper = DeckPlayerScraper()
        decks, players = scraper.update()
        commit(players, "pilot")
        commit(decks, "deck")

    def update_deck_lists(self):
        pass

    # HELPER FUNCTIONS

    def update_decks(self):
        """Opens event table and gets deck data from each link in event table"""
        new_events = list(self.currently_saved_events.loc[
            ~(self.currently_saved_events["id"].isin(
                self.currently_saved_decks["eventId"]))
        ]["link"])
        result = []
        with requests.Session() as this_session:
            for link in new_events:
                html = this_session.get(link)
                soup = BeautifulSoup(html.text, features="lxml")
                body = soup.body

                names, ranks, links = self._get_winners(body)

                has_points = False
                if self._is_points(ranks[0]):
                    has_points = True

                other_names, other_ranks, other_links = self._add_other_decks(
                    body, has_points)
                names.extend(other_names)
                ranks.extend(other_ranks)
                links.extend(other_links)

                players = self._get_players(body, names)
                new_players = self.check_new_players(players)

                assert self._are_equal_length(names, ranks, players), \
                    "names: " + str(len(names)) \
                    + ", ranks: " + str(len(ranks)) \
                    + ", players: " + str(len(players)) \
                    + ", links: " + str(len(links)) \
                    + " at " + html.url
                assert self._are_equal_length(
                    list(zip(names, ranks, players, links)), names, ranks, players, links)

                result.extend(
                    [
                        (html.url, player, link, name, rank)
                        for (player, link, name, rank)
                        in zip(players, links, names, ranks)
                    ]
                )
        return result, new_players

    def _get_winners(self, body):
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
        finally:
            return [winner_name], [winner_rank], [winner_link]

    def _add_other_decks(self, body, has_points=False):
        names = []
        ranks = []
        links = []
        if has_points:
            for name in body.find_all("div", class_="S14")[:-3]:
                assert not self._is_malformed(
                    name.text), "Bad name - " + name.text
                names.append(name.text.strip())
                this_link = name.find("a").get("href")
                assert self._is_a_link(this_link), "Bad link - " + this_link
                links.append(this_link)
            for points in body.find_all("div", class_="S12"):
                if not self._should_be_skipped(points.text):
                    assert self._is_points(points.text), "Malformed Points " + \
                        points.text
                    ranks.append(points.text.strip())
        else:
            for idx, result in enumerate(body.find_all("div", class_="S14")[:-3]):
                if idx % 2 == 0:
                    if not self._is_rank(result.text):
                        break
                    ranks.append(result.text.strip())
                else:
                    assert not self._is_malformed(
                        result.text), "Bad name - " + result.text
                    names.append(result.text.strip())
                    this_link = result.find("a").get("href")
                    assert self._is_a_link(
                        this_link), "Bad link - " + this_link
                    links.append(this_link)
        return names, ranks, links

    def check_new_players(self, players):
        new_players = []
        for player in players:
            if player not in list(self.currently_saved_players["firstName"] + " " + self.currently_saved_players["lastName"]):
                new_players.append(player)
        return [player.split(maxsplit=1) for player in new_players]

    def _get_players(self, body, names):
        result = []
        for player in body.find_all("div", class_="G11")[:len(names)]:
            result.append(player.find("a").text)
        return result

    def _is_malformed(self, name):
        return re.match("^\$[0-9]*\ \(.*\)$", name) or re.match("^[0-9]*\ TIX$", name)

    def _is_a_link(self, link):
        return re.match("^\?e=.*&d=.*&f=ST", link)

    def _should_be_skipped(self, rank):
        return rank == "close" or rank == "Companion card"

    def _is_points(self, rank):
        return re.match("^[0-9]*\ pts$", rank)

    def _is_rank(self, rank):
        return re.match("^[0-9]*-[0-9]*$", rank) or re.match("^[0-9]*$", rank)

    def _are_equal_length(self, *args):
        equal = True
        length1 = len(args[0])
        for arg in args:
            if len(arg) != length1:
                equal = False
        return equal


def update_card_table():
    """Get cards from SETS using the Scryfall API"""
    card_table = []
    with requests.Session() as this_session:
        for card_set in SETS:
            set_url = f"https://api.scryfall.com/cards/search?order=set&unique=art&q=set%3A'{card_set}'+lang%3A'en'"

            card_data_response = this_session.get(set_url)
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


def scrape_deck_lists():
    deck_data = _open_sql("deck")
    ROOT_URL = "https://www.mtgtop8.com/event"
    urls = ROOT_URL + deck_data["deckUrl"]

    assert len(list(deck_data["id"])) == len(
        urls), "Mismatched list of decks to urls"
    deck_lists = []
    with requests.Session() as this_session:
        for url, deck_id in zip(urls, deck_data["id"]):
            deck_list_response = this_session.get(url)
            deck_list_soup = BeautifulSoup(
                deck_list_response.text, features="lxml")
            deck_list_body = deck_list_soup.body

            for item in deck_list_body.find_all("td", class_="G14"):
                this_card = item.text.strip().split(maxsplit=1)
                count = this_card[0]
                assert count.isdigit(), "Count is not a digit - " + \
                    deck_list_response.url + " - " + this_card

                this_id = item.find_all("span", class_="L14")[0].get("id")[:-2]
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

                deck_lists.append(
                    (collector_number+set_name, deck_id, count, slot, )
                )

    return deck_lists


class PageScraper:

    def update(self):
        pass

    def _is_up_to_date(self):
        pass

class EventScraper(PageScraper):

    def __init__(self, url):
        self.url = url
        currently_saved_events = query("event")
        self.latest_links = list(
            currently_saved_events.loc[
                currently_saved_events["date"] == currently_saved_events["date"].max()
            ]["link"]
        )

    def update(self):
        with Scraper(self.url) as scraper:
            page = 1
            result = self._get_page(scraper)
            next_page = True
            while next_page and not self._is_up_to_date(result):
                page += 1
                scraper.execute("PageSubmit", page)
                time.sleep(2)
                result.extend(self._get_page(scraper))
                time.sleep(2)
                next_page = "Nav_PN_no" not in str(scraper)
            return result

    # HELPER FUNCTIONS
    def _get_page(self, scraper):
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

    def _is_up_to_date(self, result):
        new_links = []
        for item in result:
            _, links, _ = item
            new_links.append(links)
        for old_link in self.latest_links:
            return old_link in new_links

class DeckPlayerScraper(PageScraper):
    def __init__(self):
        currently_saved_events = query("event")
        currently_saved_decks = query("deck")
        self.new_events = list(
            currently_saved_events.loc[
                ~(currently_saved_events["id"].isin(currently_saved_decks["eventId"]))
                ]["link"]
            )
    def update(self):
        result = []
        new_players = ""
        with requests.Session() as this_session:
            print(self.new_events)
            for link in self.new_events:
                html = this_session.get(link)
                soup = BeautifulSoup(html.text, features="lxml")
                body = soup.body

                names, ranks, links = self._get_winners(body)

                print("Is this running?")

                has_points = False
                if self._is_points(ranks[0]):
                    has_points = True

                other_names, other_ranks, other_links = self._add_other_decks(
                    body, has_points)
                names.extend(other_names)
                ranks.extend(other_ranks)
                links.extend(other_links)

                players = self._get_players(body, names)
                new_players = self.check_new_players(players)

                assert self._are_equal_length(names, ranks, players), \
                    "names: " + str(len(names)) \
                    + ", ranks: " + str(len(ranks)) \
                    + ", players: " + str(len(players)) \
                    + ", links: " + str(len(links)) \
                    + " at " + html.url
                assert self._are_equal_length(
                    list(zip(names, ranks, players, links)), names, ranks, players, links)

                result.extend(
                    [
                        (html.url, player, link, name, rank)
                        for (player, link, name, rank)
                        in zip(players, links, names, ranks)
                    ]
                )

                breakpoint()
            return result, new_players

    def _get_winners(self, body):
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
        finally:
            return [winner_name], [winner_rank], [winner_link]

    def _add_other_decks(self, body, has_points=False):
        names = []
        ranks = []
        links = []
        if has_points:
            for name in body.find_all("div", class_="S14")[:-3]:
                assert not self._is_malformed(
                    name.text), "Bad name - " + name.text
                names.append(name.text.strip())
                this_link = name.find("a").get("href")
                assert self._is_a_link(this_link), "Bad link - " + this_link
                links.append(this_link)
            for points in body.find_all("div", class_="S12"):
                if not self._should_be_skipped(points.text):
                    assert self._is_points(points.text), "Malformed Points " + \
                        points.text
                    ranks.append(points.text.strip())
        else:
            for idx, result in enumerate(body.find_all("div", class_="S14")[:-3]):
                if idx % 2 == 0:
                    if not self._is_rank(result.text):
                        break
                    ranks.append(result.text.strip())
                else:
                    assert not self._is_malformed(
                        result.text), "Bad name - " + result.text
                    names.append(result.text.strip())
                    this_link = result.find("a").get("href")
                    assert self._is_a_link(
                        this_link), "Bad link - " + this_link
                    links.append(this_link)
        return names, ranks, links

    def check_new_players(self, players):
        currently_saved_players = query("pilot")
        new_players = []
        for player in players:
            if player not in list(currently_saved_players["firstName"] + " " + currently_saved_players["lastName"]):
                new_players.append(player)
        return [player.split(maxsplit=1) for player in new_players]

    def _get_players(self, body, names):
        result = []
        for player in body.find_all("div", class_="G11")[:len(names)]:
            result.append(player.find("a").text)
        return result

    def _is_malformed(self, name):
        return re.match("^\$[0-9]*\ \(.*\)$", name) or re.match("^[0-9]*\ TIX$", name)

    def _is_a_link(self, link):
        return re.match("^\?e=.*&d=.*&f=ST", link)

    def _should_be_skipped(self, rank):
        return rank == "close" or rank == "Companion card"

    def _is_points(self, rank):
        return re.match("^[0-9]*\ pts$", rank)

    def _is_rank(self, rank):
        return re.match("^[0-9]*-[0-9]*$", rank) or re.match("^[0-9]*$", rank)

    def _are_equal_length(self, *args):
        equal = True
        length1 = len(args[0])
        for arg in args:
            if len(arg) != length1:
                equal = False
        return equal
