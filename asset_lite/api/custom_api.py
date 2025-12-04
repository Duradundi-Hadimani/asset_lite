import frappe
from frappe import _
from frappe.utils import now, today, get_datetime
import json

@frappe.whitelist(allow_guest=False)
def get_user_details(user_id=None):
    """
    Get detailed user information
    Usage: /api/method/asset_lite.api.custom_api.get_user_details
    """
    try:
        if not user_id:
            user_id = frappe.session.user
            
        user = frappe.get_doc("User", user_id)
        
        # Get user roles
        roles = frappe.get_roles(user_id)
        
        response_data = {
            "user_id": user_id,
            "full_name": user.full_name,
            "email": user.email,
            "user_image": user.user_image,
            "roles": roles,
            "last_login": user.last_login,
            "enabled": user.enabled,
            "creation": user.creation,
            "modified": user.modified
        }
        
        frappe.response.message = response_data
        frappe.response.status_code = 200
        
    except Exception as e:
        frappe.log_error(f"Error in get_user_details: {str(e)}")
        frappe.response.message = {"error": str(e)}
        frappe.response.status_code = 500

@frappe.whitelist(allow_guest=False)
def get_doctype_records(doctype, filters=None, fields=None, limit=20, offset=0):
    """
    Get records from any DocType with filtering and pagination
    Usage: /api/method/asset_lite.api.custom_api.get_doctype_records
    """
    try:
        # Parse filters and fields if provided as JSON strings
        if isinstance(filters, str):
            filters = json.loads(filters)
        if isinstance(fields, str):
            fields = json.loads(fields)
            
        # Build the query
        query_filters = filters or {}
        
        # Get records
        records = frappe.get_list(
            doctype,
            filters=query_filters,
            fields=fields or ["*"],
            limit=limit,
            start=offset,
            order_by="creation desc"
        )
        
        # Get total count for pagination
        total_count = frappe.db.count(doctype, query_filters)
        
        response_data = {
            "records": records,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
        frappe.response.message = response_data
        frappe.response.status_code = 200
        
    except Exception as e:
        frappe.log_error(f"Error in get_doctype_records: {str(e)}")
        frappe.response.message = {"error": str(e)}
        frappe.response.status_code = 500

@frappe.whitelist(allow_guest=False)
def get_dashboard_stats():
    """
    Get dashboard statistics
    Usage: /api/method/asset_lite.api.custom_api.get_dashboard_stats
    """
    try:
        # Example: Get counts for different DocTypes
        stats = {
            "total_users": frappe.db.count("User", {"enabled": 1}),
            "total_customers": frappe.db.count("Customer"),
            "total_items": frappe.db.count("Item"),
            "total_orders": frappe.db.count("Sales Order"),
            "recent_activities": []
        }
        
        # Get recent activities (example)
        recent_users = frappe.get_list(
            "User",
            fields=["name", "full_name", "creation"],
            limit=5,
            order_by="creation desc"
        )
        
        stats["recent_activities"] = recent_users
        
        frappe.response.message = stats
        frappe.response.status_code = 200
        
    except Exception as e:
        frappe.log_error(f"Error in get_dashboard_stats: {str(e)}")
        frappe.response.message = {"error": str(e)}
        frappe.response.status_code = 500

# Example KYC API for your KYCDetails component
@frappe.whitelist(allow_guest=False)
def get_kyc_details():
    """
    Get KYC details - customize this based on your actual KYC DocType
    Usage: /api/method/asset_lite.api.custom_api.get_kyc_details
    """
    try:
        # Replace 'KYC' with your actual DocType name
        kyc_records = frappe.get_list(
            "KYC",  # Change this to your actual DocType
            fields=["name", "kyc_status", "kyc_type", "creation"],
            limit=50,
            order_by="creation desc"
        )
        
        frappe.response.message = kyc_records
        frappe.response.status_code = 200
        
    except Exception as e:
        frappe.log_error(f"Error in get_kyc_details: {str(e)}")
        frappe.response.message = {"error": str(e)}
        frappe.response.status_code = 500

# Simple test endpoint to verify API is working
@frappe.whitelist(allow_guest=False)
def test_api():
    """
    Simple test endpoint to verify the API is working
    Usage: /api/method/asset_lite.api.custom_api.test_api
    """
    try:
        frappe.response.message = {
            "status": "success",
            "message": "API is working!",
            "user": frappe.session.user,
            "timestamp": now()
        }
        frappe.response.status_code = 200
        
    except Exception as e:
        frappe.log_error(f"Error in test_api: {str(e)}")
        frappe.response.message = {"error": str(e)}
        frappe.response.status_code = 500
