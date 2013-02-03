import sys
import re

from prettytable import PrettyTable

from pyscrapper import run_scrapper

def main():
    """
    Objective of this script is to grab all TV Shows from eztv and list urls and names of them
    """
 
    table = PrettyTable(["Name", "Url"])

    def do_show_page(url, content):
        val = re.findall("Show Information:? <b>([^<]+)</b>", content)
        if val:
            table.add_row([val[0], url])

    config = {
        "initial_urls": "http://eztv.it/",
        "follow_urls": [
            "^http://eztv.it/showlist/$",
            "^http://eztv.it/shows/\d+/[^/]+/$"
        ],
        "landing_urls": [
            ("^http://eztv.it/shows/\d+/[^/]+/$", do_show_page)
        ],
        "clear_history": True,
    }
    run_scrapper(config, enable_logging=True)

    print(table)

if __name__ == "__main__":
    main()

