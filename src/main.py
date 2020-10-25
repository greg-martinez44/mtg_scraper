from src.Scraper import Scraper

URL = "https://www.mtgtop8.com/format?f=ST"

def main():
    return get_event_links(URL)

def get_event_links(URL):
    with Scraper(URL) as scraper:
        result = scraper.get_all_by("xpath", "//table[@class='Stable'][2]//tr[@class='hover_tr']//a")
    return result
