import frappe
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_work_orders(filters=None, fields=None, limit=20, offset=0, order_by=None):
    """
    Get list of work orders with filters and pagination
    
    Args:
        filters: JSON string of filters (e.g., '{"company": "ABC Corp"}')
        fields: JSON string of fields to return (e.g., '["work_order_type", "asset_name"]')
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
        order_by: Sort order (e.g., "creation desc")
    
    Returns:
        {
            "work_orders": [...],
            "total_count": int,
            "limit": int,
            "offset": int,
            "has_more": bool
        }
    """
    try:
        # Parse filters if provided
        if filters and isinstance(filters, str):
            import json
            filters = json.loads(filters)
        
        # Parse fields if provided
        if fields and isinstance(fields, str):
            import json
            fields = json.loads(fields)
        else:
            # Default fields to return
            fields = [
                'name',
                'company',
                'naming_series',
                'work_order_type',
                'asset_type',
                'manufacturer',
                'serial_number',
                'custom_priority_',
                'asset',
                'custom_maintenance_manager',
                'department',
                'repair_status',
                'asset_name',
                'supplier',
                'custom_pending_reason',
                'model',
                'custom_site_contractor',
                'custom_subcontractor',
                'custom_service_agreement',
                'custom_service_coverage',
                'custom_start_date',
                'custom_end_date',
                'custom_total_amount',
                'warranty',
                'service_contract',
                'covering_spare_parts',
                'spare_parts_labour',
                'covering_labour',
                'ppm_only',
                'failure_date',
                'total_hours_spent',
                'job_completed',
                'custom_difference',
                'custom_vendors_hrs',
                'custom_deadline_date',
                'custom_diffrence',
                'feedback_rating',
                'first_responded_on',
                'penalty',
                'custom_assigned_supervisor',
                'stock_consumption',
                'need_procurement',
                'repair_cost',
                'total_repair_cost',
                'capitalize_repair_cost',
                'increase_in_asset_life',
                'description',
                'actions_performed',
                'bio_med_dept',
                'workflow_state',
                'creation',
                'modified',
                'owner',
                'modified_by',
                'docstatus',
                'idx'
            ]
        
        # Get total count
        total_count = frappe.db.count('Work_Order', filters=filters or {})
        
        # Get work orders
        work_orders = frappe.get_all(
            'Work_Order',
            filters=filters or {},
            fields=fields,
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by=order_by or 'creation desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'work_orders': work_orders,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Work Orders API Error')
        frappe.response['message'] = {
            'error': str(e),
            'work_orders': [],
            'total_count': 0
        }


@frappe.whitelist(allow_guest = True)
def get_work_order_details(work_order_name):
    """
    Get detailed information about a specific work order
    
    Args:
        work_order_name: Name/ID of the work order
    
    Returns:
        Work Order document with all fields including child tables
    """
    try:
        if not work_order_name:
            frappe.throw(_('Work Order name is required'))
        
        # Check if user has permission to read this work order
        if not frappe.has_permission('Work_Order', 'read', work_order_name):
            frappe.throw(_('Not permitted to access this work order'))
        
        # Get work order details
        work_order = frappe.get_doc('Work_Order', work_order_name)
        
        frappe.response['message'] = work_order.as_dict()
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Work Order Details API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def create_work_order(work_order_data):
    """
    Create a new work order
    
    Args:
        work_order_data: JSON string containing work order fields
    
    Returns:
        Created work order document
    """
    try:
        import json
        
        # Parse work order data
        if isinstance(work_order_data, str):
            work_order_data = json.loads(work_order_data)
        
        # Check if user has permission to create work order
        if not frappe.has_permission('Work_Order', 'create'):
            frappe.throw(_('Not permitted to create work order'))
        
        # Create new work order
        work_order = frappe.get_doc({
            'doctype': 'Work_Order',
            **work_order_data
        })
        
        work_order.insert()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'work_order': work_order.as_dict(),
            'message': _('Work Order created successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Create Work Order API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_work_order(work_order_name, work_order_data):
    """
    Update an existing work order
    
    Args:
        work_order_name: Name/ID of the work order
        work_order_data: JSON string containing fields to update
    
    Returns:
        Updated work order document
    """
    try:
        import json
        
        if not work_order_name:
            frappe.throw(_('Work Order name is required'))
        
        # Parse work order data
        if isinstance(work_order_data, str):
            work_order_data = json.loads(work_order_data)
        
        # Check if user has permission to update this work order
        if not frappe.has_permission('Work_Order', 'write', work_order_name):
            frappe.throw(_('Not permitted to update this work order'))
        
        # Get and update work order
        work_order = frappe.get_doc('Work_Order', work_order_name)
        
        # Update fields
        for key, value in work_order_data.items():
            if hasattr(work_order, key):
                setattr(work_order, key, value)
        
        work_order.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'work_order': work_order.as_dict(),
            'message': _('Work Order updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Work Order API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def delete_work_order(work_order_name):
    """
    Delete a work order
    
    Args:
        work_order_name: Name/ID of the work order
    
    Returns:
        Success message
    """
    try:
        if not work_order_name:
            frappe.throw(_('Work Order name is required'))
        
        # Check if user has permission to delete this work order
        if not frappe.has_permission('Work_Order', 'delete', work_order_name):
            frappe.throw(_('Not permitted to delete this work order'))
        
        # Delete work order
        frappe.delete_doc('Work_Order', work_order_name)
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'message': _('Work Order deleted successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Delete Work Order API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_work_order_status(work_order_name, repair_status=None, workflow_state=None):
    """
    Update work order status
    
    Args:
        work_order_name: Name/ID of the work order
        repair_status: New repair status (e.g., 'Open', 'In Progress', 'Completed')
        workflow_state: New workflow state
    
    Returns:
        Updated work order document
    """
    try:
        if not work_order_name:
            frappe.throw(_('Work Order name is required'))
        
        # Check if user has permission to update this work order
        if not frappe.has_permission('Work_Order', 'write', work_order_name):
            frappe.throw(_('Not permitted to update this work order'))
        
        # Get work order
        work_order = frappe.get_doc('Work_Order', work_order_name)
        
        # Update status fields
        if repair_status:
            work_order.repair_status = repair_status
        
        if workflow_state:
            work_order.workflow_state = workflow_state
        
        work_order.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'work_order': work_order.as_dict(),
            'message': _('Work Order status updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Work Order Status API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }
