import csv
from src.Scraper import Scraper

def main():
    pass

def get_events(url):
    with Scraper(url) as scraper:
        result = scraper.get_all_by(
            "xpath", 
            "//table[@class='Stable'][2]//tr[@class='hover_tr']//a"
        )
        return result
