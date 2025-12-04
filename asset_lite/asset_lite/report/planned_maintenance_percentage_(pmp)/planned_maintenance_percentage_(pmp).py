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
        date_format = "CONCAT(YEAR(aml.due_date), ' Q', QUARTER(aml.due_date))"
    elif periodicity == "Half-Yearly":
        date_format = "CONCAT(YEAR(aml.due_date), ' H', IF(MONTH(aml.due_date) <= 6, 1, 2))"
    elif periodicity == "Yearly":
        date_format = "YEAR(aml.due_date)"
    else:  # Default to Monthly
        date_format = "DATE_FORMAT(aml.due_date, '%%m-%%Y')"

    # SQL query to count asset maintenance logs grouped by selected periodicity with the applied filters
    total_logs = frappe.db.sql(f"""
        SELECT COUNT(aml.name) AS total,
               {date_format} AS period
        FROM `tabAsset Maintenance Log` aml
        JOIN `tabAsset` asset ON aml.asset_maintenance = asset.name
        WHERE 1=1 {asset_conditions}
        GROUP BY period
    """, filters, as_dict=True)

    # SQL query to count total work orders with the applied filters
    total_work_orders = frappe.db.sql(f""" 
        SELECT COUNT(wo.name) AS total
        FROM `tabWork_Order` wo
        JOIN `tabAsset` asset ON wo.asset = asset.name
        WHERE 1=1 {asset_conditions}
    """, filters)[0][0]

    # Prepare columns
    columns = [
        {
            "label": "Period",
            "fieldname": "period",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Total Asset Maintenance Logs",
            "fieldname": "total_logs",
            "fieldtype": "Int",
            "width": 150
        },
        {
            "label": "Total Work Orders",
            "fieldname": "total_work_orders",
            "fieldtype": "Int",
            "width": 150
        },
        {
            "label": "Percentage",
            "fieldname": "percentage",
            "fieldtype": "Percent",
            "width": 150
        }
    ]

    # Prepare data
    data = []
    for row in total_logs:
        percentage = round(((flt(row['total']) / flt(total_work_orders)) * 100), 3) if total_work_orders else 0
        data.append({
            "period": row['period'],
            "total_logs": row['total'],
            "total_work_orders": total_work_orders,
            "percentage": percentage
        })

    # Sort the data by period, handling different periodicity formats
    #if periodicity in ["Monthly", "Quarterly", "Half-Yearly"]:
     #   data = sorted(data, key=lambda x: (
      #      int(x['period'].split('-')[1]) if '-' in x['period'] else 0,  # Year (for 'MM-YYYY' format)
      #      int(x['period'].split('-')[0]) if '-' in x['period'] else 0   # Month (for 'MM-YYYY' format)
     #   ))
    #elif periodicity == "Yearly":
       # data = sorted(data, key=lambda x: int(x['period']) if x['period'].isdigit() else 0)  # Year only

    # Sort the data by period, handling different periodicity formats
    if periodicity in ["Monthly", "Quarterly", "Half-Yearly"]:
        data = sorted(data, key=lambda x: (
            int(x['period'].split('-')[1]) if x['period'] and '-' in x['period'] else 0,  # Year (for 'MM-YYYY' format)
            int(x['period'].split('-')[0]) if x['period'] and '-' in x['period'] else 0   # Month (for 'MM-YYYY' format)
        ))
    elif periodicity == "Yearly":
        data = sorted(data, key=lambda x: int(x['period']) if x['period'] and x['period'].isdigit() else 0)  # Year only

    return columns, data
