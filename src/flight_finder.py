import requests
import json
import datetime
import sqlite3
import time
from urllib.parse import urlencode
from os import path


db = sqlite3.connect('my_data.sqlite3')


def create_schema():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE if not exists trip (
            key text,
            bag_limit integer,
            bag_price integer,
            city_from text,
            city_to text,
            country_from text,
            country_to text,
            departure_time integer,
            flight_duration real,
            airport_change boolean,
            price integer,
            return_duration real
        );
    """)

    cursor.execute("""
            CREATE TABLE if not exists flight (
            key text,
            airline_key text,
            trip_key text,
            arrival_time integer,
            city_from text,
            city_to text,
            departure_time integer,
            airport_code_from text,
            airport_code_to text
        );
    """)

    cursor.execute("""
        CREATE TABLE if not exists airline (
            key text,
            airline_name text
        );

    """)
    db.commit()


def api_call(fly_from, fly_to, leave_date_from, leave_date_to, return_date_from, return_date_to, max_fly_duration, max_stopovers, currency = 'USD', adults = 1) :
    # requests.get(" https://api.skypicker.com/flights?flyFrom=PDX&to=LAX&dateFrom=01/04/2019&dateTo=07/04/2019&d=picky")
    params = {
        'flyFrom': fly_from,
        'to': fly_to,
        'dateFrom': leave_date_from.strftime('%d/%m/%Y'),
        'dateTo': leave_date_to.strftime('%d/%m/%Y'),
        'return_from': return_date_from.strftime('%d/%m/%Y'),
        'return_to': return_date_to.strftime('%d/%m/%Y'),
        'max_fly_duration': int(max_fly_duration.total_seconds() / 3600),
        'max_stopovers': max_stopovers,
        'curr': currency,
        'adults': adults,
        'partner': 'picky'
    }
    response = requests.get("https://api.skypicker.com/flights?" + urlencode(params))

    return response.json()


def write_to_file(data, file_path):
    file = open(path.expanduser(file_path), 'w')
    file.write(json.dumps(data['data'], sort_keys=True, indent=4))
    file.close()


def main():
    create_schema()

    response = api_call(
        "PDX",
        "SFO",
        datetime.datetime(2019, 5, 10),
        datetime.datetime(2019, 5, 10),
        datetime.datetime(2019, 5, 19),
        datetime.datetime(2019, 5, 19),
        datetime.timedelta(hours=3),
        0,

    )

    cursor = db.cursor()

    for trip in response['data']:
        print(json.dumps(trip, indent=4, sort_keys=True))

        cursor.execute(
            "DELETE FROM trip WHERE key = ?",
            (trip['id'], )
        )
        cursor.execute(
            "DELETE FROM flight WHERE trip_key = ?",
            (trip['id'], )
        )

        print("Inserting record for {trip}".format(trip=trip['id']))
        cursor.execute("""
            INSERT INTO trip (
                key,
                bag_limit,
                bag_price,
                city_from
            ) VALUES (
                ?,
                ?,
                ?,
                ?
            )
        """, (
            trip['id'],
            trip['baglimit'].get('hold_weight'),
            trip['bags_price'].get('1', 0) * 100,
            trip['cityFrom']
        ))

        for flight in trip["route"] :
            cursor.execute("""
                INSERT INTO flight (
                    key,
                    trip_key,
                    arrival_time,
                    city_from,
                    city_to,
                    departure_time,
                    airport_code_from,
                    airport_code_to
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
            """, (
                flight['id'],
                trip['id'],
                flight['aTime'],
                flight['cityFrom'],
                flight['cityTo'],
                flight['dTime'],
                flight['flyFrom'],
                flight['flyTo']
            ))

    db.commit()
if __name__ == '__main__':
    main()