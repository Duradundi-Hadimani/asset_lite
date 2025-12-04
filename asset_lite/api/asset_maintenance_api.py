import frappe
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_asset_maintenance_logs(filters=None, fields=None, limit=20, offset=0, order_by=None):
    """
    Get list of asset maintenance logs with filters and pagination
    
    Args:
        filters: JSON string of filters (e.g., '{"maintenance_status": "Planned"}')
        fields: JSON string of fields to return (e.g., '["asset_name", "due_date"]')
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
        order_by: Sort order (e.g., "creation desc")
    
    Returns:
        {
            "asset_maintenance_logs": [...],
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
                'asset_maintenance',
                'naming_series',
                'asset_name',
                'custom_asset_type',
                'item_code',
                'item_name',
                'custom_asset_names',
                'custom_hospital_name',
                'task',
                'task_name',
                'maintenance_type',
                'periodicity',
                'has_certificate',
                'custom_early_completion',
                'maintenance_status',
                'custom_pm_overdue_reason',
                'custom_accepted_by_moh',
                'assign_to_name',
                'due_date',
                'custom_accepted_by_moh_',
                'custom_template',
                'workflow_state',
                'creation',
                'modified',
                'owner',
                'modified_by',
                'docstatus',
                'idx'
            ]
        
        # Get total count
        total_count = frappe.db.count('Asset Maintenance Log', filters=filters or {})
        
        # Get asset maintenance logs
        asset_maintenance_logs = frappe.get_all(
            'Asset Maintenance Log',
            filters=filters or {},
            fields=fields,
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by=order_by or 'creation desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenance_logs': asset_maintenance_logs,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Maintenance Logs API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenance_logs': [],
            'total_count': 0
        }


@frappe.whitelist(allow_guest = True)
def get_asset_maintenance_log_details(log_name):
    """
    Get detailed information about a specific asset maintenance log
    
    Args:
        log_name: Name/ID of the asset maintenance log
    
    Returns:
        Asset Maintenance Log document with all fields including child tables
    """
    try:
        if not log_name:
            frappe.throw(_('Asset Maintenance Log name is required'))
        
        # Check if user has permission to read this log
        if not frappe.has_permission('Asset Maintenance Log', 'read', log_name):
            frappe.throw(_('Not permitted to access this asset maintenance log'))
        
        # Get asset maintenance log details
        log = frappe.get_doc('Asset Maintenance Log', log_name)
        
        frappe.response['message'] = log.as_dict()
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Maintenance Log Details API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def create_asset_maintenance_log(log_data):
    """
    Create a new asset maintenance log
    
    Args:
        log_data: JSON string containing asset maintenance log fields
    
    Returns:
        Created asset maintenance log document
    """
    try:
        import json
        
        # Parse log data
        if isinstance(log_data, str):
            log_data = json.loads(log_data)
        
        # Check if user has permission to create asset maintenance log
        if not frappe.has_permission('Asset Maintenance Log', 'create'):
            frappe.throw(_('Not permitted to create asset maintenance log'))
        
        # Create new asset maintenance log
        log = frappe.get_doc({
            'doctype': 'Asset Maintenance Log',
            **log_data
        })
        
        log.insert()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance_log': log.as_dict(),
            'message': _('Asset Maintenance Log created successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Create Asset Maintenance Log API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_asset_maintenance_log(log_name, log_data):
    """
    Update an existing asset maintenance log
    
    Args:
        log_name: Name/ID of the asset maintenance log
        log_data: JSON string containing fields to update
    
    Returns:
        Updated asset maintenance log document
    """
    try:
        import json
        
        if not log_name:
            frappe.throw(_('Asset Maintenance Log name is required'))
        
        # Parse log data
        if isinstance(log_data, str):
            log_data = json.loads(log_data)
        
        # Check if user has permission to update this log
        if not frappe.has_permission('Asset Maintenance Log', 'write', log_name):
            frappe.throw(_('Not permitted to update this asset maintenance log'))
        
        # Get and update asset maintenance log
        log = frappe.get_doc('Asset Maintenance Log', log_name)
        
        # Update fields
        for key, value in log_data.items():
            if hasattr(log, key):
                setattr(log, key, value)
        
        log.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance_log': log.as_dict(),
            'message': _('Asset Maintenance Log updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Asset Maintenance Log API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def delete_asset_maintenance_log(log_name):
    """
    Delete an asset maintenance log
    
    Args:
        log_name: Name/ID of the asset maintenance log
    
    Returns:
        Success message
    """
    try:
        if not log_name:
            frappe.throw(_('Asset Maintenance Log name is required'))
        
        # Check if user has permission to delete this log
        if not frappe.has_permission('Asset Maintenance Log', 'delete', log_name):
            frappe.throw(_('Not permitted to delete this asset maintenance log'))
        
        # Delete asset maintenance log
        frappe.delete_doc('Asset Maintenance Log', log_name)
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'message': _('Asset Maintenance Log deleted successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Delete Asset Maintenance Log API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_maintenance_status(log_name, maintenance_status=None, workflow_state=None):
    """
    Update asset maintenance log status
    
    Args:
        log_name: Name/ID of the asset maintenance log
        maintenance_status: New maintenance status (e.g., 'Planned', 'Completed', 'Overdue')
        workflow_state: New workflow state
    
    Returns:
        Updated asset maintenance log document
    """
    try:
        if not log_name:
            frappe.throw(_('Asset Maintenance Log name is required'))
        
        # Check if user has permission to update this log
        if not frappe.has_permission('Asset Maintenance Log', 'write', log_name):
            frappe.throw(_('Not permitted to update this asset maintenance log'))
        
        # Get asset maintenance log
        log = frappe.get_doc('Asset Maintenance Log', log_name)
        
        # Update status fields
        if maintenance_status:
            log.maintenance_status = maintenance_status
        
        if workflow_state:
            log.workflow_state = workflow_state
        
        log.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance_log': log.as_dict(),
            'message': _('Asset Maintenance Log status updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Maintenance Status API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_maintenance_logs_by_asset(asset_name, filters=None, limit=20, offset=0):
    """
    Get all maintenance logs for a specific asset
    
    Args:
        asset_name: Name/ID of the asset
        filters: Additional JSON string of filters
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
    
    Returns:
        List of maintenance logs for the asset
    """
    try:
        import json
        
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        # Parse additional filters if provided
        additional_filters = {}
        if filters and isinstance(filters, str):
            additional_filters = json.loads(filters)
        
        # Combine filters
        combined_filters = {'asset_name': asset_name, **additional_filters}
        
        # Get total count
        total_count = frappe.db.count('Asset Maintenance Log', filters=combined_filters)
        
        # Get maintenance logs
        logs = frappe.get_all(
            'Asset Maintenance Log',
            filters=combined_filters,
            fields=['*'],
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by='due_date desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenance_logs': logs,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Maintenance Logs By Asset API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenance_logs': [],
            'total_count': 0
        }


@frappe.whitelist(allow_guest = True)
def get_overdue_maintenance_logs(filters=None, limit=20, offset=0):
    """
    Get all overdue maintenance logs
    
    Args:
        filters: Additional JSON string of filters
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
    
    Returns:
        List of overdue maintenance logs
    """
    try:
        import json
        from frappe.utils import today
        
        # Parse additional filters if provided
        additional_filters = {}
        if filters and isinstance(filters, str):
            additional_filters = json.loads(filters)
        
        # Combine filters - get logs with due_date less than today and status not completed
        combined_filters = {
            'due_date': ['<', today()],
            'maintenance_status': ['!=', 'Completed'],
            **additional_filters
        }
        
        # Get total count
        total_count = frappe.db.count('Asset Maintenance Log', filters=combined_filters)
        
        # Get overdue logs
        logs = frappe.get_all(
            'Asset Maintenance Log',
            filters=combined_filters,
            fields=['*'],
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by='due_date asc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenance_logs': logs,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Overdue Maintenance Logs API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenance_logs': [],
            'total_count': 0
        }
