import frappe
import random

def execute(filters=None):
    if not filters:
        filters = {}
    
    # Define columns
    columns = [
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"label": "Supplier Score", "fieldname": "supplier_score", "fieldtype": "Float", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 150},
    ]
    
    # Fetch data
    supplier_data = frappe.db.get_all(
        "Supplier Scorecard",
        fields=["supplier", "supplier_score", "status"],
        filters=filters,
    )
    
    data = []
    for row in supplier_data:
        try:
            supplier_score = float(row.supplier_score) if row.supplier_score else 0.0
        except ValueError:
            supplier_score = 0.0
            
        data.append({
            "supplier": row.supplier,
            "supplier_score": supplier_score,
            "status": row.status,
        })

    sorted_data = sorted(data, key=lambda x: x['supplier_score'])

    # Sort data by supplier score
    sorted_data = sorted(data, key=lambda x: x["supplier_score"])
    
    # Prepare chart data
    suppliers = [d["supplier"] for d in sorted_data]
    scores = [d["supplier_score"] for d in sorted_data]

    # Generate dynamic colors for each supplier score
    #color = [get_dynamic_color(d["supplier_score"]) for d in sorted_data]

    # Filter sorted_data to include only suppliers with a valid score
    
    # Filter sorted_data to include only suppliers with a valid score
    # Generate unique suppliers and assign colors
    unique_suppliers = list(set(d["supplier"] for d in sorted_data))
    colors = ["#FF5733", "#33FF57", "#3357FF", "#F1C40F", "#9B59B6"][: len(unique_suppliers)]

    # Build chart data
    chart_data = {
        "data": {
            "labels": [d["supplier"] for d in sorted_data],  # Supplier names
            "datasets": [
                {
                    "name": supplier,  # Supplier name
                    "values": [
                        d["supplier_score"] if d["supplier"] == supplier else  None
                        for d in sorted_data
                    ],
                    "colors": [colors[i]],  # Unique color for each supplier
                }
                for i, supplier in enumerate(unique_suppliers)
                if any(d["supplier"] == supplier for d in sorted_data) 
            ],
        },
        "type": "bar",  # Chart type
        "options": {
        "scales": {
            "x": {
                "stacked": True  # Enable stacking
            },
            "y": {
                "stacked": True  # Enable stacking
            }
        },
        "plugins": {
            "tooltip": {
                "callbacks": {
                    "title": lambda tooltipItem, data: data["labels"][tooltipItem[0]["dataIndex"]],  # Show supplier name
                    "label": lambda tooltipItem, data: (
                        f"Score: {data['datasets'][tooltipItem[0]['datasetIndex']]['data'][tooltipItem[0]['dataIndex']]}"
                        if data['datasets'][tooltipItem[0]['datasetIndex']]['data'][tooltipItem[0]['dataIndex']] is not None
                        else ""
                    )  # Show score only if it is not None
                }
            }
        }
    }
    }

    # Output chart data for use in the frontend
    import json
    #print(json.dumps(chart_data, indent=4))







    

    # Debugging output
    #frappe.msgprint(f"Scores: {scores}")
    #frappe.msgprint(f"Colors: {color}")  # Check the colors applied

    return columns, sorted_data, None, chart_data

def apply_dynamic_colors(value):
    """Returns the color based on the value."""
    if value > 50:
        return "#FF5733"  # Red for high values
    elif value > 20:
        return "#FFC300"  # Yellow for medium values
    else:
        return "#4CAF50"  # Green for low values
