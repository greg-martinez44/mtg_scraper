"""
Collection of asserts used in the models module
"""
import re

def is_up_to_date(result, latest):
    """Checks if there are any old links in the new links seen on mtgtop8"""
    new_links = []
    for item in result:
        _, links, _ = item
        new_links.append(links)
    for old_link in latest:
        return old_link in new_links

def is_malformed(name):
    """Assertion for misformed deck titles"""
    return re.match(r"^\$[0-9]*\ \(.*\)$", name) or re.match(r"^[0-9]*\ TIX$", name)

def is_a_link(link):
    """Assertion for collecting deck links"""
    return re.match(r"^\?e=.*&d=.*&f=ST", link)

def should_be_skipped(rank):
    """Assertion for odd/extraneous cards, based on mtgtop8 formatting"""
    return rank in ("close", "Companion card")

def is_points(rank):
    """Assertion for identifying if an event is measured by points"""
    return re.match(r"^[0-9]*\ pts$", rank)

def is_rank(rank):
    """Assertion for identifying if an event is measured by rank"""
    return re.match(r"^[0-9]*-[0-9]*$", rank) or re.match("^[0-9]*$", rank)

def are_equal_length(*args):
    """Assertion for equal length lists to avoid data loss"""
    equal = True
    length1 = len(args[0])
    for arg in args:
        if len(arg) != length1:
            equal = False
    return equal

def check_new_players(players, currently_saved_players):
    """Looks at the players on the page and filters for only new players"""
    new_players = []
    for player in players:
        if player not in list(
            currently_saved_players["firstName"] + " "
            + currently_saved_players["lastName"]
        ):
            new_players.append(player)
    return [player.split(maxsplit=1) for player in new_players]
