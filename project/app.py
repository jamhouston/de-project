from flask import Flask, jsonify, abort
import logging
from project.connector import SQLConnector

class Metrics:
    def __init__(self, conn):
        self.conn = conn

    def get_median_visits(self):
        path_query = 'sql/median_visit.sql'
        return self.conn.execute_from_file(path_query, fetch_results = True)[0][0]

    def get_median_duration(self):
        path_query = 'sql/median_duration.sql'
        return self.conn.execute_from_file(path_query, fetch_results = True)[0][0]

app = Flask(__name__)

@app.route('/metrics/orders', methods =['GET'])
def metrics():
    with SQLConnector() as conn:
        metrics = Metrics(conn)
        median_visits = metrics.get_median_visits()
        get_median_duration = metrics.get_median_duration()
        res = jsonify(median_visits_before_order=median_visits,
                    median_session_duration_minutes_before_order=get_median_duration)
        return res, 200


@app.errorhandler(Exception)
def internal_error(e):
    logging.error(e, e.args)
    resp = jsonify(error='Internal error')
    return resp, 500

if __name__ == '__main__':
    app.run()
