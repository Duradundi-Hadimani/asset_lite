// Copyright (c) 2025, seyfert and contributors
// For license information, please see license.txt

frappe.query_reports["Planned maintenance percentage (PMP)"] = {
	"filters": [
		
		{
            "fieldname": "department",
            "label": "Department",
            "fieldtype": "Link",
            "options": "Department",
            "reqd": 0
        },
        {
            "fieldname": "vendor",
            "label": "Vendor",
            "fieldtype": "Link",
            "options": "Supplier",  //Assuming 'Supplier' is the doctype used for vendors
            "reqd": 0
        },
        {
            "fieldname": "asset_class",
            "label": "Class",
            "fieldtype": "Select",
            "options": ["","Class A","Class B","Class C"],  //s Assuming 'Asset Class' is the relevant doctype
            "reqd": 0
        },
        {
            "fieldname": "periodicity",
            "label": "Periodicity",
            "fieldtype": "Select",
            "options": "\nMonthly\nQuarterly\nHalf-Yearly\nYearly",
            "default": "Monthly",
            "reqd": 1
        }


	]
};
