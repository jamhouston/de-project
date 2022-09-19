import logging
import os
from json.decoder import JSONDecodeError

import urllib3
import yaml
from jsonstream import loads
from urllib3 import exceptions

EXTRACTOR_CONFIG_NAME = '_config_extractor.yaml'

class Extractor:
    def __init__(self, conn):
        try:
            with open(f'{os.path.dirname(__file__)}/{EXTRACTOR_CONFIG_NAME}', "r") as config:
                self.config_vars = yaml.safe_load(config)

                self.buffer_table_name = self.config_vars['BUFFER_TABLE_NAME']
                self.buffer_source_column = self.config_vars['BUFFER_SOURCE_COLUMN']
                self.buffer_target_column = self.config_vars['BUFFER_TARGET_COLUMN']

                self.schema_path = self.config_vars['SCHEMA_PATH']
                self.load_process_path = self.config_vars['LOAD_PROCESS_PATH']

        except FileNotFoundError as e:
            logging.error(f"Couldn't find configuration file")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Couldn't parse configuration file")
            raise
        except KeyError as e:
            logging.error(f"Couldn't find key {e.args[0]}")
            raise
        except Exception as e:
            logging.error(f"Unknown configuration file error: {type(e)}", e)
            raise

        self.conn = conn

    def get_data_from_url(self, path):
        try:
            http = urllib3.PoolManager()
            resp = http.request('GET', path)
            data = loads(resp.data.decode('utf-8'))
            # released back into the pool without manual intervention
            json_list = list(filter(lambda x: (x['event']['customer-id'] is not None), data))
            # the data comes nonchronologically
            logging.info(f'Retrieved JSON data from {path} successfully')
            return json_list
        except exceptions.HTTPError as e:
            logging.error(f"Couldn't connect to {path}")
            raise
        except JSONDecodeError as e:
            logging.error("Couldn't parse the response", e)
            raise
        except Exception as e:
            logging.error(f"Unknown connection error: {type(e)}", e)
            raise

    def get_data_from_file(self, path):
        try:
            with open(path, 'r') as file:
                json_data = loads(file.read())
                json_list = list(filter(lambda x: (x['event']['customer-id'] is not None), json_data))
            logging.info(f'Read JSON data from {path} successfully')
            return json_list
        except FileNotFoundError as e:
            logging.error(f"File not found at {path}")
            raise
        except JSONDecodeError as e:
            logging.error("Couldn't parse the file data", e)
            raise
        except Exception as e:
            logging.error(f"Unknown error: {type(e)}", e)
            raise

    def insert_into_buffer(self, data):

        def data_to_str(data):
            values_str = ''
            while data:
                row = data.pop()
                values_str += f'{row_to_str(row)}, '
            return values_str[:-2]

        def row_to_str(row):
            row.update(row['event'])
            row.pop('event', None)
            row_string = '('
            target_columns = self.buffer_source_column.split(',')
            for column in target_columns:
                if column in row.keys():
                    if isinstance(row[column], int):
                        row[column] = str(row[column])
                    else:
                        row[column] = f"'{row[column]}'"
                    row_string += str(row[column]) + ', '
                else: row_string += 'NULL, '
            return f'{row_string[:-2]})'    

        query = f'INSERT INTO {self.buffer_table_name}({self.buffer_target_column}) VALUES {data_to_str(data)};'
        self.conn.execute(query)
        logging.info(f'Data inserted into {self.buffer_table_name}')

    def execute(self, type_get, path):
        if type_get == 'PATH':
            data = self.get_data_from_file(path)
        elif type_get == 'URL':
            data = self.get_data_from_url(path)

        if len(data) == 0:
            logging.warning('Data is empty, aborting insert')
        else:
            self.conn.execute_from_file(self.schema_path)
            logging.info('Tables created')
            self.insert_into_buffer(data)
            self.conn.execute_from_file(self.load_process_path)
            logging.info("Data inserted into event and session_customer")
            self.conn.execute(f'truncate table {self.buffer_table_name};')
            logging.info("Buffer truncated")
