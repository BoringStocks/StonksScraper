from src import app
from flask import render_template, request, send_file, Response
from flask_api import status
from .scraper import Scraper, retrieve_historical
import json
from datetime import datetime
import math


@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""

    return "Nothing to see here, try /ticker"


@app.route('/<ticker>')
def get_all(ticker):
    print(f'{ticker} requested at {datetime.utcnow()}')

    # Detect if json exists, create new json if none found
    try:
        # Unpack old json to parse time
        unpacked_json = open('data.json')
        data = json.load(unpacked_json)

        # Determine difference between old/new timestamps
        format = "%H:%M:%S"
        old_time = data['timestamp']
        new_time = (datetime.utcnow()).strftime(format)
        time_delta = datetime.strptime(
            new_time, format) - datetime.strptime(old_time, format)

        # Return new scrape if difference in stamps exceeds 5 secs or new index is requested
        if abs(time_delta.total_seconds()) >= 5 or data['symbol'] != ticker.upper():

            # return new current, write new data into json
            print('Returning new scrape')
            stock = Scraper(ticker)

            if not stock.page_content:
                return f'Stock index not found', status.HTTP_400_BAD_REQUEST

            stock.get_all()

            # Write new scrape to json
            new_unpacked_json = open('data.json')
            new_data = json.load(new_unpacked_json)

            return new_data

        else:
            # return old data if timestamp difference less than 5 secs
            print('Returning old scrape')
            return data

    except:
        # Run if no JSON found
        print('No JSON found, creating new JSON with requested index')
        stock = Scraper(ticker)

        if not stock.page_content:
            return f'Stock index not found', status.HTTP_400_BAD_REQUEST

        # Retrieve scrape data
        new_data = stock.get_all()

        # Write scrape to new json
        with open('data.json', 'w') as stock_json:
            json.dump(new_data, stock_json)

        return new_data


@app.route('/<ticker>/historical/max')
def get_historical_all(ticker):
    '''Retrieve all known historical data in 1 day increments for stock index'''

    todays_date_in_secs = math.ceil((datetime.today()).timestamp())
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker.upper()}?period1=0&period2={todays_date_in_secs}&interval=1d&events=history&includeAdjustedClose=true'
    print(url)
    data = retrieve_historical(url)

    if not data:
        return f'Stock index not found', status.HTTP_400_BAD_REQUEST

    return Response(json.dumps(data), mimetype='application/json')