#! /usr/bin/python3

import datetime
# import requests

# Use this in Lambda
# from botocore.vendored import requests

def lambda_handler(event, context):
    pre_process()

def pre_process():
    # File format of archived data 03-28-2020.csv
    data_source = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/"

    base = datetime.datetime.today()
    date_list = [(base - datetime.timedelta(days=x)).strftime("%m-%d-%Y.csv") for x in range(10)]
    date_list.reverse()
    print(date_list)


if __name__ == "__main__":
    lambda_handler(None, None)