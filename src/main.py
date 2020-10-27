import csv
from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    events = get_events_from(URL)
    links = get_links_from(events)
    save(links)


def get_links_from(events):
    return [(event.text, event.get_attribute("href")) for event in events]

def save(links):
    result = ["Event,Link"].extend(["{},{}\r\n".format(name, event) for name, event in links])
    with csv.writer("links.csv") as writer:
        writer.writerows(result)

def get_events_from(url):
    with Scraper(url) as scraper:
        result = scraper.get_all_by(
            "xpath", 
            "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
        )
        return result
