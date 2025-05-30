# ==============================================================================
# description     :Data for the project work A.Y. 2023/2024
# author          :Roberto Pinto
# date            :2024.04.27
# version         :1.0
# notes           :This software is meant for teaching purpose only and it is provided as-is under the GPL license.
# ==============================================================================

# Data
from data_structures import Warehouse, Customer

warehouses = {
    0: Warehouse(
        name="W0",
        city="Paris",
        state="FR",
        zipcode="",
        latitude=48.853,
        longitude=2.349,
        capacity=1100,
        fixed_cost=0.0,
    ),
    1: Warehouse(
        name="W1",
        city="Marseille",
        state="FR",
        zipcode="",
        latitude=43.297,
        longitude=5.381,
        capacity=800,
        fixed_cost=0.0,
    ),
    2: Warehouse(
        name="W2",
        city="Lyon",
        state="FR",
        zipcode="",
        latitude=45.748,
        longitude=4.847,
        capacity=800,
        fixed_cost=0.0,
    ),
    3: Warehouse(
        name="W3",
        city="Toulouse",
        state="FR",
        zipcode="",
        latitude=43.604,
        longitude=1.444,
        capacity=900,
        fixed_cost=0.0,
    ),
    4: Warehouse(
        name="W4",
        city="Nice",
        state="FR",
        zipcode="",
        latitude=43.703,
        longitude=7.266,
        capacity=800,
        fixed_cost=0.0,
    ),
    5: Warehouse(
        name="W5",
        city="Nantes",
        state="FR",
        zipcode="",
        latitude=47.217,
        longitude=-1.553,
        capacity=900,
        fixed_cost=0.0,
    ),
    6: Warehouse(
        name="W6",
        city="Strasbourg",
        state="FR",
        zipcode="",
        latitude=48.584,
        longitude=7.746,
        capacity=600,
        fixed_cost=0.0,
    ),
    7: Warehouse(
        name="W7",
        city="Bordeaux",
        state="FR",
        zipcode="",
        latitude=44.84,
        longitude=-0.581,
        capacity=900,
        fixed_cost=0.0,
    ),
    8: Warehouse(
        name="W8",
        city="Montpellier",
        state="FR",
        zipcode="",
        latitude=43.611,
        longitude=3.876,
        capacity=900,
        fixed_cost=0.0,
    ),
    9: Warehouse(
        name="W9",
        city="Rouen",
        state="FR",
        zipcode="",
        latitude=49.443,
        longitude=1.099,
        capacity=700,
        fixed_cost=0.0,
    ),
    10: Warehouse(
        name="W10",
        city="Lille",
        state="FR",
        zipcode="",
        latitude=50.633,
        longitude=3.059,
        capacity=800,
        fixed_cost=0.0,
    ),
}

customers = {
    0: Customer(
        name="C0",
        city="Paris",
        state="FR",
        zipcode="",
        latitude=48.8567,
        longitude=2.3522,
        demand=81,
    ),
    1: Customer(
        name="C1",
        city="Bordeaux",
        state="FR",
        zipcode="",
        latitude=44.84,
        longitude=-0.58,
        demand=29,
    ),
    2: Customer(
        name="C2",
        city="Marseille",
        state="FR",
        zipcode="",
        latitude=43.2964,
        longitude=5.37,
        demand=42,
    ),
    3: Customer(
        name="C3",
        city="Toulouse",
        state="FR",
        zipcode="",
        latitude=43.6045,
        longitude=1.444,
        demand=31,
    ),
    4: Customer(
        name="C4",
        city="Nice",
        state="FR",
        zipcode="",
        latitude=43.7034,
        longitude=7.2663,
        demand=71,
    ),
    5: Customer(
        name="C5",
        city="Nantes",
        state="FR",
        zipcode="",
        latitude=47.2181,
        longitude=-1.5528,
        demand=33,
    ),
    6: Customer(
        name="C6",
        city="Montpellier",
        state="FR",
        zipcode="",
        latitude=43.6119,
        longitude=3.8772,
        demand=46,
    ),
    7: Customer(
        name="C7",
        city="Strasbourg",
        state="FR",
        zipcode="",
        latitude=48.5833,
        longitude=7.7458,
        demand=68,
    ),
    8: Customer(
        name="C8",
        city="Rennes",
        state="FR",
        zipcode="",
        latitude=48.1147,
        longitude=-1.6794,
        demand=75,
    ),
    9: Customer(
        name="C9",
        city="Toulon",
        state="FR",
        zipcode="",
        latitude=43.1258,
        longitude=5.9306,
        demand=32,
    ),
    10: Customer(
        name="C10",
        city="Le Havre",
        state="FR",
        zipcode="",
        latitude=49.49,
        longitude=0.1,
        demand=72,
    ),
    11: Customer(
        name="C11",
        city="Dijon",
        state="FR",
        zipcode="",
        latitude=47.3167,
        longitude=5.0167,
        demand=41,
    ),
    12: Customer(
        name="C12",
        city="Grenoble",
        state="FR",
        zipcode="",
        latitude=45.1715,
        longitude=5.7224,
        demand=66,
    ),
    13: Customer(
        name="C13",
        city="Angers",
        state="FR",
        zipcode="",
        latitude=47.4736,
        longitude=-0.5542,
        demand=80,
    ),
    14: Customer(
        name="C14",
        city="Villeurbanne",
        state="FR",
        zipcode="",
        latitude=45.7667,
        longitude=4.8803,
        demand=63,
    ),
    15: Customer(
        name="C15",
        city="Nîmes",
        state="FR",
        zipcode="",
        latitude=43.8383,
        longitude=4.3597,
        demand=79,
    ),
    16: Customer(
        name="C16",
        city="Aix-en-Provence",
        state="FR",
        zipcode="",
        latitude=43.5263,
        longitude=5.4454,
        demand=67,
    ),
    17: Customer(
        name="C17",
        city="Clermont-Ferrand",
        state="FR",
        zipcode="",
        latitude=45.7831,
        longitude=3.0824,
        demand=43,
    ),
    18: Customer(
        name="C18",
        city="Le Mans",
        state="FR",
        zipcode="",
        latitude=48.0077,
        longitude=0.1984,
        demand=34,
    ),
    19: Customer(
        name="C19",
        city="Brest",
        state="FR",
        zipcode="",
        latitude=48.39,
        longitude=-4.49,
        demand=25,
    ),
    20: Customer(
        name="C20",
        city="Tours",
        state="FR",
        zipcode="",
        latitude=47.3936,
        longitude=0.6892,
        demand=64,
    ),
    21: Customer(
        name="C21",
        city="Amiens",
        state="FR",
        zipcode="",
        latitude=49.892,
        longitude=2.299,
        demand=50,
    ),
    22: Customer(
        name="C22",
        city="Limoges",
        state="FR",
        zipcode="",
        latitude=45.8353,
        longitude=1.2625,
        demand=54,
    ),
    23: Customer(
        name="C23",
        city="Perpignan",
        state="FR",
        zipcode="",
        latitude=42.6986,
        longitude=2.8956,
        demand=31,
    ),
    24: Customer(
        name="C24",
        city="Besançon",
        state="FR",
        zipcode="",
        latitude=47.24,
        longitude=6.02,
        demand=71,
    ),
    25: Customer(
        name="C25",
        city="Orléans",
        state="FR",
        zipcode="",
        latitude=47.9025,
        longitude=1.909,
        demand=28,
    ),
    26: Customer(
        name="C26",
        city="Rouen",
        state="FR",
        zipcode="",
        latitude=49.4428,
        longitude=1.0886,
        demand=30,
    ),
    27: Customer(
        name="C27",
        city="Montreuil",
        state="FR",
        zipcode="",
        latitude=48.8611,
        longitude=2.4436,
        demand=66,
    ),
    28: Customer(
        name="C28",
        city="Caen",
        state="FR",
        zipcode="",
        latitude=49.1814,
        longitude=-0.3636,
        demand=71,
    ),
    29: Customer(
        name="C29",
        city="Argenteuil",
        state="FR",
        zipcode="",
        latitude=48.95,
        longitude=2.25,
        demand=76,
    ),
    30: Customer(
        name="C30",
        city="Nancy",
        state="FR",
        zipcode="",
        latitude=48.6936,
        longitude=6.1846,
        demand=31,
    ),
    31: Customer(
        name="C31",
        city="Tourcoing",
        state="FR",
        zipcode="",
        latitude=50.7239,
        longitude=3.1612,
        demand=81,
    ),
    32: Customer(
        name="C32",
        city="Roubaix",
        state="FR",
        zipcode="",
        latitude=50.6901,
        longitude=3.1817,
        demand=73,
    ),
    33: Customer(
        name="C33",
        city="Vitry-sur-Seine",
        state="FR",
        zipcode="",
        latitude=48.7875,
        longitude=2.3928,
        demand=59,
    ),
    34: Customer(
        name="C34",
        city="Poitiers",
        state="FR",
        zipcode="",
        latitude=46.58,
        longitude=0.34,
        demand=45,
    ),
    35: Customer(
        name="C35",
        city="Dunkerque",
        state="FR",
        zipcode="",
        latitude=51.0383,
        longitude=2.3775,
        demand=58,
    ),
    36: Customer(
        name="C36",
        city="Versailles",
        state="FR",
        zipcode="",
        latitude=48.8053,
        longitude=2.135,
        demand=46,
    ),
    37: Customer(
        name="C37",
        city="La Rochelle",
        state="FR",
        zipcode="",
        latitude=46.16,
        longitude=-1.15,
        demand=76,
    ),
    38: Customer(
        name="C38",
        city="Pau",
        state="FR",
        zipcode="",
        latitude=43.3,
        longitude=-0.37,
        demand=47,
    ),
    39: Customer(
        name="C39",
        city="Mérignac",
        state="FR",
        zipcode="",
        latitude=44.8386,
        longitude=-0.6436,
        demand=49,
    ),
    40: Customer(
        name="C40",
        city="Antibes",
        state="FR",
        zipcode="",
        latitude=43.5808,
        longitude=7.1239,
        demand=46,
    ),
    41: Customer(
        name="C41",
        city="Ajaccio",
        state="FR",
        zipcode="",
        latitude=41.9267,
        longitude=8.7369,
        demand=26,
    ),
    42: Customer(
        name="C42",
        city="Cannes",
        state="FR",
        zipcode="",
        latitude=43.5513,
        longitude=7.0128,
        demand=89,
    ),
    43: Customer(
        name="C43",
        city="Saint-Nazaire",
        state="FR",
        zipcode="",
        latitude=47.2736,
        longitude=-2.2139,
        demand=47,
    ),
    44: Customer(
        name="C44",
        city="Calais",
        state="FR",
        zipcode="",
        latitude=50.9481,
        longitude=1.8564,
        demand=30,
    ),
    45: Customer(
        name="C45",
        city="Pessac",
        state="FR",
        zipcode="",
        latitude=44.8067,
        longitude=-0.6311,
        demand=39,
    ),
    46: Customer(
        name="C46",
        city="Vénissieux",
        state="FR",
        zipcode="",
        latitude=45.6969,
        longitude=4.8858,
        demand=85,
    ),
    47: Customer(
        name="C47",
        city="Clichy",
        state="FR",
        zipcode="",
        latitude=48.9044,
        longitude=2.3064,
        demand=66,
    ),
    48: Customer(
        name="C48",
        city="Valence",
        state="FR",
        zipcode="",
        latitude=44.9333,
        longitude=4.8917,
        demand=85,
    ),
    49: Customer(
        name="C49",
        city="La Seyne-sur-Mer",
        state="FR",
        zipcode="",
        latitude=43.1,
        longitude=5.883,
        demand=65,
    ),
    50: Customer(
        name="C50",
        city="Pantin",
        state="FR",
        zipcode="",
        latitude=48.8966,
        longitude=2.4017,
        demand=39,
    ),
    51: Customer(
        name="C51",
        city="Lorient",
        state="FR",
        zipcode="",
        latitude=47.75,
        longitude=-3.36,
        demand=25,
    ),
    52: Customer(
        name="C52",
        city="Bellevue",
        state="FR",
        zipcode="",
        latitude=48.871,
        longitude=2.385,
        demand=66,
    ),
    53: Customer(
        name="C53",
        city="Vannes",
        state="FR",
        zipcode="",
        latitude=47.6559,
        longitude=-2.7603,
        demand=76,
    ),
    54: Customer(
        name="C54",
        city="Chelles",
        state="FR",
        zipcode="",
        latitude=48.8833,
        longitude=2.6,
        demand=52,
    ),
    55: Customer(
        name="C55",
        city="Évry",
        state="FR",
        zipcode="",
        latitude=48.6238,
        longitude=2.4296,
        demand=46,
    ),
    56: Customer(
        name="C56",
        city="Saint-Quentin",
        state="FR",
        zipcode="",
        latitude=49.8486,
        longitude=3.2864,
        demand=62,
    ),
    57: Customer(
        name="C57",
        city="Bayonne",
        state="FR",
        zipcode="",
        latitude=43.49,
        longitude=-1.48,
        demand=51,
    ),
    58: Customer(
        name="C58",
        city="Cagnes-sur-Mer",
        state="FR",
        zipcode="",
        latitude=43.6644,
        longitude=7.1489,
        demand=35,
    ),
    59: Customer(
        name="C59",
        city="Vaulx-en-Velin",
        state="FR",
        zipcode="",
        latitude=45.7768,
        longitude=4.9186,
        demand=50,
    ),
    60: Customer(
        name="C60",
        city="Fontenay-sous-Bois",
        state="FR",
        zipcode="",
        latitude=48.8517,
        longitude=2.4772,
        demand=31,
    ),
    61: Customer(
        name="C61",
        city="Laval",
        state="FR",
        zipcode="",
        latitude=48.0733,
        longitude=-0.7689,
        demand=75,
    ),
    62: Customer(
        name="C62",
        city="Saint-Herblain",
        state="FR",
        zipcode="",
        latitude=47.2122,
        longitude=-1.6497,
        demand=89,
    ),
    63: Customer(
        name="C63",
        city="Saint-Priest",
        state="FR",
        zipcode="",
        latitude=45.6964,
        longitude=4.9439,
        demand=34,
    ),
    64: Customer(
        name="C64",
        city="Bastia",
        state="FR",
        zipcode="",
        latitude=42.7008,
        longitude=9.4503,
        demand=34,
    ),
    65: Customer(
        name="C65",
        city="Évreux",
        state="FR",
        zipcode="",
        latitude=49.02,
        longitude=1.15,
        demand=31,
    ),
    66: Customer(
        name="C66",
        city="Charleville-Mézières",
        state="FR",
        zipcode="",
        latitude=49.7719,
        longitude=4.7161,
        demand=59,
    ),
    67: Customer(
        name="C67",
        city="Rosny-sous-Bois",
        state="FR",
        zipcode="",
        latitude=48.8667,
        longitude=2.4833,
        demand=41,
    ),
    68: Customer(
        name="C68",
        city="Talence",
        state="FR",
        zipcode="",
        latitude=44.8,
        longitude=-0.584,
        demand=65,
    ),
    69: Customer(
        name="C69",
        city="Belfort",
        state="FR",
        zipcode="",
        latitude=47.64,
        longitude=6.85,
        demand=25,
    ),
    70: Customer(
        name="C70",
        city="Chalon-sur-Saône",
        state="FR",
        zipcode="",
        latitude=46.7806,
        longitude=4.8528,
        demand=79,
    ),
    71: Customer(
        name="C71",
        city="Sète",
        state="FR",
        zipcode="",
        latitude=43.4053,
        longitude=3.6975,
        demand=30,
    ),
    72: Customer(
        name="C72",
        city="Saint-Brieuc",
        state="FR",
        zipcode="",
        latitude=48.5136,
        longitude=-2.7653,
        demand=39,
    ),
    73: Customer(
        name="C73",
        city="Tarbes",
        state="FR",
        zipcode="",
        latitude=43.23,
        longitude=0.07,
        demand=64,
    ),
    74: Customer(
        name="C74",
        city="Alès",
        state="FR",
        zipcode="",
        latitude=44.1281,
        longitude=4.0817,
        demand=53,
    ),
    75: Customer(
        name="C75",
        city="Châlons-en-Champagne",
        state="FR",
        zipcode="",
        latitude=48.9575,
        longitude=4.365,
        demand=54,
    ),
    76: Customer(
        name="C76",
        city="Caluire-et-Cuire",
        state="FR",
        zipcode="",
        latitude=45.7953,
        longitude=4.8472,
        demand=68,
    ),
    77: Customer(
        name="C77",
        city="Rezé",
        state="FR",
        zipcode="",
        latitude=47.1917,
        longitude=-1.5694,
        demand=26,
    ),
    78: Customer(
        name="C78",
        city="Valenciennes",
        state="FR",
        zipcode="",
        latitude=50.3581,
        longitude=3.5233,
        demand=31,
    ),
    79: Customer(
        name="C79",
        city="Châteauroux",
        state="FR",
        zipcode="",
        latitude=46.8103,
        longitude=1.6911,
        demand=31,
    ),
    80: Customer(
        name="C80",
        city="Garges-lès-Gonesse",
        state="FR",
        zipcode="",
        latitude=48.9728,
        longitude=2.4008,
        demand=61,
    ),
    81: Customer(
        name="C81",
        city="Le Cannet",
        state="FR",
        zipcode="",
        latitude=43.5769,
        longitude=7.0194,
        demand=38,
    ),
    82: Customer(
        name="C82",
        city="Anglet",
        state="FR",
        zipcode="",
        latitude=43.485,
        longitude=-1.5183,
        demand=86,
    ),
    83: Customer(
        name="C83",
        city="Angoulême",
        state="FR",
        zipcode="",
        latitude=45.65,
        longitude=0.16,
        demand=77,
    ),
    84: Customer(
        name="C84",
        city="Wattrelos",
        state="FR",
        zipcode="",
        latitude=50.7,
        longitude=3.217,
        demand=48,
    ),
    85: Customer(
        name="C85",
        city="Villenave-d’Ornon",
        state="FR",
        zipcode="",
        latitude=44.7806,
        longitude=-0.5658,
        demand=74,
    ),
    86: Customer(
        name="C86",
        city="Colomiers",
        state="FR",
        zipcode="",
        latitude=43.6139,
        longitude=1.3367,
        demand=68,
    ),
    87: Customer(
        name="C87",
        city="Chartres",
        state="FR",
        zipcode="",
        latitude=48.456,
        longitude=1.484,
        demand=63,
    ),
    88: Customer(
        name="C88",
        city="Annemasse",
        state="FR",
        zipcode="",
        latitude=46.1958,
        longitude=6.2364,
        demand=73,
    ),
    89: Customer(
        name="C89",
        city="Creil",
        state="FR",
        zipcode="",
        latitude=49.2583,
        longitude=2.4833,
        demand=42,
    ),
    90: Customer(
        name="C90",
        city="Montluçon",
        state="FR",
        zipcode="",
        latitude=46.3408,
        longitude=2.6033,
        demand=45,
    ),
    91: Customer(
        name="C91",
        city="Nevers",
        state="FR",
        zipcode="",
        latitude=46.9933,
        longitude=3.1572,
        demand=76,
    ),
    92: Customer(
        name="C92",
        city="Agen",
        state="FR",
        zipcode="",
        latitude=44.2049,
        longitude=0.6212,
        demand=60,
    ),
    93: Customer(
        name="C93",
        city="Aix-les-Bains",
        state="FR",
        zipcode="",
        latitude=45.6886,
        longitude=5.915,
        demand=28,
    ),
    94: Customer(
        name="C94",
        city="Plaisir",
        state="FR",
        zipcode="",
        latitude=48.8183,
        longitude=1.9472,
        demand=26,
    ),
    95: Customer(
        name="C95",
        city="Rillieux-la-Pape",
        state="FR",
        zipcode="",
        latitude=45.8214,
        longitude=4.8983,
        demand=84,
    ),
    96: Customer(
        name="C96",
        city="Viry-Châtillon",
        state="FR",
        zipcode="",
        latitude=48.6713,
        longitude=2.375,
        demand=36,
    ),
    97: Customer(
        name="C97",
        city="Saint-Laurent-du-Var",
        state="FR",
        zipcode="",
        latitude=43.668,
        longitude=7.188,
        demand=89,
    ),
    98: Customer(
        name="C98",
        city="Bègles",
        state="FR",
        zipcode="",
        latitude=44.8086,
        longitude=-0.5478,
        demand=90,
    ),
    99: Customer(
        name="C99",
        city="Menton",
        state="FR",
        zipcode="",
        latitude=43.775,
        longitude=7.5,
        demand=49,
    ),
    100: Customer(
        name="C100",
        city="Liévin",
        state="FR",
        zipcode="",
        latitude=50.4228,
        longitude=2.7786,
        demand=63,
    ),
    101: Customer(
        name="C101",
        city="La Garenne-Colombes",
        state="FR",
        zipcode="",
        latitude=48.9056,
        longitude=2.2445,
        demand=47,
    ),
    102: Customer(
        name="C102",
        city="Périgueux",
        state="FR",
        zipcode="",
        latitude=45.1929,
        longitude=0.7217,
        demand=88,
    ),
    103: Customer(
        name="C103",
        city="Tournefeuille",
        state="FR",
        zipcode="",
        latitude=43.5853,
        longitude=1.3442,
        demand=89,
    ),
    104: Customer(
        name="C104",
        city="Sotteville-lès-Rouen",
        state="FR",
        zipcode="",
        latitude=49.4092,
        longitude=1.09,
        demand=42,
    ),
    105: Customer(
        name="C105",
        city="Fresnes",
        state="FR",
        zipcode="",
        latitude=48.755,
        longitude=2.3221,
        demand=63,
    ),
    106: Customer(
        name="C106",
        city="Soissons",
        state="FR",
        zipcode="",
        latitude=49.3817,
        longitude=3.3236,
        demand=87,
    ),
    107: Customer(
        name="C107",
        city="Saint-Étienne-du-Rouvray",
        state="FR",
        zipcode="",
        latitude=49.3786,
        longitude=1.105,
        demand=77,
    ),
    108: Customer(
        name="C108",
        city="Dieppe",
        state="FR",
        zipcode="",
        latitude=49.925,
        longitude=1.075,
        demand=47,
    ),
    109: Customer(
        name="C109",
        city="Saint-Sébastien-sur-Loire",
        state="FR",
        zipcode="",
        latitude=47.2081,
        longitude=-1.5014,
        demand=72,
    ),
    110: Customer(
        name="C110",
        city="Vallauris",
        state="FR",
        zipcode="",
        latitude=43.5805,
        longitude=7.0538,
        demand=79,
    ),
    111: Customer(
        name="C111",
        city="Lambersart",
        state="FR",
        zipcode="",
        latitude=50.65,
        longitude=3.025,
        demand=89,
    ),
    112: Customer(
        name="C112",
        city="Oullins",
        state="FR",
        zipcode="",
        latitude=45.7142,
        longitude=4.8075,
        demand=62,
    ),
    113: Customer(
        name="C113",
        city="Cenon",
        state="FR",
        zipcode="",
        latitude=44.8578,
        longitude=-0.5317,
        demand=26,
    ),
    114: Customer(
        name="C114",
        city="Blagnac",
        state="FR",
        zipcode="",
        latitude=43.6364,
        longitude=1.3906,
        demand=39,
    ),
    115: Customer(
        name="C115",
        city="Le Grand-Quevilly",
        state="FR",
        zipcode="",
        latitude=49.4072,
        longitude=1.0531,
        demand=48,
    ),
    116: Customer(
        name="C116",
        city="La Garde",
        state="FR",
        zipcode="",
        latitude=43.1256,
        longitude=6.0108,
        demand=85,
    ),
    117: Customer(
        name="C117",
        city="Gradignan",
        state="FR",
        zipcode="",
        latitude=44.7725,
        longitude=-0.6156,
        demand=49,
    ),
    118: Customer(
        name="C118",
        city="Vichy",
        state="FR",
        zipcode="",
        latitude=46.1278,
        longitude=3.4267,
        demand=65,
    ),
    119: Customer(
        name="C119",
        city="Biarritz",
        state="FR",
        zipcode="",
        latitude=43.48,
        longitude=-1.56,
        demand=49,
    ),
    120: Customer(
        name="C120",
        city="Montbéliard",
        state="FR",
        zipcode="",
        latitude=47.51,
        longitude=6.8,
        demand=48,
    ),
    121: Customer(
        name="C121",
        city="Alençon",
        state="FR",
        zipcode="",
        latitude=48.4306,
        longitude=0.0931,
        demand=80,
    ),
    122: Customer(
        name="C122",
        city="Cherbourg",
        state="FR",
        zipcode="",
        latitude=49.63,
        longitude=-1.62,
        demand=36,
    ),
    123: Customer(
        name="C123",
        city="Béthune",
        state="FR",
        zipcode="",
        latitude=50.5303,
        longitude=2.6408,
        demand=89,
    ),
    124: Customer(
        name="C124",
        city="Castelnau-le-Lez",
        state="FR",
        zipcode="",
        latitude=43.6369,
        longitude=3.9019,
        demand=47,
    ),
    125: Customer(
        name="C125",
        city="Eysines",
        state="FR",
        zipcode="",
        latitude=44.8853,
        longitude=-0.65,
        demand=68,
    ),
    126: Customer(
        name="C126",
        city="Le Bouscat",
        state="FR",
        zipcode="",
        latitude=44.8651,
        longitude=-0.5996,
        demand=82,
    ),
    127: Customer(
        name="C127",
        city="Rodez",
        state="FR",
        zipcode="",
        latitude=44.3506,
        longitude=2.575,
        demand=78,
    ),
    128: Customer(
        name="C128",
        city="Les Pavillons-sous-Bois",
        state="FR",
        zipcode="",
        latitude=48.9,
        longitude=2.5,
        demand=44,
    ),
    129: Customer(
        name="C129",
        city="La Valette-du-Var",
        state="FR",
        zipcode="",
        latitude=43.1383,
        longitude=5.9831,
        demand=39,
    ),
    130: Customer(
        name="C130",
        city="Lormont",
        state="FR",
        zipcode="",
        latitude=44.8792,
        longitude=-0.5217,
        demand=40,
    ),
}
