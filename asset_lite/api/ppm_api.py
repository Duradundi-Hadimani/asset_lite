import frappe
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_asset_maintenances(filters=None, fields=None, limit=20, offset=0, order_by=None):
    """
    Get list of asset maintenances (PPM schedules) with filters and pagination
    
    Args:
        filters: JSON string of filters (e.g., '{"company": "Al Jouf Hospital"}')
        fields: JSON string of fields to return (e.g., '["asset_name", "maintenance_team"]')
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
        order_by: Sort order (e.g., "creation desc")
    
    Returns:
        {
            "asset_maintenances": [...],
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
                'asset_name',
                'custom_asset_type',
                'asset_category',
                'custom_type_of_maintenance',
                'custom_asset_name',
                'item_code',
                'item_name',
                'maintenance_team',
                'custom_pm_schedule',
                'maintenance_manager',
                'maintenance_manager_name',
                'custom_warranty',
                'custom_warranty_status',
                'custom_service_contract',
                'custom_service_contract_status',
                'custom_frequency',
                'custom_total_amount',
                'custom_no_of_pms',
                'custom_price_per_pm',
                'creation',
                'modified',
                'owner',
                'modified_by',
                'docstatus',
                'idx'
            ]
        
        # Get total count
        total_count = frappe.db.count('Asset Maintenance', filters=filters or {})
        
        # Get asset maintenances
        asset_maintenances = frappe.get_all(
            'Asset Maintenance',
            filters=filters or {},
            fields=fields,
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by=order_by or 'creation desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenances': asset_maintenances,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Maintenances API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenances': [],
            'total_count': 0
        }


@frappe.whitelist(allow_guest = True)
def get_asset_maintenance_details(maintenance_name):
    """
    Get detailed information about a specific asset maintenance (PPM schedule)
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
    
    Returns:
        Asset Maintenance document with all fields including child tables
    """
    try:
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Check if user has permission to read this maintenance
        if not frappe.has_permission('Asset Maintenance', 'read', maintenance_name):
            frappe.throw(_('Not permitted to access this asset maintenance'))
        
        # Get asset maintenance details
        maintenance = frappe.get_doc('Asset Maintenance', maintenance_name)
        
        frappe.response['message'] = maintenance.as_dict()
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Maintenance Details API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def create_asset_maintenance(maintenance_data):
    """
    Create a new asset maintenance (PPM schedule)
    
    Args:
        maintenance_data: JSON string containing asset maintenance fields
    
    Returns:
        Created asset maintenance document
    """
    try:
        import json
        
        # Parse maintenance data
        if isinstance(maintenance_data, str):
            maintenance_data = json.loads(maintenance_data)
        
        # Check if user has permission to create asset maintenance
        if not frappe.has_permission('Asset Maintenance', 'create'):
            frappe.throw(_('Not permitted to create asset maintenance'))
        
        # Create new asset maintenance
        maintenance = frappe.get_doc({
            'doctype': 'Asset Maintenance',
            **maintenance_data
        })
        
        maintenance.insert()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance': maintenance.as_dict(),
            'message': _('Asset Maintenance created successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Create Asset Maintenance API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_asset_maintenance(maintenance_name, maintenance_data):
    """
    Update an existing asset maintenance (PPM schedule)
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
        maintenance_data: JSON string containing fields to update
    
    Returns:
        Updated asset maintenance document
    """
    try:
        import json
        
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Parse maintenance data
        if isinstance(maintenance_data, str):
            maintenance_data = json.loads(maintenance_data)
        
        # Check if user has permission to update this maintenance
        if not frappe.has_permission('Asset Maintenance', 'write', maintenance_name):
            frappe.throw(_('Not permitted to update this asset maintenance'))
        
        # Get and update asset maintenance
        maintenance = frappe.get_doc('Asset Maintenance', maintenance_name)
        
        # Update fields
        for key, value in maintenance_data.items():
            if hasattr(maintenance, key):
                setattr(maintenance, key, value)
        
        maintenance.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance': maintenance.as_dict(),
            'message': _('Asset Maintenance updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Asset Maintenance API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def delete_asset_maintenance(maintenance_name):
    """
    Delete an asset maintenance (PPM schedule)
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
    
    Returns:
        Success message
    """
    try:
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Check if user has permission to delete this maintenance
        if not frappe.has_permission('Asset Maintenance', 'delete', maintenance_name):
            frappe.throw(_('Not permitted to delete this asset maintenance'))
        
        # Delete asset maintenance
        frappe.delete_doc('Asset Maintenance', maintenance_name)
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'message': _('Asset Maintenance deleted successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Delete Asset Maintenance API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_maintenance_tasks(maintenance_name):
    """
    Get all maintenance tasks for a specific asset maintenance
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
    
    Returns:
        List of maintenance tasks (asset_maintenance_tasks child table)
    """
    try:
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Check if user has permission to read this maintenance
        if not frappe.has_permission('Asset Maintenance', 'read', maintenance_name):
            frappe.throw(_('Not permitted to access this asset maintenance'))
        
        # Get maintenance tasks
        tasks = frappe.get_all(
            'Asset Maintenance Task',
            filters={'parent': maintenance_name},
            fields=['*'],
            order_by='idx asc'
        )
        
        frappe.response['message'] = {
            'maintenance_tasks': tasks,
            'total_count': len(tasks)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Maintenance Tasks API Error')
        frappe.response['message'] = {
            'error': str(e),
            'maintenance_tasks': []
        }


@frappe.whitelist(allow_guest = True)
def get_service_coverage(maintenance_name):
    """
    Get service coverage details for a specific asset maintenance
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
    
    Returns:
        List of service coverage (custom_service_coverage_table child table)
    """
    try:
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Check if user has permission to read this maintenance
        if not frappe.has_permission('Asset Maintenance', 'read', maintenance_name):
            frappe.throw(_('Not permitted to access this asset maintenance'))
        
        # Get service coverage
        coverage = frappe.get_all(
            'Service Coverage',
            filters={'parent': maintenance_name},
            fields=['*'],
            order_by='idx asc'
        )
        
        frappe.response['message'] = {
            'service_coverage': coverage,
            'total_count': len(coverage)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Service Coverage API Error')
        frappe.response['message'] = {
            'error': str(e),
            'service_coverage': []
        }


@frappe.whitelist(allow_guest = True)
def add_maintenance_task(maintenance_name, task_data):
    """
    Add a new maintenance task to an asset maintenance
    
    Args:
        maintenance_name: Name/ID of the asset maintenance
        task_data: JSON string containing task fields
    
    Returns:
        Updated asset maintenance document
    """
    try:
        import json
        
        if not maintenance_name:
            frappe.throw(_('Asset Maintenance name is required'))
        
        # Parse task data
        if isinstance(task_data, str):
            task_data = json.loads(task_data)
        
        # Check if user has permission to update this maintenance
        if not frappe.has_permission('Asset Maintenance', 'write', maintenance_name):
            frappe.throw(_('Not permitted to update this asset maintenance'))
        
        # Get asset maintenance
        maintenance = frappe.get_doc('Asset Maintenance', maintenance_name)
        
        # Add new task
        maintenance.append('asset_maintenance_tasks', task_data)
        maintenance.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset_maintenance': maintenance.as_dict(),
            'message': _('Maintenance task added successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Add Maintenance Task API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_maintenance_task(task_name, task_data):
    """
    Update a specific maintenance task
    
    Args:
        task_name: Name/ID of the maintenance task
        task_data: JSON string containing fields to update
    
    Returns:
        Updated task details
    """
    try:
        import json
        
        if not task_name:
            frappe.throw(_('Maintenance task name is required'))
        
        # Parse task data
        if isinstance(task_data, str):
            task_data = json.loads(task_data)
        
        # Get the task to find parent
        task = frappe.get_doc('Asset Maintenance Task', task_name)
        
        # Check if user has permission to update parent maintenance
        if not frappe.has_permission('Asset Maintenance', 'write', task.parent):
            frappe.throw(_('Not permitted to update this maintenance task'))
        
        # Update task fields
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'maintenance_task': task.as_dict(),
            'message': _('Maintenance task updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Maintenance Task API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_maintenances_by_asset(asset_name, filters=None, limit=20, offset=0):
    """
    Get all maintenance schedules for a specific asset
    
    Args:
        asset_name: Name/ID of the asset
        filters: Additional JSON string of filters
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
    
    Returns:
        List of maintenance schedules for the asset
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
        total_count = frappe.db.count('Asset Maintenance', filters=combined_filters)
        
        # Get maintenances
        maintenances = frappe.get_all(
            'Asset Maintenance',
            filters=combined_filters,
            fields=['*'],
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by='creation desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenances': maintenances,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Maintenances By Asset API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenances': [],
            'total_count': 0
        }


@frappe.whitelist(allow_guest = True)
def get_active_service_contracts(filters=None, limit=20, offset=0):
    """
    Get all asset maintenances with active service contracts
    
    Args:
        filters: Additional JSON string of filters
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
    
    Returns:
        List of asset maintenances with active contracts
    """
    try:
        import json
        
        # Parse additional filters if provided
        additional_filters = {}
        if filters and isinstance(filters, str):
            additional_filters = json.loads(filters)
        
        # Combine filters - get maintenances with service contract = 1
        combined_filters = {
            'custom_service_contract': 1,
            **additional_filters
        }
        
        # Get total count
        total_count = frappe.db.count('Asset Maintenance', filters=combined_filters)
        
        # Get maintenances
        maintenances = frappe.get_all(
            'Asset Maintenance',
            filters=combined_filters,
            fields=['*'],
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by='creation desc'
        )
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'asset_maintenances': maintenances,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Active Service Contracts API Error')
        frappe.response['message'] = {
            'error': str(e),
            'asset_maintenances': [],
            'total_count': 0
        }
