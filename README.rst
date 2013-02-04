PyScrapper
==========

Light-weighted and with Redis backend scrapper for web-sites written on Python

.. contents::

Requirements
-------------

- python >= 2.5 (python 3.x supported as well)
- pip >= 0.8
- redis >= 2.7 (Redis Python Client) 

Installation
------------

**PyScrapper** should be installed using pip: ::

    pip install git+git://github.com/ProstoKsi/pyscrapper.git


Use pyscrapper
------------

Example of usage PyScrapper class: ::

    from pyscrapper.scrapper import PyScrapper

    scrapper = PyScrapper(
        initial_urls=["http://url/to/scrap/"],
        timeout=1
    )
    scrapper.run()

or using run_scrapper shortcut: ::

    from pyscrapper.scrapper import run_scrapper

    def do_show_page(url, content):
        """
        Parse content and store info in variable or database
        """
        pass
    
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
        "timeout": 1,
    }
    run_scrapper(config, enable_logging=True)

For more detailed usage look at examples/eztv_test.py example.

License
-------

Copyright (C) 2013 Illia Polosukhin.
This program is licensed under the MIT License (see LICENSE)

