# Data
from data_structures import Warehouse, Customer, calculate_dm

# Warehouse candidate locations
# id: (name, city, State, Zipcode, latitude, longitude)
warehouses = {
    1: ("Allentown", "Allentown", "PA", "18101", 40.602812, -75.470433),
    2: ("Atlanta", "Atlanta", "GA", "30301", 33.753693, -84.389544),
    3: ("Baltimore", "Baltimore", "MD", "21201", 39.294398, -76.622747),
    4: ("Boston", "Boston", "MA", "02101", 42.36097, -71.05344),
    5: ("Chicago", "Chicago", "IL", "60602", 41.88331, -87.624713),
    6: ("Cincinnati", "Cincinnati", "OH", "45201", 39.10663, -84.49974),
    7: ("Columbus", "Columbus", "OH", "43201", 39.991395, -83.001036),
    8: ("Dallas", "Dallas", "TX", "75201", 32.787642, -96.799525),
    9: ("Denver", "Denver", "CO", "80201", 39.75071, -104.996225),
    10: ("Indianapolis", "Indianapolis", "IN", "46201", 39.77422, -86.109309),
    11: ("Jacksonville", "Jacksonville", "FL", "32201", 30.32769, -81.64815),
    12: ("Kansas City", "Kansas City", "MO", "64101", 39.103883, -94.600613),
    13: ("Las Vegas", "Las Vegas", "NV", "89101", 36.17269, -115.121117),
    14: ("Los Angeles", "Los Angeles", "CA", "90001", 33.974044, -118.248849),
    15: ("Memphis", "Memphis", "TN", "37501", 35.033731, -89.934319),
    16: ("Minneapolis", "Minneapolis", "MN", "55401", 44.985775, -93.270165),
    17: ("Nashville", "Nashville", "TN", "37201", 36.164003, -86.7745),
    18: ("New Orleans", "New Orleans", "LA", "70112", 29.956664, -90.077506),
    19: ("Phoenix", "Phoenix", "AZ", "85001", 33.451015, -112.068554),
    20: ("Pittsburgh", "Pittsburgh", "PA", "15201", 40.474802, -79.95449),
    21: ("Raleigh", "Raleigh", "NC", "27601", 35.773856, -78.634051),
    22: ("Reno", "Reno", "NV", "89501", 39.526866, -119.811392),
    23: ("San Francisco", "San Francisco", "CA", "94102", 37.779887, -122.418066),
    24: ("Seattle", "Seattle", "WA", "98101", 47.611601, -122.333038),
    25: ("St. Louis", "St. Louis", "MO", "63101", 38.631358, -90.192246),
    26: ("Lubbock - Current WH", "Lubbock", "TX", "79401", 33.584601, -101.846676),
}

# customers::
# id:(name, city, state, zipcode, lat, long)
customers = {
    1: ("Akron", "Akron", "OH", "  ", 41.08, -81.52),
    2: ("Albuquerque", "Albuquerque", "NM", "  ", 35.12, -106.62),
    3: ("Alexandria", "Alexandria", "VA", "  ", 38.82, -77.09),
    4: ("Amarillo", "Amarillo", "TX", "  ", 35.2, -101.82),
    5: ("Anaheim", "Anaheim", "CA", "  ", 33.84, -117.87),
    6: ("Brownfield", "Brownfield", "TX", "  ", 33.18101, -102.27066),
    7: ("Arlington", "Arlington", "TX", "  ", 32.69, -97.13),
    8: ("Arlington", "Arlington", "VA", "  ", 38.88, -77.1),
    9: ("Atlanta", "Atlanta", "GA", "  ", 33.76, -84.42),
    10: ("Augusta-Richmond", "Augusta-Richmond", "GA", "  ", 33.46, -81.99),
    11: ("Aurora", "Aurora", "CO", "  ", 39.71, -104.73),
    12: ("Aurora", "Aurora", "IL", "  ", 41.77, -88.29),
    13: ("Austin", "Austin", "TX", "  ", 30.31, -97.75),
    14: ("Bakersfield", "Bakersfield", "CA", "  ", 35.36, -119),
    15: ("Baltimore", "Baltimore", "MD", "  ", 39.3, -76.61),
    16: ("Baton Rouge", "Baton Rouge", "LA", "  ", 30.45, -91.13),
    17: ("Bellevue", "Bellevue", "WA", "  ", 47.6, -122.16),
    18: ("Birmingham", "Birmingham", "AL", "  ", 33.53, -86.8),
    19: ("Boise City", "Boise City", "ID", "  ", 43.61, -116.23),
    20: ("Boston", "Boston", "MA", "  ", 42.34, -71.02),
    21: ("Bridgeport", "Bridgeport", "CT", "  ", 41.19, -73.2),
    22: ("Brownsville", "Brownsville", "TX", "  ", 25.93, -97.48),
    23: ("Buffalo", "Buffalo", "NY", "  ", 42.89, -78.86),
    24: ("Cape Coral", "Cape Coral", "FL", "  ", 26.64, -82),
    25: ("Carrollton", "Carrollton", "TX", "  ", 32.99, -96.9),
    26: ("Cary", "Cary", "NC", "  ", 35.78, -78.8),
    27: ("Cedar Rapids", "Cedar Rapids", "IA", "  ", 41.97, -91.67),
    28: ("Chandler", "Chandler", "AZ", "  ", 33.3, -111.87),
    29: ("Charlotte", "Charlotte", "NC", "  ", 35.2, -80.83),
    30: ("Chattanooga", "Chattanooga", "TN", "  ", 35.07, -85.26),
    31: ("Chesapeake", "Chesapeake", "VA", "  ", 36.68, -76.31),
    32: ("Chicago", "Chicago", "IL", "  ", 41.84, -87.68),
    33: ("Chula Vista", "Chula Vista", "CA", "  ", 32.63, -117.04),
    34: ("Cincinnati", "Cincinnati", "OH", "  ", 39.14, -84.51),
    35: ("Cleveland", "Cleveland", "OH", "  ", 41.48, -81.68),
    36: ("Colorado Springs", "Colorado Springs", "CO", "  ", 38.86, -104.76),
    37: ("Columbia", "Columbia", "SC", "  ", 34.04, -80.89),
    38: ("Columbus", "Columbus", "OH", "  ", 39.99, -82.99),
    39: ("Columbus", "Columbus", "GA", "  ", 32.51, -84.87),
    40: ("Corona", "Corona", "CA", "  ", 33.87, -117.57),
    41: ("Corpus Christi", "Corpus Christi", "TX", "  ", 27.71, -97.29),
    42: ("Dallas", "Dallas", "TX", "  ", 32.79, -96.77),
    43: ("Dayton", "Dayton", "OH", "  ", 39.78, -84.2),
    44: ("Denton", "Denton", "TX", "  ", 33.21, -97.13),
    45: ("Denver", "Denver", "CO", "  ", 39.77, -104.87),
    46: ("Des Moines", "Des Moines", "IA", "  ", 41.58, -93.62),
    47: ("Detroit", "Detroit", "MI", "  ", 42.38, -83.1),
    48: ("Durham", "Durham", "NC", "  ", 35.98, -78.91),
    49: ("East Los Angeles", "East Los Angeles", "CA", "  ", 34.03, -118.17),
    50: ("Elk Grove", "Elk Grove", "CA", "  ", 38.4, -121.37),
    51: ("El Paso", "El Paso", "TX", "  ", 31.85, -106.44),
    52: ("Escondido", "Escondido", "CA", "  ", 33.14, -117.07),
    53: ("Eugene", "Eugene", "OR", "  ", 44.05, -123.11),
    54: ("Fayetteville", "Fayetteville", "NC", "  ", 35.07, -78.9),
    55: ("Fontana", "Fontana", "CA", "  ", 34.1, -117.46),
    56: ("Fort Collins", "Fort Collins", "CO", "  ", 40.56, -105.07),
    57: ("Fort Lauderdale", "Fort Lauderdale", "FL", "  ", 26.14, -80.14),
    58: ("Fort Wayne", "Fort Wayne", "IN", "  ", 41.07, -85.14),
    59: ("Fort Worth", "Fort Worth", "TX", "  ", 32.75, -97.34),
    60: ("Fremont", "Fremont", "CA", "  ", 37.53, -122),
    61: ("Fresno", "Fresno", "CA", "  ", 36.78, -119.79),
    62: ("Fullerton", "Fullerton", "CA", "  ", 33.88, -117.93),
    63: ("Garden Grove", "Garden Grove", "CA", "  ", 33.78, -117.96),
    64: ("Garland", "Garland", "TX", "  ", 32.91, -96.63),
    65: ("Gilbert", "Gilbert", "AZ", "  ", 33.33, -111.76),
    66: ("Glendale", "Glendale", "AZ", "  ", 33.58, -112.2),
    67: ("Glendale", "Glendale", "CA", "  ", 34.18, -118.25),
    68: ("Grand Prairie", "Grand Prairie", "TX", "  ", 32.69, -97.02),
    69: ("Grand Rapids", "Grand Rapids", "MI", "  ", 42.96, -85.66),
    70: ("Greensboro", "Greensboro", "NC", "  ", 36.08, -79.83),
    71: ("Hampton", "Hampton", "VA", "  ", 37.05, -76.29),
    72: ("Hayward", "Hayward", "CA", "  ", 37.63, -122.1),
    73: ("Henderson", "Henderson", "NV", "  ", 36.03, -115),
    74: ("Hialeah", "Hialeah", "FL", "  ", 25.86, -80.3),
    75: ("Highlands Ranch", "Highlands Ranch", "CO", "  ", 39.55, -104.97),
    76: ("Hollywood", "Hollywood", "FL", "  ", 26.03, -80.16),
    77: ("Concord", "Concord", "NH", "  ", 43.2347496666667, -71.5435606666667),
    78: ("Houston", "Houston", "TX", "  ", 29.77, -95.39),
    79: ("Huntington Beach", "Huntington Beach", "CA", "  ", 33.69, -118.01),
    80: ("Huntsville", "Huntsville", "AL", "  ", 34.71, -86.63),
    81: ("Indianapolis", "Indianapolis", "IN", "  ", 39.78, -86.15),
    82: ("Irvine", "Irvine", "CA", "  ", 33.66, -117.8),
    83: ("Irving", "Irving", "TX", "  ", 32.86, -96.97),
    84: ("Jackson", "Jackson", "MS", "  ", 32.32, -90.21),
    85: ("Jacksonville", "Jacksonville", "FL", "  ", 30.33, -81.66),
    86: ("Jersey City", "Jersey City", "NJ", "  ", 40.71, -74.06),
    87: ("Joliet", "Joliet", "IL", "  ", 41.53, -88.12),
    88: ("Kansas City", "Kansas City", "MO", "  ", 39.12, -94.55),
    89: ("Kansas City", "Kansas City", "KS", "  ", 39.12, -94.73),
    90: ("Knoxville", "Knoxville", "TN", "  ", 35.97, -83.95),
    91: ("Lakewood", "Lakewood", "CO", "  ", 39.7, -105.11),
    92: ("Lancaster", "Lancaster", "CA", "  ", 34.69, -118.18),
    93: ("Laredo", "Laredo", "TX", "  ", 27.53, -99.49),
    94: ("Las Vegas", "Las Vegas", "NV", "  ", 36.21, -115.22),
    95: ("Lexington", "Lexington", "KY", "  ", 38.04, -84.46),
    96: ("Lincoln", "Lincoln", "NE", "  ", 40.82, -96.69),
    97: ("Little Rock", "Little Rock", "AR", "  ", 34.72, -92.35),
    98: ("Long Beach", "Long Beach", "CA", "  ", 33.79, -118.16),
    99: ("Los Angeles", "Los Angeles", "CA", "  ", 34.11, -118.41),
    100: ("Louisville", "Louisville", "KY", "  ", 38.22, -85.74),
    101: ("Lubbock", "Lubbock", "TX", "  ", 33.58, -101.88),
    102: ("MacAllen", "MacAllen", "TX", "  ", 26.22, -98.24),
    103: ("MacKinney", "MacKinney", "TX", "  ", 33.2, -96.65),
    104: ("Madison", "Madison", "WI", "  ", 43.08, -89.39),
    105: ("Memphis", "Memphis", "TN", "  ", 35.11, -90.01),
    106: ("Mesa", "Mesa", "AZ", "  ", 33.42, -111.74),
    107: ("Mesquite", "Mesquite", "TX", "  ", 32.77, -96.6),
    108: ("Metairie", "Metairie", "LA", "  ", 30, -90.18),
    109: ("Miami", "Miami", "FL", "  ", 25.78, -80.21),
    110: ("Milwaukee", "Milwaukee", "WI", "  ", 43.06, -87.97),
    111: ("Minneapolis", "Minneapolis", "MN", "  ", 44.96, -93.27),
    112: ("Mobile", "Mobile", "AL", "  ", 30.68, -88.09),
    113: ("Modesto", "Modesto", "CA", "  ", 37.66, -120.99),
    114: ("Montgomery", "Montgomery", "AL", "  ", 32.35, -86.28),
    115: ("Moreno Valley", "Moreno Valley", "CA", "  ", 33.93, -117.21),
    116: ("Naperville", "Naperville", "IL", "  ", 41.76, -88.15),
    117: ("Nashville", "Nashville", "TN", "  ", 36.17, -86.78),
    118: ("Newark", "Newark", "NJ", "  ", 40.72, -74.17),
    119: ("New Orleans", "New Orleans", "LA", "  ", 30.07, -89.93),
    120: ("Newport News", "Newport News", "VA", "  ", 37.08, -76.51),
    121: ("New York", "New York", "NY", "  ", 40.67, -73.94),
    122: ("Norfolk", "Norfolk", "VA", "  ", 36.92, -76.24),
    123: ("North Las Vegas", "North Las Vegas", "NV", "  ", 36.27, -115.14),
    124: ("Oakland", "Oakland", "CA", "  ", 37.77, -122.22),
    125: ("Oceanside", "Oceanside", "CA", "  ", 33.23, -117.31),
    126: ("Oklahoma City", "Oklahoma City", "OK", "  ", 35.47, -97.51),
    127: ("Omaha", "Omaha", "NE", "  ", 41.26, -96.01),
    128: ("Ontario", "Ontario", "CA", "  ", 34.05, -117.61),
    129: ("Orange", "Orange", "CA", "  ", 33.81, -117.82),
    130: ("Orlando", "Orlando", "FL", "  ", 28.5, -81.37),
    131: ("Overland Park", "Overland Park", "KS", "  ", 38.91, -94.68),
    132: ("Oxnard", "Oxnard", "CA", "  ", 34.2, -119.21),
    133: ("Palmdale", "Palmdale", "CA", "  ", 34.61, -118.09),
    134: ("Paradise", "Paradise", "NV", "  ", 36.08, -115.13),
    135: ("Pasadena", "Pasadena", "TX", "  ", 29.66, -95.15),
    136: ("Pasadena", "Pasadena", "CA", "  ", 34.16, -118.14),
    137: ("Paterson", "Paterson", "NJ", "  ", 40.91, -74.16),
    138: ("Pembroke Pines", "Pembroke Pines", "FL", "  ", 26.01, -80.34),
    139: ("San Angelo", "San Angelo", "TX", "  ", 31.44322, -100.46333),
    140: ("Philadelphia", "Philadelphia", "PA", "  ", 40.01, -75.13),
    141: ("Phoenix", "Phoenix", "AZ", "  ", 33.54, -112.07),
    142: ("Pittsburgh", "Pittsburgh", "PA", "  ", 40.44, -79.98),
    143: ("Plano", "Plano", "TX", "  ", 33.05, -96.75),
    144: ("Pomona", "Pomona", "CA", "  ", 34.06, -117.76),
    145: ("Portland", "Portland", "OR", "  ", 45.54, -122.66),
    146: ("Port Saint Lucie", "Port Saint Lucie", "FL", "  ", 27.28, -80.35),
    147: ("Providence", "Providence", "RI", "  ", 41.82, -71.42),
    148: ("Raleigh", "Raleigh", "NC", "  ", 35.82, -78.66),
    149: ("Del Rio", "Del Rio", "TX", "  ", 29.36041, -100.89904),
    150: ("Reno", "Reno", "NV", "  ", 39.54, -119.82),
    151: ("Richmond", "Richmond", "VA", "  ", 37.53, -77.47),
    152: ("Riverside", "Riverside", "CA", "  ", 33.94, -117.4),
    153: ("Rochester", "Rochester", "NY", "  ", 43.17, -77.62),
    154: ("Rockford", "Rockford", "IL", "  ", 42.27, -89.06),
    155: ("Sacramento", "Sacramento", "CA", "  ", 38.57, -121.47),
    156: ("Saint Louis", "Saint Louis", "MO", "  ", 38.64, -90.24),
    157: ("Saint Paul", "Saint Paul", "MN", "  ", 44.95, -93.1),
    158: ("Saint Petersburg", "Saint Petersburg", "FL", "  ", 27.76, -82.64),
    159: ("Salem", "Salem", "OR", "  ", 44.92, -123.02),
    160: ("Salinas", "Salinas", "CA", "  ", 36.68, -121.64),
    161: ("Salt Lake City", "Salt Lake City", "UT", "  ", 40.78, -111.93),
    162: ("San Antonio", "San Antonio", "TX", "  ", 29.46, -98.51),
    163: ("San Bernardino", "San Bernardino", "CA", "  ", 34.14, -117.29),
    164: ("San Diego", "San Diego", "CA", "  ", 32.81, -117.14),
    165: ("San Francisco", "San Francisco", "CA", "  ", 37.77, -122.45),
    166: ("San Jose", "San Jose", "CA", "  ", 37.3, -121.85),
    167: ("Santa Ana", "Santa Ana", "CA", "  ", 33.74, -117.88),
    168: ("Santa Clarita", "Santa Clarita", "CA", "  ", 34.41, -118.51),
    169: ("Santa Rosa", "Santa Rosa", "CA", "  ", 38.45, -122.7),
    170: ("Savannah", "Savannah", "GA", "  ", 32.02, -81.13),
    171: ("Scottsdale", "Scottsdale", "AZ", "  ", 33.69, -111.87),
    172: ("Seattle", "Seattle", "WA", "  ", 47.62, -122.35),
    173: ("Shreveport", "Shreveport", "LA", "  ", 32.47, -93.8),
    174: ("Sioux Falls", "Sioux Falls", "SD", "  ", 43.54, -96.73),
    175: ("Spokane", "Spokane", "WA", "  ", 47.67, -117.41),
    176: ("Springfield", "Springfield", "MO", "  ", 37.2, -93.29),
    177: ("Springfield", "Springfield", "MA", "  ", 42.12, -72.54),
    178: ("Spring Valley", "Spring Valley", "NV", "  ", 36.11, -115.24),
    179: ("Stockton", "Stockton", "CA", "  ", 37.97, -121.31),
    180: ("Sunnyvale", "Sunnyvale", "CA", "  ", 37.39, -122.03),
    181: ("Sunrise Manor", "Sunrise Manor", "NV", "  ", 36.19, -115.05),
    182: ("Syracuse", "Syracuse", "NY", "  ", 43.04, -76.14),
    183: ("Tacoma", "Tacoma", "WA", "  ", 47.25, -122.46),
    184: ("Tallahassee", "Tallahassee", "FL", "  ", 30.46, -84.28),
    185: ("Tampa", "Tampa", "FL", "  ", 27.96, -82.48),
    186: ("Tempe", "Tempe", "AZ", "  ", 33.39, -111.93),
    187: ("Toledo", "Toledo", "OH", "  ", 41.66, -83.58),
    188: ("Toms River", "Toms River", "NJ", "  ", 39.94, -74.17),
    189: ("Torrance", "Torrance", "CA", "  ", 33.83, -118.34),
    190: ("Tucson", "Tucson", "AZ", "  ", 32.2, -110.89),
    191: ("Tulsa", "Tulsa", "OK", "  ", 36.13, -95.92),
    192: ("Vancouver", "Vancouver", "WA", "  ", 45.63, -122.64),
    193: ("Virginia Beach", "Virginia Beach", "VA", "  ", 36.74, -76.04),
    194: ("Visalia", "Visalia", "CA", "  ", 36.33, -119.32),
    195: ("Warren", "Warren", "MI", "  ", 42.49, -83.03),
    196: ("Washington", "Washington", "DC", "  ", 38.91, -77.02),
    197: ("Wichita", "Wichita", "KS", "  ", 37.69, -97.34),
    198: ("Winston-Salem", "Winston-Salem", "NC", "  ", 36.1, -80.26),
    199: ("Worcester", "Worcester", "MA", "  ", 42.27, -71.81),
    200: ("Yonkers", "Yonkers", "NY", "  ", 40.95, -73.87),
}

#  Demand::
# id: demand_value
customer_demands = {
    1: 205375,
    2: 535923,
    3: 147786,
    4: 190449,
    5: 342336,
    6: 283690,
    7: 385024,
    8: 214890,
    9: 571861,
    10: 199489,
    11: 334924,
    12: 176710,
    13: 792778,
    14: 336429,
    15: 632410,
    16: 221091,
    17: 128225,
    18: 226152,
    19: 210099,
    20: 610407,
    21: 136604,
    22: 183598,
    23: 267037,
    24: 161428,
    25: 130013,
    26: 145939,
    27: 130349,
    28: 258122,
    29: 723514,
    30: 173001,
    31: 223315,
    32: 2878948,
    33: 226606,
    34: 332807,
    35: 424526,
    36: 388306,
    37: 130246,
    38: 768662,
    39: 193007,
    40: 152977,
    41: 296937,
    42: 1304930,
    43: 151594,
    44: 127364,
    45: 609651,
    46: 200202,
    47: 901160,
    48: 235337,
    49: 135682,
    50: 141026,
    51: 631862,
    52: 139583,
    53: 152842,
    54: 177632,
    55: 191526,
    56: 141921,
    57: 184625,
    58: 253250,
    59: 751149,
    60: 207431,
    61: 490930,
    62: 133165,
    63: 167800,
    64: 220597,
    65: 243090,
    66: 255662,
    67: 199608,
    68: 167767,
    69: 193337,
    70: 259523,
    71: 147560,
    72: 145517,
    73: 265681,
    74: 209524,
    75: 129817,
    76: 142105,
    77: 375134,
    78: 2307883,
    79: 194227,
    80: 185501,
    81: 803930,
    82: 223785,
    83: 206798,
    84: 171210,
    85: 822401,
    86: 242594,
    87: 153577,
    88: 454520,
    89: 144431,
    90: 187071,
    91: 142294,
    92: 151452,
    93: 232298,
    94: 570083,
    95: 279146,
    96: 257612,
    97: 192247,
    98: 464505,
    99: 3878715,
    100: 556482,
    101: 226180,
    102: 136555,
    103: 135935,
    104: 237838,
    105: 662989,
    106: 474115,
    107: 134509,
    108: 141919,
    109: 425242,
    110: 606508,
    111: 386751,
    112: 190007,
    113: 203882,
    114: 200848,
    115: 199353,
    116: 146177,
    117: 605197,
    118: 279278,
    119: 206720,
    120: 182057,
    121: 8459026,
    122: 234477,
    123: 236574,
    124: 412612,
    125: 172679,
    126: 564147,
    127: 449283,
    128: 174731,
    129: 141351,
    130: 235745,
    131: 176161,
    132: 189413,
    133: 150264,
    134: 261122,
    135: 148101,
    136: 144485,
    137: 145162,
    138: 146408,
    139: 168424,
    140: 1445993,
    141: 1635783,
    142: 305708,
    143: 282016,
    144: 154638,
    145: 573530,
    146: 163859,
    147: 170868,
    148: 421938,
    149: 176424,
    150: 221051,
    151: 198179,
    152: 302653,
    153: 205236,
    154: 159109,
    155: 475452,
    156: 349763,
    157: 281501,
    158: 243829,
    159: 157890,
    160: 145628,
    161: 184856,
    162: 1402013,
    163: 199314,
    164: 1309749,
    165: 817411,
    166: 977893,
    167: 341991,
    168: 171722,
    169: 159730,
    170: 133244,
    171: 241464,
    172: 614214,
    173: 204311,
    174: 160938,
    175: 204424,
    176: 158605,
    177: 149926,
    178: 212144,
    179: 291422,
    180: 135564,
    181: 219092,
    182: 136410,
    183: 200855,
    184: 175438,
    185: 351091,
    186: 181658,
    187: 288207,
    188: 131619,
    189: 141478,
    190: 551067,
    191: 387683,
    192: 169603,
    193: 439564,
    194: 127444,
    195: 133470,
    196: 597885,
    197: 374803,
    198: 223127,
    199: 174854,
    200: 206441,
}

# Convert data using standard nametuple

for k, value in warehouses.items():
    warehouses[k] = Warehouse(
        name=value[0],
        city=value[1],
        state=value[2],
        zipcode=value[3],
        latitude=value[4],
        longitude=value[5],
        capacity=None,
        fixed_cost=0,
    )

for k, value in customers.items():
    customers[k] = Customer(
        name=value[0],
        city=value[1],
        state=value[2],
        zipcode=value[3],
        latitude=value[4],
        longitude=value[5],
        demand=customer_demands[k],
    )


# Distances
# (from, to): distance
distance = calculate_dm(warehouses, customers, use_haversine=True)
