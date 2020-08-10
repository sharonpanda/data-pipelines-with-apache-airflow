import os

import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

taxi_zones = {
    1: "Newark Airport",
    2: "Jamaica Bay",
    3: "Allerton/Pelham Gardens",
    4: "Alphabet City",
    5: "Arden Heights",
    6: "Arrochar/Fort Wadsworth",
    7: "Astoria",
    8: "Astoria Park",
    9: "Auburndale",
    10: "Baisley Park",
    11: "Bath Beach",
    12: "Battery Park",
    13: "Battery Park City",
    18: "Bedford Park",
    14: "Bay Ridge",
    15: "Bay Terrace/Fort Totten",
    16: "Bayside",
    17: "Bedford",
    19: "Bellerose",
    20: "Belmont",
    21: "Bensonhurst East",
    22: "Bensonhurst West",
    23: "Bloomfield/Emerson Hill",
    24: "Bloomingdale",
    25: "Boerum Hill",
    26: "Borough Park",
    27: "Breezy Point/Fort Tilden/Riis Beach",
    28: "Briarwood/Jamaica Hills",
    33: "Brooklyn Heights",
    29: "Brighton Beach",
    30: "Broad Channel",
    31: "Bronx Park",
    32: "Bronxdale",
    34: "Brooklyn Navy Yard",
    35: "Brownsville",
    36: "Bushwick North",
    37: "Bushwick South",
    38: "Cambria Heights",
    39: "Canarsie",
    40: "Carroll Gardens",
    41: "Central Harlem",
    42: "Central Harlem North",
    43: "Central Park",
    44: "Charleston/Tottenville",
    45: "Chinatown",
    46: "City Island",
    47: "Claremont/Bathgate",
    48: "Clinton East",
    49: "Clinton Hill",
    50: "Clinton West",
    51: "Co-Op City",
    52: "Cobble Hill",
    53: "College Point",
    54: "Columbia Street",
    55: "Coney Island",
    56: "Corona",
    58: "Country Club",
    59: "Crotona Park",
    60: "Crotona Park East",
    61: "Crown Heights North",
    62: "Crown Heights South",
    63: "Cypress Hills",
    64: "Douglaston",
    65: "Downtown Brooklyn/MetroTech",
    66: "DUMBO/Vinegar Hill",
    67: "Dyker Heights",
    68: "East Chelsea",
    69: "East Concourse/Concourse Village",
    72: "East Flatbush/Remsen Village",
    73: "East Flushing",
    70: "East Elmhurst",
    71: "East Flatbush/Farragut",
    74: "East Harlem North",
    75: "East Harlem South",
    76: "East New York",
    77: "East New York/Pennsylvania Avenue",
    78: "East Tremont",
    79: "East Village",
    80: "East Williamsburg",
    85: "Erasmus",
    86: "Far Rockaway",
    81: "Eastchester",
    87: "Financial District North",
    82: "Elmhurst",
    83: "Elmhurst/Maspeth",
    84: "Eltingville/Annadale/Prince's Bay",
    88: "Financial District South",
    89: "Flatbush/Ditmas Park",
    90: "Flatiron",
    125: "Hudson Sq",
    91: "Flatlands",
    92: "Flushing",
    93: "Flushing Meadows-Corona Park",
    94: "Fordham South",
    95: "Forest Hills",
    96: "Forest Park/Highland Park",
    97: "Fort Greene",
    98: "Fresh Meadows",
    99: "Freshkills Park",
    100: "Garment District",
    101: "Glen Oaks",
    102: "Glendale",
    103: "Governor's Island/Ellis Island/Liberty Island",
    106: "Gowanus",
    107: "Gramercy",
    108: "Gravesend",
    109: "Great Kills",
    110: "Great Kills Park",
    111: "Green-Wood Cemetery",
    112: "Greenpoint",
    113: "Greenwich Village North",
    114: "Greenwich Village South",
    115: "Grymes Hill/Clifton",
    116: "Hamilton Heights",
    117: "Hammels/Arverne",
    118: "Heartland Village/Todt Hill",
    119: "Highbridge",
    120: "Highbridge Park",
    149: "Madison",
    150: "Manhattan Beach",
    121: "Hillcrest/Pomonok",
    122: "Hollis",
    123: "Homecrest",
    124: "Howard Beach",
    126: "Hunts Point",
    127: "Inwood",
    128: "Inwood Hill Park",
    129: "Jackson Heights",
    134: "Kew Gardens",
    151: "Manhattan Valley",
    130: "Jamaica",
    139: "Laurelton",
    131: "Jamaica Estates",
    132: "JFK Airport",
    133: "Kensington",
    140: "Lenox Hill East",
    135: "Kew Gardens Hills",
    136: "Kingsbridge Heights",
    137: "Kips Bay",
    141: "Lenox Hill West",
    142: "Lincoln Square East",
    152: "Manhattanville",
    138: "LaGuardia Airport",
    143: "Lincoln Square West",
    144: "Little Italy/NoLiTa",
    145: "Long Island City/Hunters Point",
    146: "Long Island City/Queens Plaza",
    147: "Longwood",
    148: "Lower East Side",
    153: "Marble Hill",
    154: "Marine Park/Floyd Bennett Field",
    155: "Marine Park/Mill Basin",
    156: "Mariners Harbor",
    159: "Melrose South",
    157: "Maspeth",
    158: "Meatpacking/West Village West",
    160: "Middle Village",
    161: "Midtown Center",
    162: "Midtown East",
    163: "Midtown North",
    164: "Midtown South",
    170: "Murray Hill",
    165: "Midwood",
    166: "Morningside Heights",
    167: "Morrisania/Melrose",
    178: "Ocean Parkway South",
    168: "Mott Haven/Port Morris",
    169: "Mount Hope",
    171: "Murray Hill-Queens",
    172: "New Dorp/Midland Beach",
    173: "North Corona",
    174: "Norwood",
    175: "Oakland Gardens",
    179: "Old Astoria",
    176: "Oakwood",
    177: "Ocean Hill",
    180: "Ozone Park",
    181: "Park Slope",
    182: "Parkchester",
    183: "Pelham Bay",
    184: "Pelham Bay Park",
    185: "Pelham Parkway",
    186: "Penn Station/Madison Sq West",
    189: "Prospect Heights",
    190: "Prospect Park",
    187: "Port Richmond",
    188: "Prospect-Lefferts Gardens",
    191: "Queens Village",
    192: "Queensboro Hill",
    193: "Queensbridge/Ravenswood",
    194: "Randalls Island",
    196: "Rego Park",
    195: "Red Hook",
    203: "Rosedale",
    197: "Richmond Hill",
    198: "Ridgewood",
    199: "Rikers Island",
    212: "Soundview/Bruckner",
    213: "Soundview/Castle Hill",
    200: "Riverdale/North Riverdale/Fieldston",
    204: "Rossville/Woodrow",
    201: "Rockaway Park",
    202: "Roosevelt Island",
    205: "Saint Albans",
    206: "Saint George/New Brighton",
    207: "Saint Michaels Cemetery/Woodside",
    208: "Schuylerville/Edgewater Park",
    209: "Seaport",
    210: "Sheepshead Bay",
    211: "SoHo",
    214: "South Beach/Dongan Hills",
    215: "South Jamaica",
    216: "South Ozone Park",
    217: "South Williamsburg",
    218: "Springfield Gardens North",
    219: "Springfield Gardens South",
    225: "Stuyvesant Heights",
    220: "Spuyten Duyvil/Kingsbridge",
    224: "Stuy Town/Peter Cooper Village",
    226: "Sunnyside",
    221: "Stapleton",
    222: "Starrett City",
    223: "Steinway",
    227: "Sunset Park East",
    228: "Sunset Park West",
    229: "Sutton Place/Turtle Bay North",
    230: "Times Sq/Theatre District",
    231: "TriBeCa/Civic Center",
    239: "Upper West Side South",
    232: "Two Bridges/Seward Park",
    233: "UN/Turtle Bay South",
    234: "Union Sq",
    235: "University Heights/Morris Heights",
    236: "Upper East Side North",
    237: "Upper East Side South",
    238: "Upper West Side North",
    240: "Van Cortlandt Park",
    241: "Van Cortlandt Village",
    258: "Woodhaven",
    242: "Van Nest/Morris Park",
    245: "West Brighton",
    263: "Yorkville West",
    243: "Washington Heights North",
    244: "Washington Heights South",
    253: "Willets Point",
    246: "West Chelsea/Hudson Yards",
    247: "West Concourse",
    248: "West Farms/Bronx River",
    249: "West Village",
    257: "Windsor Terrace",
    250: "Westchester Village/Unionport",
    251: "Westerleigh",
    252: "Whitestone",
    254: "Williamsbridge/Olinville",
    255: "Williamsburg (North Side)",
    256: "Williamsburg (South Side)",
    259: "Woodlawn/Wakefield",
    260: "Woodside",
    261: "World Trade Center",
    262: "Yorkville East",
}

weekdays = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}


@app.route("/")
def index():
    conn = psycopg2.connect(
        database=os.environ["POSTGRES_DATABASE"],
        user=os.environ["POSTGRES_USERNAME"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
    )
    cursor = conn.cursor()
    cursor.execute(
        f"""with citibike as (
select
start_location_id,
end_location_id,
date_part('dow', stoptime) as weekday,
CASE WHEN extract(hour from stoptime) >= 8 and extract(hour from stoptime) < 11 THEN '8 AM - 11 AM'
     WHEN extract(hour from stoptime) >= 11 and extract(hour from stoptime) < 16 THEN '11 AM - 4 PM'
     WHEN extract(hour from stoptime) >= 16 and extract(hour from stoptime) < 19 THEN '4 PM - 7 PM'
     WHEN extract(hour from stoptime) >= 19 and extract(hour from stoptime) < 22 THEN '7 PM - 10 PM'
     ELSE '10 PM - 8 AM' END
     AS time_group,
cast(avg(tripduration) as float) as avg_seconds
from citi_bike_rides
where start_location_id != end_location_id
group by start_location_id, end_location_id, weekday, time_group
),
taxi as (
select
start_location_id,
end_location_id,
date_part('dow', stoptime) as weekday,
CASE WHEN extract(hour from stoptime) >= 8 and extract(hour from stoptime) < 11 THEN '8 AM - 11 AM'
     WHEN extract(hour from stoptime) >= 11 and extract(hour from stoptime) < 16 THEN '11 AM - 4 PM'
     WHEN extract(hour from stoptime) >= 16 and extract(hour from stoptime) < 19 THEN '4 PM - 7 PM'
     WHEN extract(hour from stoptime) >= 19 and extract(hour from stoptime) < 22 THEN '7 PM - 10 PM'
     ELSE '10 PM - 8 AM' END
     AS time_group,
cast(avg(tripduration) as float) as avg_seconds
from taxi_rides
where start_location_id != end_location_id
group by start_location_id, end_location_id, weekday, time_group
)
select
citibike.start_location_id,
citibike.end_location_id,
citibike.weekday,
citibike.time_group,
citibike.avg_seconds as citibike_avg_seconds,
taxi.avg_seconds as taxi_avg_seconds,
case when citibike.avg_seconds < taxi.avg_seconds then 'Citi Bike'
     when taxi.avg_seconds < citibike.avg_seconds then 'Taxi'
     else 'No difference' end
     as fastest
from citibike inner join taxi
on citibike.start_location_id=taxi.start_location_id
and citibike.end_location_id=taxi.end_location_id
and citibike.weekday=taxi.weekday
and citibike.time_group=taxi.time_group
order by start_location_id, end_location_id, weekday, time_group;"""
    )
    data = cursor.fetchall()

    # Replace location ids with names
    for i, row in enumerate(data):
        listrow = list(row)
        listrow[0] = taxi_zones.get(listrow[0], "Unknown zone name")
        listrow[1] = taxi_zones.get(listrow[1], "Unknown zone name")
        listrow[2] = weekdays[listrow[2]]
        data[i] = tuple(listrow)

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
