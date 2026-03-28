import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle
import pprint
from IPython.display import display, HTML


dpi = 136


def print_dict(data):
    """PrettyPrint the data"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)


def print_solution(data):
    """Print some details of the solution"""
    print_dict(data)


def show_results_summary(result: dict, warehouses: dict = None):
    """Display an HTML summary card of the optimization results.
    :param result: the solution dictionary returned by the optimizer
    :param warehouses: optional dict of Warehouse objects (needed for state and capacity info)
    """
    if not result:
        display(
            HTML(
                '<p style="font-family:sans-serif;color:#dc3545">No solution available.</p>'
            )
        )
        return

    status = result.get("status", "Unknown")
    status_color = "#28a745" if status == "Optimal" else "#dc3545"

    _S = "font-family:sans-serif"  # base style shorthand

    # --- Key metrics table ---
    rows = []

    wh_ids = result.get("active_warehouses_id", set())
    total_warehouses = len(warehouses) if warehouses else "?"
    rows.append(("Open facilities", f"<b>{len(wh_ids)}</b> out of {total_warehouses}"))

    if "avg_weighted_distance" in result:
        rows.append(
            (
                "Avg weighted distance",
                f"<b>{result['avg_weighted_distance']:.1f}</b> km",
            )
        )
    if "avg_customer_distance" in result:
        rows.append(
            ("Avg distance (unweighted)", f"{result['avg_customer_distance']:.1f} km")
        )
    if "most_distant_customer" in result:
        rows.append(
            ("Most distant customer", f"{result['most_distant_customer']:.1f} km")
        )

    multi = result.get("multi_sourced_customers", [])
    if multi:
        rows.append(("Multi-sourced customers", ", ".join(str(c) for c in multi)))

    metrics_html = "".join(
        f"<tr>"
        f'<td style="padding:5px 16px 5px 0;color:#555;font-size:13px;white-space:nowrap">{label}</td>'
        f'<td style="padding:5px 0;font-size:13px">{value}</td>'
        f"</tr>"
        for label, value in rows
    )

    # --- Per-warehouse detail table ---
    wh_stats = {}
    for rec in result.get("customers_assignment", []):
        wid = rec["Warehouse_id"]
        if wid not in wh_stats:
            w_obj = warehouses.get(wid) if warehouses else None
            wh_stats[wid] = {
                "city": rec["Warehouse"],
                "state": getattr(w_obj, "state", "") if w_obj else "",
                "capacity": getattr(w_obj, "capacity", None) if w_obj else None,
                "n_customers": 0,
                "outflow": 0.0,
            }
        wh_stats[wid]["n_customers"] += 1
        wh_stats[wid]["outflow"] += rec["Flow"]

    total_outflow = sum(s["outflow"] for s in wh_stats.values())

    _th = (
        'style="padding:5px 14px 5px 0;font-size:12px;color:#666;font-weight:600;'
        'border-bottom:1px solid #ccc;white-space:nowrap;text-align:left"'
    )
    _td = 'style="padding:4px 14px 4px 0;font-size:13px;white-space:nowrap"'
    _td_r = 'style="padding:4px 14px 4px 0;font-size:13px;text-align:right"'

    wh_rows_html = ""
    for wid in sorted(wh_stats):
        s = wh_stats[wid]
        cap_cell = ""
        if s["capacity"]:
            util_pct = s["outflow"] / s["capacity"] * 100
            bar_color = (
                "#28a745"
                if util_pct <= 80
                else "#ffc107"
                if util_pct <= 95
                else "#dc3545"
            )
            cap_cell = (
                f"<td {_td_r}>"
                f"{util_pct:.1f}%&nbsp;"
                f'<span style="font-size:11px;color:#888">({int(s["outflow"]):,}&nbsp;/&nbsp;{s["capacity"]:,})</span>'
                f"</td>"
            )
        else:
            cap_cell = f'<td {_td_r} style="color:#aaa;font-size:12px">—</td>'

        wh_rows_html += (
            f"<tr>"
            f"<td {_td}><b>{wid}</b></td>"
            f"<td {_td}>{s['city']}</td>"
            f"<td {_td}>{s['state']}</td>"
            f"<td {_td_r}>{s['n_customers']:,}</td>"
            f"<td {_td_r}>{int(s['outflow']):,}</td>"
            f"{cap_cell}"
            f"</tr>"
        )

    has_capacity = any(s["capacity"] for s in wh_stats.values())
    cap_header = f"<th {_th}>Capacity util.</th>" if has_capacity else ""

    warehouses_html = f"""
    <div style="margin-top:14px;padding-top:12px;border-top:1px solid #e0e0e0">
      <div style="font-size:13px;font-weight:600;color:#333;margin-bottom:6px">
        Open warehouses ({len(wh_stats)})
      </div>
      <table style="border-collapse:collapse">
        <thead>
          <tr>
            <th {_th}>ID</th>
            <th {_th}>City</th>
            <th {_th}>State</th>
            <th {_th} style="text-align:right">Customers</th>
            <th {_th} style="text-align:right">Outflow (units)</th>
            {cap_header}
          </tr>
        </thead>
        <tbody>{wh_rows_html}</tbody>
        <tfoot>
          <tr>
            <td colspan="4" style="padding:5px 14px 3px 0;font-size:13px;
                font-weight:600;border-top:1px solid #ccc">Total outflow</td>
            <td style="padding:5px 0 3px;font-size:13px;font-weight:600;
                text-align:right;border-top:1px solid #ccc">{int(total_outflow):,}</td>
            {'<td style="border-top:1px solid #ccc"></td>' if has_capacity else ""}
          </tr>
        </tfoot>
      </table>
    </div>"""

    # --- Demand by distance ranges ---
    ranges_html = ""
    if "demand_perc_by_ranges" in result:
        range_rows = "".join(
            f"<tr>"
            f'<td style="padding:3px 16px 3px 0;color:#555;font-size:13px">{lo:,} – {hi:,} km</td>'
            f'<td style="padding:3px 0;font-size:13px"><b>{perc * 100:.1f}%</b></td>'
            f"</tr>"
            for (lo, hi), perc in result["demand_perc_by_ranges"].items()
        )
        ranges_html = f"""
        <div style="margin-top:14px;padding-top:12px;border-top:1px solid #e0e0e0">
          <div style="font-size:13px;font-weight:600;color:#333;margin-bottom:4px">Demand coverage by distance</div>
          <table style="border-collapse:collapse">{range_rows}</table>
        </div>"""

    html = f"""
    <div style="{_S};border:1px solid #d0d0d0;border-radius:8px;
                padding:16px 20px;margin:10px 0 6px;background:#f8f9fa">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <span style="font-size:15px;font-weight:700;color:#1a1a1a">Optimization Results</span>
        <span style="background:{status_color};color:white;padding:2px 10px;
                     border-radius:12px;font-size:11px;font-weight:700;letter-spacing:.5px">
          {status.upper()}
        </span>
      </div>
      <table style="border-collapse:collapse">{metrics_html}</table>
      {warehouses_html}
      {ranges_html}
    </div>"""

    display(HTML(html))


def show_assignments(result: dict):
    """Display the customer-to-warehouse assignments as a formatted table.
    :param result: the solution dictionary returned by the optimizer
    """
    if not result or "customers_assignment" not in result:
        display(
            HTML(
                '<p style="font-family:sans-serif;color:#666">No assignment data available.</p>'
            )
        )
        return

    rows = [
        {
            "WH ID": each["Warehouse_id"],
            "Warehouse": each["Warehouse"],
            "Cust. ID": each["Customer_id"],
            "Customer": each["Customer"],
            "Demand": each["Customer Demand"],
            "Distance (km)": round(each["Distance"], 1),
            "Flow": round(each["Flow"], 0),
        }
        for each in result["customers_assignment"]
    ]

    df = pd.DataFrame(rows).sort_values(["WH ID", "Cust. ID"]).reset_index(drop=True)

    display(
        HTML(
            '<div style="font-family:sans-serif;font-size:14px;font-weight:600;'
            'color:#1a1a1a;margin:14px 0 6px">Customer Assignments</div>'
        )
    )
    with pd.option_context("display.max_rows", 500):
        display(df)


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
        print(f"PLOTTING RADIUS (approx) {radius}...")
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
