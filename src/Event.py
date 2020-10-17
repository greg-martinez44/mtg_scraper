from bs4 import BeautifulSoup

class Event:

    def __init__(
        self,
        page_source
        ):
        self.html = BeautifulSoup(page_source)

