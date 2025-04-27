# ==============================================================================
# description     :Support functions
# author          :Roberto Pinto
# date            :2022.04.21
# version         :1.2
# notes           :This software is meant for teaching purpose only and it is provided as-is under the GPL license.
# ==============================================================================

from collections import namedtuple
from math import sqrt
from typing import Optional
import pandas as pd
from haversine import haversine, Unit
import folium


Warehouse = namedtuple(
    "Warehouse", "name, city, state, zipcode, latitude, longitude, capacity, fixed_cost"
)

Customer = namedtuple(
    "Customer", "name, city, state, zipcode, latitude, longitude, demand"
)

Factory = namedtuple(
    "Factory",
    "name, city, state, zipcode, latitude, longitude, capacity, fixed_cost",
)


def import_data(data, datatype):
    """Importa data from a variable.
    The <data> parameter must be a list of strings containing values separated by ';'
    The data must be in this order:
        - Warehouse: "IDENTIFIER;LATITUDE;LONGITUDE;CAPACITY;FIXED_COST"
        - Customer: "IDENTIFIER;LATITUDE;LONGITUDE;DEMAND"
    Latitude is represented along the y-axis, whereas the longitude is represented along the x-axis
    All values are required: if fixed costs are not relevant, set them to zero (do not omit)
    Use -1 to represent infinite capacity for the warehouses
    Parameter <datatype> must be either 'warehouse' or 'customer'
    It returns a variable containing all the data that can be used in the optimization function
    """

    if datatype not in ["warehouse", "customer"]:
        raise Exception("Parameter datatype must be either warehouse or customer")
    if not isinstance(data, list):
        raise Exception(
            "Parameter data must be a list of either warehouse or customer data"
        )

    imported_data = {}

    for n, each in enumerate(data):
        row = each.split(";")

        if row[3] in [-1, "-1"]:
            q = None
        else:
            q = float(row[3])

        if datatype == "warehouse":
            try:
                fixed_cost = float(row[4])
            except (ValueError, TypeError, IndexError):
                print(
                    f"The warehouse {row[0]} fixed cost is not valid or missing: set to zero"
                )
                fixed_cost = 0.0

            imported_data[n] = Warehouse(
                name=row[0],
                city=row[0],
                state="",
                zipcode="",
                latitude=float(row[1]),
                longitude=float(row[2]),
                capacity=q,
                fixed_cost=fixed_cost,
            )
        elif datatype == "customer":
            imported_data[n] = Customer(
                name=row[0],
                city=row[0],
                state="",
                zipcode="",
                latitude=float(row[1]),
                longitude=float(row[2]),
                demand=q,
            )

    return imported_data


def dist(origin: Warehouse, destination: Customer) -> float:
    """Return the distance between origin and destination.
    origin must be of type Warehouse, whereas destination must be of type Customer"""

    if isinstance(origin, Warehouse) and isinstance(destination, Customer):
        return sqrt(
            (origin.latitude - destination.latitude) ** 2
            + (origin.longitude - destination.longitude) ** 2
        )


def calculate_dm(warehouses: dict, customers: dict, use_haversine: bool = True) -> dict:
    """Calculate the distance matrix between warehouses and customers using the haversine formula
    :param warehouses: dict of warehouses
    :param customers: dict of customers
    :return: distance matrix
    """

    if not all([warehouses, customers]):
        raise Exception("You must pass the location of warehouses and customers")

    dm = {}

    for kw, w in warehouses.items():
        for kc, c in customers.items():
            if use_haversine:
                dm[(kw, kc)] = haversine(
                    (w.latitude, w.longitude),
                    (c.latitude, c.longitude),
                    unit=Unit.KILOMETERS,
                )
            else:
                dm[(kw, kc)] = dist(w, c)

    return dm


def show_data(data: dict) -> None:
    """Print the data in a readable format"""
    with pd.option_context("display.max_rows", 100):
        if not isinstance(data, dict):
            raise Exception("Param data must be a dict")
        df = []
        for k, v in data.items():
            df.append([k] + list(v))
        if isinstance(data[list(data.keys())[0]], Warehouse):
            df = pd.DataFrame(
                df,
                columns=[
                    "Id",
                    "Identifier",
                    "City",
                    "State",
                    "Zipcode",
                    "Latitude",
                    "Longitude",
                    "Capacity",
                    "Yearly fixed cost",
                ],
            )
        elif isinstance(data[list(data.keys())[0]], Customer):
            df = pd.DataFrame(
                df,
                columns=[
                    "Id",
                    "Identifier",
                    "City",
                    "State",
                    "Zipcode",
                    "Latitude",
                    "Longitude",
                    "Yearly demand",
                ],
            )

        df = df.drop(["State", "Zipcode"], axis=1)
        print(df.to_markdown())


def set_capacity(warehouses: dict, w_id: int, capacity: int | float) -> None:
    """Change the capacity of a warehouse. It changes the warehouses dict in place by producing a new nametuple Warehouse changing only the capacity
    :param warehouses: list of warehouses
    :param w_id: id of the warehouse to be modified
    :param capacity: new capacity for the warehouse
    :return: changes the warehouse list in place, do not return data
    """

    if w_id not in warehouses.keys():
        return None

    warehouse = warehouses[w_id]
    warehouses[w_id] = Warehouse(
        name=warehouse.name,
        city=warehouse.city,
        state=warehouse.state,
        zipcode=warehouse.zipcode,
        latitude=warehouse.latitude,
        longitude=warehouse.longitude,
        capacity=capacity,
        fixed_cost=warehouse.fixed_cost,
    )


def set_all_capacities(warehouses: dict, capacity: int | float) -> None:
    """Change the capacity of all warehouses with the given capacity
    :param warehouses: list of warehouses
    :param capacity: new capacity for the warehouses
    :return: changes the warehouse list in place, do not return data
    """
    for k in warehouses.keys():
        set_capacity(warehouses, k, capacity)


def set_fixed_cost(warehouses: dict, w_id: int, fixed_cost: int | float) -> None:
    """Change the yearly fixed_cost of the warehouse. It changes the warehouses dict in place by producing a new nametuple Warehouse changing only the fixed_cost
    :param warehouses: list of warehouses
    :param w_id: id of the warehouse to be modified
    :param fixed_cost: new fixed cost for the warehouse
    :return: changes the warehouse list in place, do not return data
    """

    if w_id not in warehouses.keys():
        return None

    warehouse = warehouses[w_id]
    warehouses[w_id] = Warehouse(
        name=warehouse.name,
        city=warehouse.city,
        state=warehouse.state,
        zipcode=warehouse.zipcode,
        latitude=warehouse.latitude,
        longitude=warehouse.longitude,
        capacity=warehouse.capacity,
        fixed_cost=fixed_cost,
    )


def set_all_fixed_costs(warehouses: dict, fixed_cost: int | float) -> None:
    """Change the fixed_cost of all warehouses with the given fixed_cost
    :param warehouses: list of warehouses
    :param fixed_cost: new fixed cost for the warehouses
    :return: changes the warehouse list in place, do not return data
    """
    for k in warehouses.keys():
        set_fixed_cost(warehouses, k, fixed_cost)


def scale_demand(customers: dict, c_id: int, factor: float = 1.0) -> None:
    """scale a customer demand by factor
    :param customers: list of customers
    :param c_id: id of the customer to be modified
    :param factor: scaling factor for the demand. The function return the list of customers with each demand multiplied by factor (rounded to integer)
    :return: changes the customer list in place, do not return data
    """

    if c_id not in customers.keys():
        return None

    customer = customers[c_id]
    customers[c_id] = Customer(
        name=customer.name,
        city=customer.city,
        state=customer.state,
        zipcode=customer.zipcode,
        latitude=customer.latitude,
        longitude=customer.longitude,
        demand=round(customer.demand * factor, 0),
    )


def scale_all_demands(customers: dict, factor: float = 1.0) -> None:
    """scale all customer demands
    :param customers: list of customers
    :param factor: scaling factor for the demand. The function return the list of customers with each demand multiplied by factor (rounded to integer)
    :return: changes the customer list in place, do not return data
    """
    if not customers:
        raise Exception("You must pass the list of customers as a parameter")

    for k in customers.keys():
        scale_demand(customers, k, factor)


def set_demand(customers: dict, c_id: int, demand: int | float = 0.0) -> None:
    """set a customer demand
    :param customers: list of customers
    :param c_id: id of the customer to be modified
    :param demand: new demand for the customer. The function return the list of customers with each demand multiplied by factor (rounded to integer)
    :return: changes the customer list in place, do not return data
    """

    if c_id not in customers.keys():
        return None

    customer = customers[c_id]
    customers[c_id] = Customer(
        name=customer.name,
        city=customer.city,
        state=customer.state,
        zipcode=customer.zipcode,
        latitude=customer.latitude,
        longitude=customer.longitude,
        demand=demand,
    )


def set_all_demands(customers: dict, demand: int | float = 0) -> None:
    """set all customer demands
    :param customers: list of customers
    :param demand: new demand for all customers. The function return the list of customers with each demand multiplied by factor (rounded to integer)
    :return: changes the customer list in place, do not return data
    """
    for k in customers.keys():
        set_demand(customers, k, demand)


def show_assignments(results):
    """Display the customers assigned to each active warehouse in a tabular format
    :param results: the results of an optimization run
    """
    data = []
    for each in results["customers_assignment"]:
        data.append(
            [
                each["Warehouse_id"],
                each["Warehouse"],
                each["Customer_id"],
                each["Customer"],
                each["Customer Demand"],
                each["Distance"],
            ]
        )

    data = pd.DataFrame(
        data=data,
        columns=[
            "Warehouse_id",
            "Warehouse",
            "Customer_id",
            "Customer",
            "Customer_demand",
            "Distance",
        ],
    )
    with pd.option_context("display.max_rows", 100):
        print(data.to_markdown())


def get_demand(customers: dict) -> float:
    """Return the demand of a set of customers"""
    tot = 0
    for each in customers.values():
        tot += each.demand
    return tot


def get_capacity(warehouses: dict) -> float:
    """Return the capacity of a set of warehouses"""
    tot = 0
    for each in warehouses.values():
        tot += each.capacity
    return tot


def show_geo_map(
    customers: Optional[dict] = None,
    warehouses: Optional[dict] = None,
    flows: list | None = None,
    zoom: int = 8,
) -> folium.Map:
    """Show the map with the locations of customers and warehouses (if provided)"""

    # Convert data to be displayed
    _customers = []
    _warehouses = []

    if customers:
        for _, each in customers.items():
            _customers.append(
                {
                    "name": each.name,
                    "city": each.city,
                    "location": [each.latitude, each.longitude],
                    "demand": each.demand,
                }
            )

    if warehouses:
        for _, each in warehouses.items():
            _warehouses.append(
                {
                    "name": each.name,
                    "city": each.city,
                    "location": [each.latitude, each.longitude],
                    "capacity": each.capacity,
                }
            )

    # Create Map
    if _customers:
        map = folium.Map(location=_customers[0]["location"], zoom_start=zoom)
    else:
        map = folium.Map(location=_warehouses[0]["location"], zoom_start=zoom)

    if flows:
        for each in flows:
            folium.PolyLine(
                locations=[
                    [
                        _warehouses[each[0]]["location"][0],
                        _warehouses[each[0]]["location"][1],
                    ],
                    [
                        _customers[each[1]]["location"][0],
                        _customers[each[1]]["location"][1],
                    ],
                ],
                color="blue",
                weight=2,
                opacity=0.5,
            ).add_to(map)

    if _customers:
        for each in _customers:
            folium.Marker(
                location=each["location"],
                popup=f"{each['name']} - {each['city']}\n\r Demand: {each['demand']}",
                icon=folium.Icon(color="green"),
            ).add_to(map)

    if _warehouses:
        for each in _warehouses:
            folium.Marker(
                location=each["location"],
                popup=f"{each['name']} - {each['city']}\n\r Capacity: {each['capacity']}",
                icon=folium.Icon(color="red"),
            ).add_to(map)

    return map


def add_warehouse(warehouses: dict | None, new_warehouse: Warehouse) -> None:
    """Add a warehouse to the list of warehouses
    :param warehouses: current set of warehouses
    :param new_warehouse: new warehouse to be added"""
    if warehouses is None or not isinstance(warehouses, dict):
        raise Exception("<add_warehouse> The parameter warehouses must be a dictionary")
    warehouses[len(warehouses)] = new_warehouse


def add_customer(customers: dict | None, new_customer: Customer) -> None:
    """Add a customer to the list of customers
    :param customers: current set of customers
    :param new_customer: new customer to be added"""
    if customers is None or not isinstance(customers, dict):
        raise Exception("The parameter customers must be a dictionary")
    customers[len(customers)] = new_customer


def add_warehouse_from_data(
    warehouses: dict | None = None,
    name: str = "",
    city: str = "",
    state: str = "",
    zipcode: str = "",
    latitude: float = 0.0,
    longitude: float = 0.0,
    capacity: float = 0.0,
    fixed_cost: float = 0.0,
) -> None:
    """Add a warehouse to the list of warehouses from data
    :param warehouses: current set of warehouses"""

    if not isinstance(warehouses, dict):
        raise Exception("The parameter warehouses must be a dictionary")

    if not all([name, latitude, longitude]):
        print(f"{name=} - {latitude=} - {longitude=}")
        raise Exception("All parameters are required")

    # check range of latitude and longitude
    if latitude < -90 or latitude > 90:
        raise Exception("Latitude must be between -90 and 90")
    if longitude < -180 or longitude > 180:
        raise Exception("Longitude must be between -180 and 180")

    if list(filter(lambda x: x.name == name, warehouses.values())):
        print(
            f"The warehouse name {name} already exists. Warehouse's name must be unique"
        )
        return None

    new_warehouse = Warehouse(
        name=name,
        city=city,
        state=state,
        zipcode=zipcode,
        latitude=latitude,
        longitude=longitude,
        capacity=capacity,
        fixed_cost=fixed_cost,
    )

    add_warehouse(warehouses=warehouses, new_warehouse=new_warehouse)


def add_customer_from_data(
    customers: dict | None = None,
    name: str = "",
    city: str = "",
    state: str = "",
    zipcode: str = "",
    latitude: float = 0.0,
    longitude: float = 0.0,
    demand: float = 0.0,
) -> None:
    """Add a customer to the list of customers from data
    :param customers: current set of customers"""

    if not isinstance(customers, dict):
        raise Exception("The parameter customers must be a dictionary")

    if not all([name, latitude, longitude]):
        raise Exception("All parameters are required")

    # check range of latitude and longitude
    if latitude < -90 or latitude > 90:
        raise Exception("Latitude must be between -90 and 90")
    if longitude < -180 or longitude > 180:
        raise Exception("Longitude must be between -180 and 180")

    if list(filter(lambda x: x.name == name, customers.values())):
        print(
            f"The customer name {name} already exists. Customer's name must be unique"
        )
        return None

    new_customer = Customer(
        name=name,
        city=city,
        state=state,
        zipcode=zipcode,
        latitude=latitude,
        longitude=longitude,
        demand=demand,
    )

    add_customer(customers=customers, new_customer=new_customer)
