#!/usr/bin/env python3
""" Create tz database links for major metropolian areas that don't exist in the IANA db

eV Quirk
"""

import unicodedata

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from tzwhere import tzwhere
import sys


def parse_majorcities(soup, geocoder):
    locations_with_city = []
    table = soup.find('table', {'class': "sortable wikitable mw-datatable"})
    if table is None:
        return None

    for row in table.findAll('tr'):
        columns = row.findAll('td')
        if columns:
            city = columns[0].find('a').text
            country = columns[1].findAll('a')[1].text
            location = geocoder.geocode(f"{city}, {country}")
            locations_with_city.append([location, city, country])

    return locations_with_city


def parse_tz_db_time_zones(soup):
    locations_with_city = []
    table = soup.findAll('table', {'class': "wikitable sortable"})[0]
    if table is None:
        return None

    tbody = table.find('tbody')
    for row in tbody.findAll('tr'):
        columns = row.findAll('td')
        if not columns:
            continue

        tz_db_name = columns[1].find('a').text
        try:
            region, city = tz_db_name.split('/')
        except ValueError:
            continue

        if city and columns:
            locations_with_city.append([None, city, region])

    return locations_with_city


def main(input_file="vendor/wikipedia/majorcities.html"):
    print(f"Parsing {input_file}\r\n")

    geocoder = Nominatim(user_agent="utz", timeout=30)
    tz = tzwhere.tzwhere()
    links = []

    with open(input_file) as f:
        soup = BeautifulSoup(f, features="html.parser")
        locations_with_city = parse_majorcities(soup, geocoder)
        if locations_with_city is None:
            f.seek(0)
            locations_with_city = parse_tz_db_time_zones(soup)

    if locations_with_city is None:
        print("No data available, parsers might have failed")
        return

    for (location, city, region) in locations_with_city:
        if not location:
            location = geocoder.geocode(city)  # try searching for just the city
        if location:
            zone = tz.tzNameAt(location.latitude, location.longitude)
            if zone:
                city = unicodedata.normalize('NFD', city).encode(
                    'ascii', 'ignore').decode('ascii')
                city = city.replace(' ', '_')
                city = city.replace('+', 'p').replace('-', 'm')
                if zone.split('/')[-1] not in city:
                    alias = zone.split('/')[:-1]
                    alias.append(city)
                    links.append(('Link', zone, '/'.join(alias)))
                else:
                    print(f"{city}, {region} already present as {zone}")
            else:
                print(f"couldn't find zone for: {city}, {region}")
        else:
            print(f"couldn't find location for: {city}, {region}")

    with open('majorcities', 'w') as f:
        f.write('\n'.join(['\t'.join(entry) for entry in links]))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
