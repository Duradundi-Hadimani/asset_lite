import frappe
from frappe import _
from frappe.utils import nowdate
import json


def _ok(payload, code=200):
    frappe.response.status_code = code
    frappe.response.message = payload


def _err(msg, code=500):
    frappe.response.status_code = code
    frappe.response.message = {"error": msg}


@frappe.whitelist(allow_guest = True)
def get_number_cards():
    """
    Returns counts for Number Cards:
    - total_assets
    - work_orders_open
    - work_orders_in_progress
    - work_orders_completed
    """
    try:
        total_assets = frappe.db.count("Asset")
        work_orders_open = frappe.db.count("Work Order", {"status": ["in", ["Not Started", "Open", "Pending"]]})
        work_orders_in_progress = frappe.db.count("Work Order", {"status": ["in", ["In Process", "In Progress", "Started"]]})
        work_orders_completed = frappe.db.count("Work Order", {"status": ["in", ["Completed", "Closed", "Finished"]]})

        _ok({
            "total_assets": total_assets,
            "work_orders_open": work_orders_open,
            "work_orders_in_progress": work_orders_in_progress,
            "work_orders_completed": work_orders_completed,
        })
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_number_cards")
        _err(str(e))


@frappe.whitelist(allow_guest = True)
def list_dashboard_charts(search=None, public_only=True, limit=50):
    """
    List available Dashboard Chart docs and their y-axis rows.
    """
    try:
        filters = {}
        if str(public_only) in ("1", "true", "True"):  # tolerate string flags
            filters["is_public"] = 1

        charts = frappe.get_all(
            "Dashboard Chart",
            filters=filters,
            fields=[
                "name",
                "chart_name",
                "type",
                "is_public",
                "chart_type",
                "report_name",
                "use_report_chart",
                "x_field",
                "time_interval",
                "timespan",
                "custom_options",
            ],
            limit=int(limit or 50),
            order_by="modified desc",
        )

        for c in charts:
            y_rows = frappe.get_all(
                "Dashboard Chart Field",
                filters={"parenttype": "Dashboard Chart", "parent": c["name"]},
                fields=["y_field", "color"],
                order_by="idx asc",
            )
            c["y_axes"] = y_rows

        _ok({"charts": charts})
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "list_dashboard_charts")
        _err(str(e))


@frappe.whitelist(allow_guest = True)
def get_dashboard_chart_data(chart_name, report_filters=None):
    """
    Return chart-ready JSON for any Dashboard Chart (Report-based or Custom).
    """
    try:
        if isinstance(report_filters, str):
            report_filters = json.loads(report_filters or "{}")
        report_filters = report_filters or {}

        chart = frappe.get_doc("Dashboard Chart", chart_name)

        # Handle Custom charts (non-Report based)
        if chart.chart_type != "Report" or not chart.use_report_chart:
            # For Custom charts, query the source doctype directly
            try:
                # Get chart configuration
                source = chart.document_type
                based_on = chart.based_on
                value_based_on = chart.value_based_on or "name"
                
                # Build aggregation query
                if chart.type == "Pie":
                    # Group by based_on field and count
                    data = frappe.db.sql(f"""
                        SELECT {based_on} as label, COUNT({value_based_on}) as value
                        FROM `tab{source}`
                        GROUP BY {based_on}
                        ORDER BY value DESC
                    """, as_dict=True)
                    
                    labels = [str(d.get("label")) for d in data]
                    values = [float(d.get("value") or 0) for d in data]
                    
                    _ok({
                        "labels": labels,
                        "datasets": [{"name": "count", "values": values}],
                        "type": "Pie",
                        "options": _parse_custom_options(chart.custom_options),
                        "source": {"doctype": source},
                    })
                else:
                    # Bar chart: group by based_on
                    data = frappe.db.sql(f"""
                        SELECT {based_on} as label, COUNT({value_based_on}) as value
                        FROM `tab{source}`
                        GROUP BY {based_on}
                        ORDER BY value DESC
                        LIMIT 20
                    """, as_dict=True)
                    
                    labels = [str(d.get("label")) for d in data]
                    values = [float(d.get("value") or 0) for d in data]
                    
                    _ok({
                        "labels": labels,
                        "datasets": [{"name": "count", "values": values, "color": "#4F46E5"}],
                        "type": "Bar",
                        "options": _parse_custom_options(chart.custom_options),
                        "source": {"doctype": source},
                    })
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Custom Chart Error: {chart_name}")
                _err(f"Error processing custom chart: {str(e)}")
            return

        y_axes = frappe.get_all(
            "Dashboard Chart Field",
            filters={"parenttype": "Dashboard Chart", "parent": chart.name},
            fields=["y_field", "color"],
            order_by="idx asc",
        )

        run = frappe.get_attr("frappe.desk.query_report.run")
        report_result = run(chart.report_name, filters=report_filters)
        rows = report_result.get("result", []) or []
        data_rows = [r for r in rows if not r.get("is_total_row")]

        x_key = chart.x_field
        labels = [str(r.get(x_key)) for r in data_rows if r.get(x_key) is not None]

        datasets = []
        for y in y_axes:
            series_name = y.get("y_field")  # Use field name as series name
            values = []
            for r in data_rows:
                val = r.get(y.get("y_field"))
                try:
                    values.append(float(val) if val is not None else 0)
                except Exception:
                    values.append(0)
            datasets.append({"name": series_name, "values": values, "color": y.get("color")})

        chart_type = (chart.type or "Bar").title()
        if chart_type.lower() == "pie":
            ds = datasets[0] if datasets else {"name": "value", "values": []}
            _ok({
                "labels": labels,
                "datasets": [ds],
                "type": "Pie",
                "options": _parse_custom_options(chart.custom_options),
                "source": {"report": chart.report_name},
            })
            return

        _ok({
            "labels": labels,
            "datasets": datasets,
            "type": chart_type,
            "options": _parse_custom_options(chart.custom_options),
            "source": {"report": chart.report_name},
        })
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_dashboard_chart_data")
        _err(str(e))


def _parse_custom_options(raw):
    if not raw:
        return {}
    try:
        if isinstance(raw, dict):
            return raw
        return json.loads(raw)
    except Exception:
        return {}


@frappe.whitelist(allow_guest = True)
def get_repair_cost_by_item(year=None):
    """
    Example specialized endpoint for 'Repair Cost' report style chart
    (X: item_code, Y: amount, Filter: Year)
    """
    try:
        year = int(year or frappe.utils.getdate(nowdate()).year)
        rows = frappe.db.sql(
            """
            SELECT item_code, SUM(amount) as amount
            FROM `tabWork Order` wo
            WHERE YEAR(wo.posting_date) = %(year)s
            GROUP BY item_code
            ORDER BY amount DESC
            """,
            {"year": year},
            as_dict=True,
        )
        labels = [r.item_code or "Unknown" for r in rows]
        values = [float(r.amount or 0) for r in rows]
        _ok({
            "labels": labels,
            "datasets": [{"name": f"Repair Cost {year}", "values": values}],
            "type": "Bar",
            "options": {},
        })
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_repair_cost_by_item")
        _err(str(e))


