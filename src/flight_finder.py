import requests
import json
import datetime
from urllib.parse import urlencode
from os import path

def api_call(fly_from, fly_to, leave_date_from, leave_date_to, return_date_from, return_date_to, max_fly_duration, max_stopovers, currency = 'USD', adults = 1) :
    # requests.get(" https://api.skypicker.com/flights?flyFrom=PDX&to=LAX&dateFrom=01/04/2019&dateTo=07/04/2019&d=picky")
    params = {
        'flyFrom' : fly_from,
        'to' : fly_to,
        'dateFrom' : leave_date_from.strftime('%d/%m/%Y'),
        'dateTo' : leave_date_to.strftime('%d/%m/%Y'),
        'return_from' : return_date_from.strftime('%d/%m/%Y'),
        'return_to' : return_date_to.strftime('%d/%m/%Y'),
        'max_fly_duration' : int(max_fly_duration.total_seconds() / 3600),
        'max_stopovers' : max_stopovers,
        'curr' : currency,
        'adults' : adults,
        'partner' : 'picky'
    }
    response = requests.get("https://api.skypicker.com/flights?" + urlencode(params))

    return response.json()

def write_to_file(data, file_path) :
    file = open(path.expanduser(file_path),'w')
    file.write(json.dumps(data['data'], sort_keys = True, indent=4))
    file.close()
