import frappe
from frappe.utils import flt, fmt_money

def execute(filters=None):
    filters = filters or {}

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

    # Construct conditions for filtering based on Asset fields
    asset_conditions = ""
    if filters.get("department"):
        asset_conditions += " AND asset.department = %(department)s"
    if filters.get("vendor"):
        asset_conditions += " AND asset.custom_vendor = %(vendor)s"
    if filters.get("asset_class"):
        asset_conditions += " AND asset.custom_class = %(asset_class)s"

    # Query to calculate the sum of repair costs from Material Request linked to Work Order and Asset
    repair_costs = frappe.db.sql(f"""
        SELECT SUM(mri.amount) AS total_repair_cost,
               {date_format} AS date
        FROM `tabMaterial Request Item` mri
        JOIN `tabMaterial Request` mr ON mri.parent = mr.name
        JOIN `tabWork_Order` wo ON mr.custom_work_orders = wo.name
        JOIN `tabAsset` asset ON wo.asset = asset.name
        WHERE mr.material_request_type = 'Purchase'
        {asset_conditions}
        GROUP BY {date_format}
    """, filters, as_dict=True)

    # Query to calculate the sum of actual asset costs for the filtered assets
    actual_asset_cost = frappe.db.sql(f"""
        SELECT SUM(asset.gross_purchase_amount) AS total_actual_cost
        FROM `tabAsset` asset
        WHERE 1=1 {asset_conditions}
    """, filters, as_dict=True)[0]

    total_actual_cost = flt(actual_asset_cost['total_actual_cost'])

    # Prepare columns
    columns = [
        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Total Repair Cost",
            "fieldname": "total_repair_cost",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Actual Asset Cost",
            "fieldname": "total_actual_cost",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Repair Cost to Asset Cost Ratio (%)",
            "fieldname": "cost_ratio",
            "fieldtype": "Percent",
            "width": 200
        }
    ]

    # Prepare data for report and chart
    data = []
    chart_labels = []
    chart_values = []
    tooltip_data = []

    for row in repair_costs:
        total_repair_cost = flt(row['total_repair_cost'])
        cost_ratio = round(((total_repair_cost * 100) / total_actual_cost), 2) if total_actual_cost else 0
        data.append({
            "date": row['date'],
            "total_repair_cost": total_repair_cost,
            "total_actual_cost": total_actual_cost,
            "cost_ratio": cost_ratio
        })
        chart_labels.append(row['date'])
        chart_values.append(cost_ratio)
        tooltip_data.append(f"Date: {row['date']}<br>Cost Ratio: {cost_ratio}%<br>"
                            f"Repair Cost: {fmt_money(total_repair_cost)}<br>"
                            f"Actual Asset Cost: {fmt_money(total_actual_cost)}")

    # Define the chart
    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [
                {
                    "name": "Repair Cost to Asset Cost Ratio (%)",
                    "values": chart_values,
                    "type": "bar",
                    "barWidth": 15,
                    "color": "#FF5733"
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "tooltip_options": {
            "enabled": True,
            "custom": {
                "content": lambda tooltip_item: {
                    "title": tooltip_data[tooltip_item['dataIndex']]['date'],
                    "body": [
                        f"Repair Cost: {tooltip_data[tooltip_item['dataIndex']]['repair_cost']}",
                        f"Actual Asset Cost: {tooltip_data[tooltip_item['dataIndex']]['actual_cost']}",
                        #f"Cost Ratio: {tooltip_data[tooltip_item['dataIndex']]['cost_ratio']}"
                    ]
                }
            }
        }
    }

    # Return the report data and chart
    return columns, data, None, chart