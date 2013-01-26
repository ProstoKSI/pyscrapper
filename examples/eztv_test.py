import sys
import re
import logging

from prettytable import PrettyTable

from pyscrapper import PyScrapper


def main():
    """
    Objective of this script is to grab all TV Shows from eztv and list urls and names of them
    """
 
    table = PrettyTable(["Name", "Url"])

    def do_show_page(url, content):
        val = re.findall("Show Information:? <b>([^<]+)</b>", content)
        if val:
            table.add_row([val[0], url])

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    config = {
        "initial_urls": "http://eztv.it/",
        "logger": logging,
        "follow_urls": [
            "^http://eztv.it/showlist/$",
            "^http://eztv.it/shows/\d+/[^/]+/$"
        ],
        "landing_urls": [
            ("^http://eztv.it/shows/\d+/[^/]+/$", do_show_page)
        ],
        "clear_history": True,
    }
    scrapper = PyScrapper(**config)
    scrapper.run()

    print(table)

if __name__ == "__main__":
    main()

