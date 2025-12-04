# Copyright (c) 2025, seyfert and contributors
# For license information, please see license.txt

# import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data


import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}

    # Construct conditions for filtering based on Asset fields
    asset_conditions = ""
    if filters.get("department"):
        asset_conditions += " AND asset.department = %(department)s"
    if filters.get("asset"):
        asset_conditions += " AND asset.name = %(asset)s"
    if filters.get("asset_class"):
        asset_conditions += " AND asset.custom_class = %(asset_class)s"
    if filters.get("vendor"):
        asset_conditions += " AND asset.custom_vendor = %(vendor)s"

    # Query to calculate sum of uptime and downtime hours grouped by asset and available for use date
    uptime_downtime = frappe.db.sql("""
        SELECT 
            asset.name AS asset_name,
			asset.asset_name AS asset,
            DATE_FORMAT(asset.available_for_use_date, '%%m-%%Y') AS available_date,
            SUM(asset.custom_up_time) AS total_uptime_hours,
            SUM(asset.custom_down_time) AS total_downtime_hours
        FROM `tabAsset` asset
        
        WHERE 1=1 {asset_conditions}
        GROUP BY asset.asset_name,asset.custom_vendor,asset.department
    """.format(asset_conditions=asset_conditions), filters, as_dict=True)

    # Prepare columns
    columns = [
        {
            "label": "Asset",
            "fieldname": "asset_name",
            "fieldtype": "Link",
			"options":"Asset",
            "width": 150
        },
		 {
            "label": "Asset Name",
            "fieldname": "asset",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Available Date",
            "fieldname": "available_date",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Total Uptime Hours",
            "fieldname": "total_uptime_hours",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Total Downtime Hours",
            "fieldname": "total_downtime_hours",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Uptime to Downtime Ratio",
            "fieldname": "uptime_downtime_ratio",
            "fieldtype": "Float",
            "width": 200
        }
    ]

    # Prepare data
    data = []
    for row in uptime_downtime:
        total_uptime_hours = flt(row['total_uptime_hours'])
        total_downtime_hours = flt(row['total_downtime_hours'])
        ratio = (total_uptime_hours / total_downtime_hours) if total_downtime_hours else 0
        data.append({
            "asset_name": row['asset_name'],
			"asset": row['asset'],
            "available_date": row['available_date'],
            "total_uptime_hours": total_uptime_hours,
            "total_downtime_hours": total_downtime_hours,
            "uptime_downtime_ratio": round(ratio, 2)
        })

    return columns, data



