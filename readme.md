# Metrics loader

## How to run

1. Activate the virtual environment inside the root folder:

```bash
$ python3 -m venv /Users/jamhouston/projects/de-assessment-jamhouston
$ source bin/activate
$ pip install -r requirements.txt
```

2. Check the DB connector config file `project/_config_connector.yaml`, in case you need to change any values:

```yaml
  DB_HOST: 'localhost'
  DB_PORT: 5432
  DB_NAME: 'postgres'
  DB_USER: 'postgres'
  DB_PASSWORD: 'secret'
```

2. Run a Postgresql container:

```bash
$ docker run -p 5432:5432 -d -e POSTGRES_PASSWORD=secret postgres:latest
```

If you used a different password or port in the config, change them in the command accordingly.

3. Run the data loader from a data set:

```bash
$ python3 -m project.loader.main --url 'https://storage.googleapis.com/xcc-de-assessment/events.json'
```

If you already have the dataset locally, you can specify a full path to the file with the `--path` argument:

```bash
$ python3 -m project.loader.main --path '/path/to/data/set.json'
```

After that, parsed and sessionised data will be put into the DB.  

6. Run the metrics web application:

```bash
$ export FLASK_APP=app.py
$ python3 -m project.app
```

It should write `Running on http://127.0.0.1:5000` in the logs.

## How to use

You can get the metrics in JSON from the `metrics/orders` endpoint. Use the host and port specified in the logs on startup:

```bash
$curl http://127.0.0.1:5000/metrics/orders

{
    "median_visits_before_order": ...
    "median_session_duration_minutes_before_order": ...
}
```