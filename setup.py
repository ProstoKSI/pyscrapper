import os
from setuptools import setup, find_packages

from pyscrapper import VERSION, PROJECT


MODULE_NAME = 'pyscrapper'
PACKAGE_DATA = list()

def read( fname ):
    try:
        return open( os.path.join( os.path.dirname( __file__ ), fname ) ).read()
    except IOError:
        return ''


META_DATA = dict(
    name = PROJECT,
    version = VERSION,
    description = read('DESCRIPTION'),
    long_description = read('README.md'),
    license='MIT',

    author = "Illia Polosukhin",
    author_email = "ilblackdragon@gmail.com",

    url = "http://github.com/ProstoKSI/pyscrapper.git",

    packages = find_packages(),
    package_data = { '': PACKAGE_DATA, },

    install_requires = [ 'config', ],
)

if __name__ == "__main__":
    setup( **META_DATA )

