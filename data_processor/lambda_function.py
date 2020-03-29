#! /usr/bin/python3

import csv
import datetime
import json
import requests

# Use this in Lambda
# from botocore.vendored import requests

def lambda_handler(event, context):
    process()
    # process_time_series()

def process():
    # File format of archived data 03-28-2020.csv
    # data_source_url = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/"
    data_source_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"

    start = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y")

    # Number of days from [1/22/20, today).
    days = abs((start - datetime.datetime.today()).days) - 1
    date_files = [(start + datetime.timedelta(days=x)).strftime("%m-%d-%Y.csv") for x in range(days)]

    # Retry 3 times if any request fails.
    csv_data = {}
    retries = 0
    success = False
    while not success and retries < 3:
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
                # pass
        data["dates"].append(cd)
        data["cases"].append(cases)
        data["deaths"].append(deaths)
        data["rates"].append((deaths/cases * 100))

    with open("../data/us.json", "w") as f:
        f.write(json.dumps(data))

    print(len(data["cases"]))
    print(len(data["deaths"]))
    print(len(data["rates"]))
    print(len(data["dates"]))
    print(len(date_files))

# Only has country granularity.
def process_time_series():
    SOURCE_CASES = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

    start = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y")

    # Number of days from [1/22/20, today).
    days = abs((start - datetime.datetime.today()).days) - 1
    dates = [(start + datetime.timedelta(days=x)).strftime("%-m/%-d/%y") for x in range(days)]

    response = requests.get(SOURCE_CASES)
    if response.status_code == 200:
        csv_data = str(response.content.decode("utf-8-sig").encode("utf-8")).lstrip("b'")
        reader = csv.DictReader(csv_data.replace("\\r\\n", "\\n").split("\\n"))
        print(reader.fieldnames)
        total = 0
        cases = []
        for row in reader:
            if row["Country/Region"] == "US":
                for date in dates:
                    total = int(row[date])
                    cases.append(total)
            pass
        print(total)

def get_country(row):
    if "Country/Region" in row:
        return row["Country/Region"]
    return row["Country_Region"]

if __name__ == "__main__":
    lambda_handler(None, None)