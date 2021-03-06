"""Plotting the city street language summary."""
from __future__ import division
import matplotlib.pyplot as plt
import mplleaflet
import csv
import os
import urllib
import zipfile
import json

import street_languages

city_info_dict = {}
#city_info_dict['montreal'] = {'geofile': 'data/montreal_canada/test_montreal_canada-roads.geojson'}
city_info_dict['montreal'] = {'geofile': 'data/montreal_canada/montreal_canada-roads.geojson'}
city_info_dict['calgary'] = {'geofile': 'data/calgary_canada/calgary_canada-roads.geojson'}
city_info_dict['fredericton'] = {'geofile': 'data/fredericton_canada/fredericton_canada-roads.geojson'}
city_info_dict['halifax'] = {'geofile': 'data/halifax_canada/halifax_canada-roads.geojson'}
city_info_dict['hamilton'] = {'geofile': 'data/hamilton_canada/hamilton_canada-roads.geojson'}
city_info_dict['kamloops'] = {'geofile': 'data/kamloops_canada/kamloops_canada-roads.geojson'}
city_info_dict['mississauga'] = {'geofile': 'data/mississauga_canada/mississauga_canada-roads.geojson'}
city_info_dict['ottawa'] = {'geofile': 'data/ottawa_canada/ottawa_canada-roads.geojson'}
city_info_dict['quebec'] = {'geofile': 'data/quebec_canada/quebec_canada-roads.geojson'}
city_info_dict['trois-rivieres'] = {'geofile': 'data/trois-rivieres_canada/trois-rivieres_canada-roads.geojson'}
city_info_dict['toronto'] = {'geofile': 'data/toronto_canada/toronto_canada-roads.geojson'}
city_info_dict['winnipeg'] = {'geofile': 'data/winnipeg_canada/winnipeg_canada-roads.geojson'}
city_info_dict['saint-john'] = {'geofile': 'data/saint-john_canada/saint-john_canada-roads.geojson'}
city_info_dict['edmonton'] = {'geofile': 'data/edmonton_canada/edmonton_canada-roads.geojson'}

city_info_dict['hampton-roads'] = {'geofile': 'data/hampton-roads_virginia/hampton-roads_virginia-roads.geojson'}
city_info_dict['new-orleans'] = {'geofile': 'data/new-orleans_louisiana/new-orleans_louisiana-roads.geojson'}
city_info_dict['minneapolis-saint-paul'] = {'geofile': 'data/minneapolis-saint-paul_minnesota/minneapolis-saint-paul_minnesota-roads.geojson'}
city_info_dict['chicago'] = {'geofile': 'data/chicago_illinois/chicago_illinois-roads.geojson'}
city_info_dict['detroit'] = {'geofile': 'data/detroit_michigan/detroit_michigan-roads.geojson'}
city_info_dict['louisville'] = {'geofile': 'data/louisville_kentucky/louisville_kentucky-roads.geojson'}
city_info_dict['duluth'] = {'geofile': 'data/duluth_minnesota/duluth_minnesota-roads.geojson'}
city_info_dict['memphis'] = {'geofile': 'data/memphis_tennessee/memphis_tennessee-roads.geojson'}
city_info_dict['charlotte'] = {'geofile': 'data/charlotte_north-carolina/charlotte_north-carolina-roads.geojson'}
city_info_dict['new-york'] = {'geofile': 'data/new-york_new-york/new-york_new-york-roads.geojson'}


def download_data(basename):
    """Dowload the city geojson data from mapzen data.
    basename must be of the format: albany_new-york
    as seen on the mapzen metro extract page
    https://mapzen.com/metro-extracts/
    """
    # Set the names
    local_dir = 'data/'
    fname = '{}.imposm-geojson.zip'.format(basename)
    local_fname = os.path.join(local_dir, fname)
    url = 'https://s3.amazonaws.com/metro-extracts.mapzen.com/'
    url = os.path.join(url, fname)

    # download
    print('\ndownloading:\n{}'.format(fname))
    urllib.urlretrieve(url, local_fname)

    # extract
    with zipfile.ZipFile(local_fname) as zf:
        zf.extractall(os.path.join(local_dir, basename))
    # delete zip file
    os.remove(local_fname)

def update_city_csv(csvname, city_dict):
    """Appends the city stat csv with the give dictionary
    """
    csvnewline = city_dict['city']
    csvnewline += " {} {}".format(city_dict['english'], city_dict['french'])
    csvnewline += " {} {}".format(city_dict['longitude'], city_dict['latitude'])
    csvnewline += "\n"
    fcsv = open(csvname, 'a')
    print("\nAppending {} with line:\n{}".format(csvname, csvnewline))
    fcsv.write(csvnewline)


def get_city_stats_from_csv(cityname, csvfname):
    """Return language statistics from street."""
    with open(csvfname) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=' ')
        for row in reader:
            if row['city'] == cityname:
                return row
    raise ValueError


def get_city_stats(geofname, cityname='SomeCity', updatecsv=True):
    """Return languages statistics about the given city."""
    csvfname = 'city_stats/city_summary.csv'
    try:
        return get_city_stats_from_csv(cityname, csvfname)
    except ValueError:
        pass
    print("\n{} not in csv, info will be determined from data".format(cityname))
    city_info = street_languages.City(geofname, cityname)
    city_info.set_language_stats()
    info_dict = {}
    info_dict['english'] = city_info.get_fraction_language('en')
    info_dict['french'] = city_info.get_fraction_language('fr')
    longlat = city_info.get_city_longlat()
    info_dict['longitude'] = longlat[0]
    info_dict['latitude'] = longlat[1]
    info_dict['city'] = cityname
    if updatecsv:
        update_city_csv(csvfname, info_dict)
    return info_dict


def get_all_processed_cities(csvfname):
    """Return a list of all citis in the csv."""
    city_list = []
    with open(csvfname) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=' ')
        for row in reader:
            if row['city'] in city_list:
                print('\n!!!Warning: csv file has more than one {}\n'.format(row['city']))
            city_list.append(row['city'])
    return city_list


def locate_local_geofile(city):
    """Locating the geojson file
    search in the data/ subdirectory
    """
    data_dir = 'data/'
    similar_cities = [s for s in os.listdir(data_dir) if city in s]
    if len(similar_cities) == 1:
        return os.path.join(data_dir, similar_cities[0],
                            "{}-roads.geojson".format(similar_cities[0]))
    if len(similar_cities) > 1:
        print('!!Error: more than one possible choice for city:')
        print similar_cities
    raise ValueError

def plot_streets(cityname):
    """Plots the streets from a given city
    """
    try:
        geofname = city_info_dict[cityname]['geofile']
    except KeyError:
        geofname = locate_geofile(cityname)
    city = street_languages.City(geofname, cityname)

def get_all_north_american_cities(shortnames=False):
    """Return all north american cities available at mapzen."""
    city_json = 'mapzen_cities.json'
    city_dict = json.load(open(city_json))
    all_na_cities = city_dict['regions']['north_america']['cities'].keys()
    if not shortnames:
        return all_na_cities
    # Remove the trailing _* for short names
    short_names = []
    for ilong_name in all_na_cities:
        if ilong_name == 'grand-rapids-holland-muskegon_michigan':
            continue
        short_names.append(ilong_name.split('_')[0])
    return short_names


def download_and_get_geofile_name(city):
    """Download the imposm-geojson files from mapzen.

    It query a json file of all mapzen available files
    downloaded from:
    https://raw.githubusercontent.com/mapzen/metroextractor-cities/master/cities.json
    To avoid collisions, the city is only search in north america
    """
    all_cities = get_all_north_american_cities()
    potential_cities = [c for c in all_cities if city in c]
    if len(potential_cities)<1:
        raise ValueError
    if len(potential_cities)>1:
        print('\n\nWARNING: more than one city like {}:'.format(city))
        print(potential_cities)
        print('Using the first one: {}'.format(potential_cities[0]))
    download_data(potential_cities[0])


def get_geofilename(city, download=False):
    """Return the file containing the geojson info."""
    try:
        geofname = city_info_dict[city]['geofile']
        if not os.path.exists(geofname):
            print('Skipping city {}'.format(city))
            raise KeyError
        return geofname
    except KeyError:
        pass
    try:
        return locate_local_geofile(city)
    except ValueError:
        if download:
            download_and_get_geofile_name(city)
    return locate_local_geofile(city)


def plot_cities(city_list='all'):
    """Plotting cities from a list.

    if city_list = all, use all city in csv file
    """
    csvname = 'city_stats/city_summary.csv'

    if city_list == 'all':
        city_list = get_all_processed_cities(csvname)

    longitudes = []
    latitudes = []
    frac_fr = []
    frac_en = []
    fcsv = open(csvname, 'a')
    for icity in city_list:
        igeofname = get_geofilename(icity, True)
        icity_info = get_city_stats(igeofname, icity)
        istr_en = float(icity_info['english'])
        istr_fr = float(icity_info['french'])
        ilong = icity_info['longitude']
        ilat = icity_info['latitude']
        longitudes.append(ilong)
        latitudes.append(ilat)
        frac_en.append(istr_en)
        frac_fr.append(istr_fr)
    for ilong, ilat, ifr, ien in zip(longitudes, latitudes, frac_fr, frac_en):
        imaxmkr = max(ifr, ien)
        imkrfactor = 30/imaxmkr
        plt.plot(ilong, ilat, 'ro', markeredgecolor='r', ms=int(imkrfactor*ien), alpha=0.35)
        plt.plot(ilong, ilat, 'bo', markeredgecolor='b', ms=int(imkrfactor*ifr), alpha=0.35)
    mplleaflet.show()
    raw_input('press enter when finished...')

if __name__ == "__main__":
    #citylist = city_info_dict.keys()
    #plot_cities(['montreal', ])
    #plot_cities(['new-york',])
    #plot_cities(['vancouver', 'victoria', 'windsor'])
    plot_cities(get_all_north_american_cities(True))
    #print get_all_north_american_cities(True)
