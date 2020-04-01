#! /usr/bin/python3

import boto3
import csv
import datetime
import json
import requests

from collections import OrderedDict
from io import BytesIO

STORE_IN_S3 = True

filters = [",", "County", "county", "Recovered", "Unassigned Location", "Wuhan", "Grand Princess Cruise Ship", "United States Virgin Islands"]

def lambda_handler(event, context):
    process()

def process():
    data_source_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"

    start = datetime.datetime.strptime("02-22-2020", "%m-%d-%Y")

    # Number of days from [1/22/20, today).
    days = abs((start - datetime.datetime.today()).days) - 1
    date_files = [(start + datetime.timedelta(days=x)).strftime("%m-%d-%Y.csv") for x in range(days)]

    # Retry 3 times if any request fails.
    csv_data = {}
    retries = 0
    success = False
    while not success and retries < 1:
        for d_file in date_files:
            response = requests.get("{}{}".format(data_source_url, d_file))
            if response.status_code == 200:
                csv_data[d_file[:-4]] = str(response.content.decode("utf-8-sig").encode("utf-8")).lstrip("b'")
                success = True
            else:
                retries += 1
                success = False
            print("{}> Success: {}".format(d_file, success))

            if not success:
                break

    options_data = []
    if success:
        totals = {}
        for cd in csv_data:
            reader = csv.DictReader(csv_data[cd].replace("\\r\\n", "\\n").split("\\n"))
            cases = 0
            deaths = 0
            for row in reader:
                if get_country(row) == "US":
                    state = get_state(row)
                    calc_totals(totals, row, state, cd)
                    calc_totals(totals, row, "US", cd)

        for key in totals:
            if not any(ff for ff in filters if ff in key):
                dates = []
                cases = []
                deaths = []
                rates = []
                for date in totals[key]:
                    dates.append(date)
                    cases.append(totals[key][date]["cases"])
                    deaths.append(totals[key][date]["deaths"])
                    rates.append(totals[key][date]["rate"])
                final_data = {
                    "title": "{} COVID-19 Graph".format(key),
                    "dates": dates,
                    "cases": cases,
                    "deaths": deaths,
                    "rates": rates
                }

                filename = "{}.json".format(key.replace(" ", "").lower())

                # We exclude US because it's the hard coded default.
                if key != "US":
                    options_data.append({"name": key, "dataset": filename})

                store("data/{}".format(filename), final_data)

        options_data.sort(key=lambda o: o["name"])
        store("data/options.json", options_data)

def store(filename, data):
    if STORE_IN_S3:
            store_in_s3(filename, data)
    else:
        store_local(filename, data)

def store_local(filename, data):
    success = False
    try:
        # filename = "data/{}.json".format(key)
        with open(filename, 'w') as f:
            f.write(json.dumps(data))
        success = True
    except Exception as e:
        print(e)
    print("Saved to {}> Success: {}".format(filename, success))

def store_in_s3(key, data):
    bucket = "chrisdima.io"
    extra_args = {"ACL": "public-read"}
    success = False
    try:
        s3 = boto3.client('s3')
        s3.upload_fileobj(
            BytesIO(json.dumps(data).encode("utf-8")),
            bucket,
            key,
            ExtraArgs=extra_args
        )
        success = True
    except Exception as e:
        print(e)
    print("upload s3://{}/{}({})> Success: {}".format(bucket, key, extra_args, success))

def calc_totals(totals, row, key, cd):
    totals.setdefault(key, {})
    totals[key].setdefault(cd, {"cases": 0, "deaths": 0})
    totals[key][cd]["cases"] += int(row["Confirmed"])
    totals[key][cd]["deaths"] += int(row["Deaths"]) if row["Deaths"] != "" else 0
    totals[key][cd]["rate"] = totals[key][cd]["deaths"]/totals[key][cd]["cases"]*100 if totals[key][cd]["deaths"] > 0 else 0

def get_country(row):
    if "Country/Region" in row:
        return row["Country/Region"]
    return row["Country_Region"]

def get_state(row):
    if "Province/State" in row:
        return row["Province/State"]
    return row["Province_State"]

if __name__ == "__main__":
    lambda_handler(None, None)