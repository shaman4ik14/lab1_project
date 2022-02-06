"""PROGRAM FOR WORKING AND CREATING MAP WITH DATA"""
import argparse
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
import math

parser = argparse.ArgumentParser()
parser.add_argument('year', type=str)
parser.add_argument('latitude', type=float)
parser.add_argument('longitude', type=float)
parser.add_argument('path_to_dataset', type=str)
args = parser.parse_args()

data = set()
with open(args.path_to_dataset, 'r', encoding='utf-8', errors='ignore') as read_file:
    count = 0
    for lines in read_file:
        count += 1
        if 15 <= count:
            pos = lines.index('(')
            year = lines[pos + 1: pos + 5]
            if year == args.year:
                name = lines[:pos + 1].split(' (')[0]
                location = lines[pos + 6:]
                if ')}' in location:
                    location = location.split(')}')[1]
                coord = 0
                while location[coord] in ' \t':
                    coord += 1
                location = location[coord:]
                while True:
                    if location[-1:].isalpha() or ')' in location[-1:]:
                        break
                    else:
                        location = location.rstrip('\n')
                        location = location.rstrip('\t')
                if '\t' in location:
                    location = location.replace('\t', '')
                if '(' in location:
                    location_pos = location.index('(')
                    location = location[:location_pos]
                data.add((name, location))
        if count > 3000 or len(data) > 250:
            break
lat = args.latitude
lon = args.longitude

map = folium.Map(location=[lat, lon], zoom_start=8, tiles="Stamen Toner")
data_with_coord = dict()

geolocator = Nominatim(user_agent="user_agent")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
for point in data:
    try:
        location = geolocator.geocode(point[1])
        current_coord = (location.latitude, location.longitude)
        data_with_coord[current_coord] = data_with_coord.get(current_coord, []) + [point[0], point[1]]
    except:
        pass


def calculate_haversine_dist(lat_0, lon_0, lat_1, lon_1):
    """
    Calculate haversine between 2 coordinates
    :param lat_0: latitude 1
    :param lon_0: longitude 1
    :param lat_1: latitude 2
    :param lon_1: longitude 2
    :return: Distance
    >>> calculate_haversine_dist(50.1, 43.1, 34.5, -23.1)
    2030850.167038123
    """

    r = 6400000
    first_part = (math.sin((lat_0-lat_1)/2) ** 2)
    second_part = (math.cos(lat_0) * math.cos(lat_1) * (math.sin((lon_0-lon_1)/2) ** 2))
    under_sqrt = first_part + second_part
    local_sqrt = under_sqrt ** 0.5
    next_part = math.asin(local_sqrt)
    result = 2 * r * next_part
    return result


info_about_coordinate = [(k, v) for k, v in data_with_coord.items()]
sorted_info = sorted(info_about_coordinate, key=lambda x: calculate_haversine_dist(lat, lon, x[0][0], x[0][1]))
points_data = sorted_info[:10]

html = """<h4>Films information:</h4>
Year: {}<br>
Film name: {}<br>
Place: {}
"""
fg = folium.FeatureGroup(name=year)
for elements in points_data:
    iframe = folium.IFrame(html=html.format(year, elements[1][0], elements[1][1]),
                           width=300, height=100)
    fg.add_child(folium.Marker(location=[elements[0][0], elements[0][1]],
                               popup=folium.Popup(iframe),
                               icon=folium.Icon(color='red')))

fg1 = folium.FeatureGroup(name='additional information')
fg1.add_child(folium.CircleMarker(location=[lat, lon], radius=10,
                                  popup='Start Point', fill_color='green',
                                  color='blue', fill_opacity=0.8))
fg1.add_child(folium.CircleMarker(location=[lat, lon], radius=50,
                                  popup='Start Point',
                                  color='blue', fill_opacity=0.8))

fg1.add_child(folium.CircleMarker(location=[49.817545, 24.023932], radius=10,
                                  popup='UCU Campus', fill_color='orange',
                                  color='yellow', fill_opacity=0.8))


map.add_child(fg)
map.add_child(fg1)
map.add_child(folium.LayerControl())
map.save('map.html')
