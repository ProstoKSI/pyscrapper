pyscrapper
==========

Python light-weighted and Redis-back scrapper for web-sites

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

    from pyscrapper import PyScrapper

    scrapper = PyScrapper(
        initial_urls=["http://url/to/scrap/"],
        timeout=1
    )
    scrapper.run()

    or

    from pyscrapper import run_scrapper

    
    config = {
        'initial_urls': ["http://url/to/scrap/"],
        'timeout': 1,
    }
    run_scrapper(config, enable_logging=True)

For more detailed usage look at examples/eztv_test.py example.

License
-------

Copyright (C) 2013 Illia Polosukhin
This program is licensed under the MIT License (see LICENSE)

