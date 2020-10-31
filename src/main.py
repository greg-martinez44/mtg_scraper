import csv

import time
from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    print(">>Enter main<<")
    result = scrape_data_from(URL)
    save(result)

def scrape_data_from(url):
    print(">>Opening scraper<<")
    result = []
    next_page = True
    page = 1
    with Scraper(url) as scraper:
        result = get_page(scraper)
        while next_page:
            print(">>While loop executes<<")
            page += 1
            scraper.execute("PageSubmit", page)
            time.sleep(2)
            result.extend(get_page(scraper))
            next_page = "Nav_PN_no" not in repr(scraper)
        return result

def get_page(scraper):
    events = get_events_from(scraper)
    result = get_links_to(events)
    time.sleep(2)
    return result

def get_events_from(scraper):
    print(">>Enter get_events_from<<")
    result = scraper.get_all_by(
        "xpath", 
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
    )
    return result

def get_links_to(events):
    print(">>Enter get_links_to<<")
    return [(event.text, event.get_attribute("href")) for event in events]

def save(links):
    print(">>Enter save<<")
    header = ['Event','Link']
    result = csv_from(links)
    with open("links.csv", 'w') as links_file:
        writer = csv.writer(links_file)
        writer.writerow(header)
        for event in result:
            writer.writerow(event)

def csv_from(links):
    return [(f'{name}', f'{event}') for name, event in links]

if __name__ == "__main__":
    main()
