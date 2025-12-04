// Copyright (c) 2024, seyfert and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier Score"] = {
	"filters": [
		{
            "fieldname": "vendor",
            "label": __("Vendor"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0, // Optional filter
        }

	],

    "formatter": function(value, row, column, data, default_formatter) {
        // First, use the default formatter to get the base value
        value = default_formatter(value, row, column, data);

        // Check if data exists and apply formatting based on your condition
        if (data && column.fieldname == "status") {
            // Check your condition here, for example, if total is greater than threshold
            if (data["status"] =="Excellent") {
                // Apply background color to the entire cell, including empty cells
                return `<span style="background-color:green; font-weight:block;color:white; display:block; ">${value}</span>`;
            }
            else if ((data["status"] =="Average")){
             return `<span style="background-color:orange; font-weight:block;color:white; display:block; ">${value}</span>`;
            }
            else if ((data["status"] =="Poor")){
                return `<span style="background-color:yellow; font-weight:block;color:white; display:block; ">${value}</span>`;
            }
            else if ((data["status"] =="Very Poor")){
                return `<span style="background-color:red; font-weight:block;color:white; display:block; ">${value}</span>`;
            }
        }

        return value;
    }

};
