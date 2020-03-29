#! /usr/bin/python3

import boto3
import csv
import datetime
import json
import requests

from io import BytesIO

# Use this in Lambda
# from botocore.vendored import requests

def lambda_handler(event, context):
    process()

def process():
    data_source_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"

    start = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y")

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

    if success:
        data = {
            "title": "US COVID-19 Data",
            "dates": [],
            "cases": [],
            "deaths": [],
            "rates": []
        }

        for cd in csv_data:
            reader = csv.DictReader(csv_data[cd].replace("\\r\\n", "\\n").split("\\n"))
            cases = 0
            deaths = 0
            for row in reader:
                if get_country(row) == "US":
                    cases += int(row["Confirmed"])
                    deaths += int(row["Deaths"]) if row["Deaths"] != "" else 0

            data["dates"].append(cd)
            data["cases"].append(cases)
            data["deaths"].append(deaths)
            data["rates"].append((deaths/cases * 100))

        bucket = "chrisdima.io"
        key = "data/us.json"
        extra_args = {"ACL": "public-read"}
        upload_success = False
        try:
            s3 = boto3.client('s3')
            s3.upload_fileobj(
                BytesIO(json.dumps(data).encode("utf-8")),
                bucket,
                key,
                ExtraArgs=extra_args
            )
            upload_success = True
        except Exception as e:
            print(e)
        print("upload s3://{}/{}({})> Success: {}".format(bucket, key, extra_args, upload_success))

def get_country(row):
    if "Country/Region" in row:
        return row["Country/Region"]
    return row["Country_Region"]

if __name__ == "__main__":
    lambda_handler(None, None)