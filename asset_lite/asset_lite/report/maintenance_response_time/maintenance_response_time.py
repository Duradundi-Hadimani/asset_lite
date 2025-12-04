import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}

    # Construct conditions for filtering based on Asset fields
    asset_conditions = ""
    if filters.get("department"):
        asset_conditions += " AND asset.department = %(department)s"
    if filters.get("vendor"):
        asset_conditions += " AND asset.custom_vendor = %(vendor)s"
    if filters.get("asset_class"):
        asset_conditions += " AND asset.custom_class = %(asset_class)s"

    # Determine the grouping format based on periodicity
    periodicity = filters.get("periodicity", "Monthly")
    if periodicity == "Quarterly":
        date_format = "CONCAT(YEAR(wo.failure_date), ' Q', QUARTER(wo.failure_date))"
    elif periodicity == "Half-Yearly":
        date_format = "CONCAT(YEAR(wo.failure_date), ' H', IF(MONTH(wo.failure_date) <= 6, 1, 2))"
    elif periodicity == "Yearly":
        date_format = "YEAR(wo.failure_date)"
    else:  # Default to Monthly
        date_format = "DATE_FORMAT(wo.failure_date, '%%m-%%Y')"

    # Query to fetch the overall average response times and count of work orders
    overall_response_times = frappe.db.sql(f"""
        SELECT {date_format} AS period,
               COUNT(wo.name) AS total_work_orders,
               AVG(TIMESTAMPDIFF(HOUR, wo.failure_date, wo.first_responded_on)) AS average_response_time
        FROM `tabWork_Order` wo
        JOIN `tabAsset` asset ON wo.asset = asset.name
        WHERE wo.failure_date IS NOT NULL 
              AND wo.first_responded_on IS NOT NULL
        GROUP BY period
    """, filters, as_dict=True)

    # Query to fetch vendor-specific response times (if vendor filter is applied)
    vendor_response_times = []
    if filters.get("vendor"):
        vendor_response_times = frappe.db.sql(f"""
            SELECT {date_format} AS period,
                   AVG(TIMESTAMPDIFF(HOUR, wo.failure_date, wo.first_responded_on)) AS vendor_average_response_time
            FROM `tabWork_Order` wo
            JOIN `tabAsset` asset ON wo.asset = asset.name
            WHERE wo.failure_date IS NOT NULL 
                  AND wo.first_responded_on IS NOT NULL
                  AND asset.custom_vendor = %(vendor)s
            GROUP BY period
        """, filters, as_dict=True)

    # Prepare columns
    columns = [
        {"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 150},
        {"label": "Total Work Orders", "fieldname": "total_work_orders", "fieldtype": "Int", "width": 150},
        {"label": "Overall Avg Response Time (Hours)", "fieldname": "average_response_time", "fieldtype": "Float", "width": 200},
    ]

    if filters.get("vendor"):
        columns.append({"label": "Vendor Avg Response Time (Hours)", "fieldname": "vendor_average_response_time", "fieldtype": "Float", "width": 200})

    # Prepare data
    data = []
    labels = []
    avg_response_times = []
    total_work_orders_list = []
    vendor_avg_response_times = {}

    # Store vendor-specific response times in a dictionary for quick lookup
    for row in vendor_response_times:
        # vendor_avg_response_times[row["period"]] = flt(row["vendor_average_response_time"])
        vendor_avg_response_times[row["period"]] = round(flt(row["vendor_average_response_time"]), 2)

    for row in overall_response_times:
        period_label = row["period"]
        total_work_orders = row["total_work_orders"]
        # average_response_time = flt(row["average_response_time"])
        # vendor_avg_time = vendor_avg_response_times.get(period_label, None)  # Get vendor-specific time or None
        average_response_time = round(flt(row["average_response_time"]), 2)
        vendor_avg_time = round(vendor_avg_response_times.get(period_label, 0), 2) if period_label in vendor_avg_response_times else None


        labels.append(period_label)
        avg_response_times.append(average_response_time)
        total_work_orders_list.append(total_work_orders)

        row_data = {
            "period": period_label,
            "total_work_orders": total_work_orders,
            "average_response_time": average_response_time,
        }

        if filters.get("vendor"):
            row_data["vendor_average_response_time"] = vendor_avg_time

        data.append(row_data)

    # Define the chart configuration with three datasets
    chart_datasets = [
        {
            "name": "Overall Avg Response Time (Hours)",
            "values": avg_response_times
        },
        {
            "name": "Total Work Orders",
            "values": total_work_orders_list
        }
    ]

    if filters.get("vendor"):
        # vendor_values = [vendor_avg_response_times.get(period, None) for period in labels]
        vendor_values = [round(vendor_avg_response_times.get(period, 0), 2) for period in labels]
        chart_datasets.append({
            "name": f"Vendor Avg Response Time ({filters.get('vendor')})",
            "values": vendor_values
        })

    chart = {
        "data": {
            "labels": labels,
            "datasets": chart_datasets
        },
        "type": "line",
        "colors": ["#FF5733", "#33B5FF", "#28A745"]  # Optional: Different colors
    }

    return columns, data, None, chart
