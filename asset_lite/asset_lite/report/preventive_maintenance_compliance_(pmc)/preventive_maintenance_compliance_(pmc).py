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
    else:
        date_format = "DATE_FORMAT(aml.due_date, '%%m-%%Y')"

    # Query to count total asset maintenance logs grouped by periodicity
    total_logs = frappe.db.sql(f"""
        SELECT {date_format} AS period,
               COUNT(aml.name) AS total
        FROM `tabAsset Maintenance Log` aml
        JOIN `tabAsset` asset ON aml.asset_maintenance = asset.name
        WHERE 1=1 {asset_conditions}
        GROUP BY period
    """, filters, as_dict=True)

    # Query to count completed asset maintenance logs grouped by periodicity
    completed_logs = frappe.db.sql(f"""
        SELECT {date_format} AS period,
               COUNT(aml.name) AS total
        FROM `tabAsset Maintenance Log` aml
        JOIN `tabAsset` asset ON aml.asset_maintenance = asset.name
        WHERE aml.maintenance_status = 'Completed' 
              AND aml.completion_date <= aml.due_date
              {asset_conditions}
        GROUP BY period
    """, filters, as_dict=True)

    # Convert completed_logs to a dictionary for easy lookup
    completed_logs_dict = {log['period']: log['total'] for log in completed_logs}

    # Prepare data
    data = []
    for row in total_logs:
        period = row['period']
        total = row['total']
        completed = completed_logs_dict.get(period, 0)
        percentage = (flt(completed) / flt(total)) * 100 if total else 0

        data.append({
            "period": period,
            "total_logs": total,
            "completed_logs": completed,
            "percentage": percentage
        })

    # Sort the data by year and month
    #data = sorted(data, key=lambda x: (
     #   int(x['period'].split('-')[1]),  # Month as integer (for 'MM-YYYY' format)
      #  int(x['period'].split('-')[0])   # Year (for 'MM-YYYY' format)
    #))
    # Ensure period is not None before splitting
    data = sorted(data, key=lambda x: (
        int(x['period'].split('-')[1]) if x['period'] else float('inf'),  # Month or push None 
        int(x['period'].split('-')[0]) if x['period'] else float('inf')   # Year
    ))
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
            "label": "Completed Asset Maintenance Logs",
            "fieldname": "completed_logs",
            "fieldtype": "Int",
            "width": 150
        },
        {
            "label": "Percentage Completed",
            "fieldname": "percentage",
            "fieldtype": "Percent",
            "width": 150
        }
    ]

    return columns, data
