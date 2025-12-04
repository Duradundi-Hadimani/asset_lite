import frappe
@frappe.whitelist()
def get_custom_html_data(filters=None):
    return {
        "labels": ["Custom"],
        "datasets": [{"name": "Custom HTML", "values": [1]}],
        "type": "custom",
        "custom_html": True
    }




# asset_lite/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_active_map_data(hospital=None):
    filters = {"latitude": ["!=", ""], "longitude": ["!=", ""]}
    if hospital:
        filters["name"] = hospital

    hospitals = frappe.get_all("Location", fields=["name", "latitude", "longitude"], filters=filters)
    results = []

    for h in hospitals:
        name = h.name

        def count(doctype, filters):
            try:
                return frappe.db.count(doctype, filters)
            except:
                return 0

        data = {
            "name": name,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "assets": count("Asset", {"company": name}),
            "normal_work_orders": count("Work_Order", {
                "company": name, "custom_priority_": "Normal",
                "repair_status": ["in", ["Open", "Work In Progress"]]
            }),
            "urgent_work_orders": count("Work_Order", {
                "company": name, "custom_priority_": "Urgent",
                "repair_status": ["in", ["Open", "Work In Progress"]]
            }),

            # Work Orders by status (for table)
            "wo_open": count("Work_Order", {"company": name, "repair_status": "Open"}),
            "wo_progress": count("Work_Order", {"company": name, "repair_status": "Work In Progress"}),
            "wo_review": count("Work_Order", {"company": name, "repair_status": "Pending Review"}),
            "wo_completed": count("Work_Order", {"company": name, "repair_status": "Completed"}),


            "planned_maintenance": count("Asset Maintenance Log", {
                "custom_hospital_name": name,
                "maintenance_status": "Planned"
            }),
            "completed_maintenance": count("Asset Maintenance Log", {
                "custom_hospital_name": name,
                "maintenance_status": "Completed"
            }),
            "overdue_maintenance": count("Asset Maintenance Log", {
                "custom_hospital_name": name,
                "maintenance_status": "Overdue"
            })
        }

        results.append(data)

    return results



