import csv
import os
import sqlite3

import time
from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    print(">>Enter main<<")
    result = scrape_data_from(URL)
    save(result)

def scrape_data_from(url):
    result = []
    next_page = True
    page = 1
    with Scraper(url) as scraper:
        result = get_page(scraper)
        while next_page:
            page += 1
            scraper.execute("PageSubmit", page)
            time.sleep(2)
            result.extend(get_page(scraper))
            next_page = "Nav_PN_no" not in repr(scraper)
        return result

def get_page(scraper):
    events = get_events_from(scraper)
    dates = get_dates_from(scraper)
    result = get_info_for(events, dates)
    time.sleep(2)
    return result

def get_events_from(scraper):
    result = scraper.get_all_by(
        "xpath", 
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
    )
    return result

def get_dates_from(scraper):
    result = scraper.get_all_by(
        "xpath", 
        "//table[@class='Stable'][2]//tr[@class='hover_tr']//td[@class='S10']"
        )
    return result

def get_info_for(events, dates):
    return [(event.text, event.get_attribute("href"), date.text) for event, date in zip(events, dates)]

def save(data):
    result = union_events("links.db", data)

def union_events(db, data):
    conn = sqlite3.connect(os.path.abspath("dbs/links.db"))
    cursor = conn.cursor()
    for event in data:
        add_new_(cursor, event)
    conn.commit()
    conn.close()

def add_new(cursor, event):
    try:
        cursor.execute(
            """
            INSERT INTO event (name, link, date)
            VALUES (?, ?, ?)
            """, (event,)
            )
    except sqlite3.IntegrityError:
        pass


if __name__ == "__main__":
    main()
