import argparse
import sys
import logging

from ..connector import *
from .extractor import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="""Please specify either path or URL""")

        self.parser.add_argument('--path',
                            type=str,
                            help='Path to the dataset')
        self.parser.add_argument('--url',
                            type=str,
                            help='URL of the dataset')

        self.args = self.parser.parse_args()
        self.path = self.args.path
        self.url = self.args.url

    def get_path(self):
        if self.path is None and self.url is None:
            logging.error('Specify either path or URL')
            sys.exit(-1)
        elif self.path is not None and self.url is not None:
            logging.error('You can only specify either path or URL')
            sys.exit(-1)
        elif self.path is not None:
            return ('PATH', self.path)
        else:
            return ('URL', self.url)


if __name__ == '__main__':
    type_get, path = ArgParser().get_path()
    try:
        with SQLConnector() as conn:
            extractor = Extractor(conn)
            extractor.execute(type_get, path)
    except Exception:
        sys.exit(-1)
    
    
