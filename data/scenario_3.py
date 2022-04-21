from random import randint
from math import sqrt
from data_structures import Warehouse, Customer


def d(lat_1, lon_1, lat_2, lon_2):
    return sqrt(
        (lat_1 - lat_2)**2 + (lon_1 - lon_2)**2
    )

num_customers = 300
num_candidates = 48

c1 = (500, 500)
c2 = (1000, 1000)

def generate_location():
    for k in range(1000):
        p = (randint(0, 2500), randint(0, 2500), 10)
        if d(p[0], p[1], c1[0], c1[1]) > 150 and d(p[0], p[1], c2[0], c2[1]) > 150:
            return p
    return p

customers = {i: generate_location() for i in range(num_customers - 1)}
customers[num_customers-1] = (0, 0, 300)

warehouses = {i: (randint(0, 2500), randint(0, 2500)) for i in range(num_candidates)}

for n, v in customers.items():
    customers[n] = Customer(name=n,
                            city=n,
                            state=n,
                            latitude=v[0],
                            longitude=v[1],
                            demand=v[2],
                            zipcode=None)

for n, v in warehouses.items():
    warehouses[n] = Warehouse(name=n,
                              city=n,
                              state=n,
                              latitude=v[0],
                              longitude=v[1],
                              zipcode=None,
                              capacity=None)

distance = {(w_id, c_id): d(w.latitude, w.longitude, c.latitude, c.longitude) for w_id, w in warehouses.items() for c_id, c in customers.items()}




