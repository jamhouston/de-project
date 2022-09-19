import psycopg2
import yaml
import logging
import os

CONNECTION_TIMEOUT = 5
CONNECTOR_CONFIG_NAME = '_config_connector.yaml'

class SQLConnector:
    def __init__(self):
        # TODO: Extract config init logic
        try:
            with open(f'{os.path.dirname(__file__)}/{CONNECTOR_CONFIG_NAME}', "r") as config:
                self.config_vars = yaml.safe_load(config)

                self.host = self.config_vars['DB_HOST']
                self.port = self.config_vars['DB_PORT']
                self.dbname = self.config_vars['DB_NAME']
                self.user = self.config_vars['DB_USER']
                self.password = self.config_vars['DB_PASSWORD']

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

        try:
            self.conn = psycopg2.connect(host=self.host,
                                        port=self.port,
                                        dbname=self.dbname,
                                        user=self.user,
                                        password=self.password,
                                        connect_timeout=CONNECTION_TIMEOUT)
        except psycopg2.OperationalError:
            logging.error(f"Couldn't connect to the server after {CONNECTION_TIMEOUT} seconds")
            raise
        except Exception as e:
            logging.error(f"Unknown SQL connection error: {type(e)}", e)
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def execute(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            logging.error(f"SQL query error: {type(e)}", e)
            raise
        
    def execute_from_file(self, query, fetch_results = False):
        try:
            cursor = self.conn.cursor()
            path = f'{os.path.dirname(__file__)}/{query}'
            with open(path, "r") as file:
                query = file.read()
                cursor.execute(query)
                if fetch_results:
                    res = cursor.fetchall()
                    self.conn.commit()
                    return res
                else:
                    self.conn.commit()
                    return
        except Exception as e:
            logging.error(f"SQL query error: {type(e)}", e)
            raise
