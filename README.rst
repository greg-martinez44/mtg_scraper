===========
MTG Scraper
===========

Abstract
========
The MTG Scraper is a simple tool that crawls through the tables of events found on mtgtop8.com for the standard format. It is meant as an easy way to store data on the event names, the cards played, how often those cards won in the latest Standard events.

The tool uses the Selenium package to crawl through each table on the website. Once it has all the links, a combination of requests and BeautifulSoup4 will look at each page and get exactly what is needed. All the data will be stored in a sqlite3 database file.

Functionality
=============
The program should:

Execute Scraper
---------------
A button executes the scraping function that grabs the event data from mtgtop8.com.

The scraper should also crawl through the new items in the list to get the deck lists for each event.

Display Results
---------------
A message appears that tells the user how many _new_ items were added to the sqlite database file.

* Grab the max id value before scraping
* After scraping, if the max id is larger than previously:
    - Find the difference to quantify how many items were added.
    - Display the event titles for the new events.

Visualize Data
--------------
The app should make use of a plotting library (seaborn or matplotlib) to build graphics to describe:
* Events per month
* Percentage by color
* Top played cards
* Bottom played cards
* Most "winning" cards
* Least "winning" cards
