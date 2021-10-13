===========
MTG Scraper
===========

The MTG Scraper is a simple tool that crawls through the tables of events found on mtgtop8.com for the standard format. It is meant as an easy way to store data on the event names, the cards played, how often those cards won in the latest Standard events.

The tool uses the Selenium package to crawl through each table on the website. Once it has all the links, a combination of requests and BeautifulSoup4 will look at each page and get exactly what is needed. All the data will be stored in a sqlite3 database file.

