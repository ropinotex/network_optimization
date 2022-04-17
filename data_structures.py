# ==============================================================================
# description     :Optimization models for teaching purposes
# author          :Roberto Pinto
# date            :2022.03.22
# version         :1.0
# notes           :This software is meant for teaching purpose only and it is provided as-is under the GPL license.
#                  The models are inspired by the book Watson, M., Lewis, S., Cacioppi, P., Jayaraman, J. (2013)
#                  Supply Chain Network Design, Pearson. 
#                  http://networkdesignbook.com/
#                  All the data has been taken from the book.
#                  The software is provided as-is, with no guarantee by the author.
# ==============================================================================

from collections import namedtuple
from math import sqrt
import pandas as pd
from haversine import haversine


Warehouse = namedtuple('Warehouse', 'name, city, state, zipcode, latitude, longitude, capacity')
Customer = namedtuple('Customer', 'name, city, state, zipcode, latitude, longitude, demand')

def import_data(data, datatype):
    """ Importa data from a variable. 
        The data parameter must be a list of strings containing values separated by ';'
        The data must be in this order:
            - Warehouse: "IDENTIFIER;X_COORD;Y_COORD;CAPACITY"
            - Customer: "IDENTIFIER;X_COORD;Y_COORD;DEMAND"
        Use -1 to represent infinite capacity
        Parameter datatype refers to either warehouse or customer
        It returns a variable containing all the data that can be used in the optimization function"""

    if datatype not in ['warehouse', 'customer']:
        raise Exception('Parameter datatype must be either warehouse or customer')
    if not isinstance(data, list):
        raise Exception('Parameter data must be a list of either warehouse or customer data')

    imported_data = {}

    for n, each in enumerate(data):
        row = each.split(';')

        if row[3] in [-1, '-1']:
            q = None
        else:
            q = float(row[3])

        if datatype == 'warehouse':
            imported_data[n] = Warehouse(name=row[0],
                                         city=row[0],
                                         state="",
                                         zipcode="",
                                         latitude=float(row[1]),
                                         longitude=float(row[2]),
                                         capacity=q)
        elif datatype == 'customer':
            imported_data[n] = Customer(name=row[0],
                                        city=row[0],
                                        state="",
                                        zipcode="",
                                        latitude=float(row[1]),
                                        longitude=float(row[2]),
                                        demand=q)
    
    return imported_data

def dist(origin, destination):
    """ Return the distance between origin and destination.
        origin must be of type Warehouse, whereas destination must be of type Customer"""

    if isinstance(origin, Warehouse) and isinstance(destination, Customer):
        return sqrt((origin.latitude - destination.latitude)**2 + (origin.longitude - destination.longitude)**2)


def calculate_dm(warehouses=None, customers=None):
    """ Calculate the distance matrix between warehouses and customers"""

    if not all([warehouses, customers]):
        raise Exception('You must pass the location of warehouses and customers')
    
    dm = {}

    for kw, w in warehouses.items():
        for kc, c in customers.items():
            dm[(kw, kc)] = haversine((w.longitude, w.latitude), (c.longitude, c.latitude))

    return dm

def show_data(data):
    """ Print the data in a readable format """
    if not isinstance(data, dict):
        raise Exception('Param data must be a dict')
    df = []
    for k, v in data.items():
        df.append([k] + list(v))

    df = pd.DataFrame(df, columns=['Id', 'Identifier', 'City', 'State', 'Zipcode', 'x', 'y', 'Capcity/Demand'])
    return df
