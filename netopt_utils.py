import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Circle
import pprint


dpi = 136


def print_dict(data):
    """PrettyPrint the data"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


def print_solution(data):
    """Print some details of the solution"""
    print_dict(data)


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
                each["Flow"],
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
            "Flow",
        ],
    )
    with pd.option_context("display.max_rows", 100):
        print(data.to_markdown())


def plot_map(
    warehouses: dict = dict(),
    customers: dict = dict(),
    flows: set = set(),
    multi_sourced: dict = dict(),
    active_warehouses: set = set(),
    options: dict = dict(),
    hide_inactive: bool = False,
    hide_flows: bool = False,
    plot_size: tuple[int, int] = (8, 12),
    **kwargs,
):
    """Plot the network data
    :param warehouses: list of warehouses
    :param customers: list of customers
    :param flows: plot flows between warehouses and customers
    :param active_warehouses: list of warehouses to be plotted as active
    :param hide_inactive: if true, the warehouses not in the active_warehouses list will be hidden
    :param hide_flows: if true, hide the flows in the plot
    :param multi_sourced: list of customers receiving flows from more than one warehouse. These will be plotted in a different color
    :param plot_size: size of the plot
    :param warehouse_active_marker: shape of the active warehouse icons; allowed values are s=square, o=circle, *=star, ^=triangle, v=inverted triangle
    :param warehouse_active_markercolor: color of the active warehouse icons. Allowed values are red, green, blue, black, yellow
    :param warehouse_active_markersize: size of the active warehouse icons
    :param warehouse_marker: shape of the warehouse icons; allowed values are s=square, o=circle, *=star, ^=triangle, v=inverted triangle
    :param warehouse_markercolor: color of the warehouse icons. Allowed values are red, green, blue, black, yellow
    :param warehouse_markersize: size of the warehouse icons
    :param customer_multisourced_marker: shape of the multisourced customer icons; allowed values are s=square, o=circle, *=star, ^=triangle, v=inverted triangle
    :param customer_multisourced_markercolor: color of the multisourced customer icons. Allowed values are red, green, blue, black, yellow
    :param customer_multisourced_markersize: size of the multisourced customer icons
    :param customer_marker: shape of the customer icons; allowed values are s=square, o=circle, *=star, ^=triangle, v=inverted triangle
    :param customer_markercolor: color of the customer icons. Allowed values are red, green, blue, black, yellow
    :param customer_markersize: size of the customer icons
    :return: plot of the data
    """

    if not multi_sourced:
        multi_sourced = {}

    if not active_warehouses:
        active_warehouses = []

    fig_x, fig_y = plot_size
    fig, ax = plt.subplots(figsize=(fig_x, fig_y), dpi=dpi)
    # plt.figure(figsize=(fig_x, fig_y), dpi=dpi)

    ax.set_aspect("equal")

    # Check if radius is defined and should be plotted
    if radius := options.get("radius", None):
        print(f"PLOTTING RADIUS {radius}...")
        for k, each in warehouses.items():
            if k in active_warehouses:
                circle = Circle(
                    (each.longitude, each.latitude),
                    radius / 100,
                    edgecolor="blue",
                    facecolor="lightblue",
                    fill=True,
                    alpha=0.2,
                    linestyle="-",
                )
                ax.add_patch(circle)
    # Plot flows
    if flows and not hide_flows:
        for flow in flows:
            plt.plot(
                [warehouses[flow[0]].longitude, customers[flow[1]].longitude],
                [warehouses[flow[0]].latitude, customers[flow[1]].latitude],
                color="k",
                linestyle="-",
                linewidth=0.3,
            )

    # Plot customers
    if customers:
        for c_id, each in customers.items():
            # Highlight customers served by multiple suppliers
            if c_id in multi_sourced.keys():
                plt.plot(
                    each.longitude,
                    each.latitude,
                    marker=kwargs.get("customer_multisourced_marker", "*"),
                    color=kwargs.get("customer_multisourced_markercolor", "yellow"),
                    markersize=kwargs.get("customer_multisourced_markersize", 5),
                )
            else:
                plt.plot(
                    each.longitude,
                    each.latitude,
                    marker=kwargs.get("customer_marker", "o"),
                    color=kwargs.get("customer_markercolor", "blue"),
                    markersize=kwargs.get("customer_markersize", 4),
                )

    # Plot warehouses
    if warehouses:
        for k, each in warehouses.items():
            if k in active_warehouses:
                plt.plot(
                    each.longitude,
                    each.latitude,
                    marker=kwargs.get("warehouse_active_marker", "v"),
                    color=kwargs.get("warehouse_active_markercolor", "green"),
                    markersize=kwargs.get("warehouse_active_markersize", 5),
                )
            else:
                if not hide_inactive:
                    plt.plot(
                        each.longitude,
                        each.latitude,
                        marker=kwargs.get("warehouse_marker", "s"),
                        color=kwargs.get("warehouse_markercolor", "red"),
                        markersize=kwargs.get("warehouse_markersize", 4),
                    )

    # Remove axes
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    ####################

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(-20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)

    def update_annot(ind):
        x, y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = "{}, {}".format(
            " ".join(list(map(str, ind["ind"]))),
            " ".join([names[n] for n in ind["ind"]]),
        )
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()
    ############
