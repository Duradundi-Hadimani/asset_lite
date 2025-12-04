# Copyright (c) 2024, seyfert and contributors
# For license information, please see license.txt

import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data


def execute(filters):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Supplier", "fieldname": "vendor", "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"label": "Total Repair Hours", "fieldname": "total_hours", "fieldtype": "Float", "width": 150},
        {"label": "Total Assets", "fieldname": "total_assets", "fieldtype": "Int", "width": 150},
        {"label": "Repair Hours per Asset", "fieldname": "hours_per_asset", "fieldtype": "Float", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
        
    ]

def get_data(filters):
    supplier_condition = ""
    if filters and filters.get("vendor"):
        supplier_condition = supplier_condition+f"AND wo.vendor = '{filters.get('vendor')}'"

    # Step 1: Fetch Total Hours and Group by Supplier
    work_orders = frappe.db.sql(f"""
        SELECT
            wo.vendor AS vendor,
            SUM(wo.total_hours_spent) AS total_hours
        FROM
            `tabWork_Order` wo
        WHERE
         wo.vendor IS NOT NULL AND
         wo.docstatus =1
           {supplier_condition}
        GROUP BY
            wo.vendor
        ORDER BY
            total_hours DESC
    """, as_dict=True)

    # Step 2: Fetch Total Assets for each Supplier
    supplier_assets = frappe.db.sql(f"""
        SELECT
            asset.custom_vendor AS vendor,
            COUNT(asset.name) AS total_assets
        FROM
            `tabAsset` asset
        WHERE
            asset.custom_vendor IS NOT NULL
            AND asset.docstatus = 1
            
        GROUP BY
            asset.custom_vendor
    """, as_dict=True)

    # Map total assets by vendor for easy lookup
    asset_map = {entry["vendor"]: entry["total_assets"] for entry in supplier_assets}

    # Step 3: Calculate Repair Hours per Asset and Status
    data = []
    for wo in work_orders:
        total_assets = asset_map.get(wo["vendor"], 0)  # Get total assets for the vendor
        total_hours = round(wo["total_hours"], 2)  # Round total hours to 2 decimal places
        hours_per_asset = round((wo["total_hours"] / total_assets),2) if total_assets > 0 else 0  # Avoid division by zero

        # Determine status based on hours_per_asset
        if hours_per_asset <= 30:
            status = "Excellent"
           
        elif 30 < hours_per_asset <= 50:
            status = "Average"
           
        elif 50 < hours_per_asset <= 80:
            status = "Poor"
           
        elif 80 < hours_per_asset <= 100:
            status = "Very Poor"
           
        else:
            status = "Critical"  # Add an additional category if above 100
          


        data.append({
            "vendor": wo["vendor"],
            "total_hours": total_hours,
            "total_assets": total_assets,
            "hours_per_asset": hours_per_asset,
            "status": status,
           
        })
    
    

    return data
