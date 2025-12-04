# Copyright (c) 2024, seyfert and contributors
# For license information, please see license.txt

import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"label": "Sum of Total Hours", "fieldname": "total_hours", "fieldtype": "Float", "width": 150},
        {"label": "Sum of Downtime", "fieldname": "downtime", "fieldtype": "Float", "width": 150},
        {"label": "Downtime Percentage", "fieldname": "percentage", "fieldtype": "Percent", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    # Apply filters for supplier if provided
    supplier_condition = ""
    if filters.get("supplier"):
        supplier_condition = f"AND a.custom_vendor = '{filters.get('supplier')}'"

    # Fetch the Sum of Total Hours and Downtime grouped by Supplier
    results = frappe.db.sql(f"""
        SELECT
            a.custom_vendor AS supplier,
            SUM(a.custom_total_hours) AS total_hours,
            SUM(a.custom_down_time) AS downtime
        FROM
            `tabAsset` a
        WHERE
            a.docstatus = 1
            {supplier_condition}
        GROUP BY
            a.custom_vendor
        ORDER BY
            total_hours DESC
    """, as_dict=True)

    # Prepare the data
    data = []
    for row in results:
        total_hours = row.get("total_hours", 0)
        downtime = row.get("downtime", 0)

        # Calculate percentage
        percentage = round((downtime / total_hours * 100), 2) if total_hours > 0 else 0

        # Determine status based on percentage
        if percentage <= 30:
            status = "Excellent"
        elif 30 < percentage <= 50:
            status = "Average"
        elif 50 < percentage <= 80:
            status = "Poor"
        elif 80 < percentage <= 100:
            status = "Very Poor"
        else:
            status = "Critical"

        # Append to data
        data.append({
            "supplier": row["supplier"],
            "total_hours": total_hours,
            "downtime": downtime,
            "percentage": percentage,
            "status": status,
        })

        # Sort data by percentage in ascending order
        data.sort(key=lambda x: x["percentage"])

    return data
