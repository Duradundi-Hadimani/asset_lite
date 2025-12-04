import frappe
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_assets(filters=None, fields=None, limit=20, offset=0, order_by=None, include_finance_books=True):
    """
    Get list of assets with filters and pagination
    
    Args:
        filters: JSON string of filters (e.g., '{"company": "ABC Corp"}')
        fields: JSON string of fields to return (e.g., '["asset_name", "location"]')
        limit: Number of records to return (default: 20)
        offset: Number of records to skip (default: 0)
        order_by: Sort order (e.g., "creation desc")
        include_finance_books: Include depreciation details (default: True)
    
    Returns:
        {
            "assets": [...],
            "total_count": int,
            "limit": int,
            "offset": int,
            "has_more": bool
        }
    """
    try:
        import json
        frappe.log_error(f"Logged in User ",frappe.session.user)

        
        # Parse filters if provided
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
        
        # Parse fields if provided
        if fields and isinstance(fields, str):
            fields = json.loads(fields)
        else:
            # Default fields to return
            fields = [
                'name',
                'asset_name',
                'company',
                'custom_serial_number',
                'location',
                'custom_manufacturer',
                'department',
                'custom_asset_type',
                'custom_manufacturing_year',
                'custom_model',
                'custom_class',
                'custom_device_status',
                'custom_down_time',
                'asset_owner_company',
                'custom_up_time',
                'custom_modality',
                'custom_attach_image',
                'custom_site_contractor',
                'custom_total_amount',
                'creation',
                'modified',
                'owner',
                'modified_by',
                # Depreciation related fields from parent
                'calculate_depreciation',
                'opening_accumulated_depreciation',
                'opening_number_of_booked_depreciations',
                'is_fully_depreciated',
                'depreciation_method',
                'value_after_depreciation',
                'total_number_of_depreciations',
                'frequency_of_depreciation',
                'gross_purchase_amount',
                'total_asset_cost',
                'available_for_use_date',
                'status'
            ]
        
        # Get total count
        total_count = frappe.db.count('Asset', filters=filters or {})
        
        # Get assets
        assets = frappe.get_all(
            'Asset',
            filters=filters or {},
            fields=fields,
            limit_page_length=int(limit),
            limit_start=int(offset),
            order_by=order_by or 'creation desc'
        )
        
        # Include finance_books (depreciation details) for each asset
        if include_finance_books:
            for asset in assets:
                asset['finance_books'] = get_finance_books(asset['name'])
        
        # Calculate has_more
        has_more = (int(offset) + int(limit)) < total_count
        
        frappe.response['message'] = {
            'assets': assets,
            'total_count': total_count,
            'limit': int(limit),
            'offset': int(offset),
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Assets API Error')
        frappe.response['message'] = {
            'error': str(e),
            'assets': [],
            'total_count': 0
        }


def get_finance_books(asset_name):
    """
    Get finance books (depreciation details) for an asset
    
    Args:
        asset_name: Name/ID of the asset
    
    Returns:
        List of finance book entries with depreciation details
    """
    finance_books = frappe.get_all(
        'Asset Finance Book',
        filters={'parent': asset_name},
        fields=[
            'name',
            'idx',
            'finance_book',
            'depreciation_method',
            'total_number_of_depreciations',
            'total_number_of_booked_depreciations',
            'daily_prorata_based',
            'shift_based',
            'frequency_of_depreciation',
            'depreciation_start_date',
            'salvage_value_percentage',
            'expected_value_after_useful_life',
            'value_after_depreciation',
            'rate_of_depreciation'
        ],
        order_by='idx asc'
    )
    return finance_books


@frappe.whitelist(allow_guest = True)
def get_asset_details(asset_name, include_depreciation_schedule=False):
    """
    Get detailed information about a specific asset
    
    Args:
        asset_name: Name/ID of the asset
        include_depreciation_schedule: Include depreciation schedule entries (default: False)
    
    Returns:
        Asset document with all fields including finance_books
    """
    try:
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        # Check if user has permission to read this asset
        if not frappe.has_permission('Asset', 'read', asset_name):
            frappe.throw(_('Not permitted to access this asset'))
        
        # Get asset details (includes finance_books child table)
        asset = frappe.get_doc('Asset', asset_name)
        asset_dict = asset.as_dict()
        
        # Optionally include depreciation schedule
        if include_depreciation_schedule:
            asset_dict['depreciation_schedule'] = get_depreciation_schedule(asset_name)
        
        # Add computed depreciation summary
        asset_dict['depreciation_summary'] = get_depreciation_summary(asset_name)
        
        frappe.response['message'] = asset_dict
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Details API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


def get_depreciation_schedule(asset_name):
    """
    Get depreciation schedule entries for an asset
    
    Args:
        asset_name: Name/ID of the asset
    
    Returns:
        List of depreciation schedule entries
    """
    schedule = frappe.get_all(
        'Depreciation Schedule',
        filters={'parent': asset_name},
        fields=[
            'name',
            'idx',
            'schedule_date',
            'depreciation_amount',
            'accumulated_depreciation_amount',
            'journal_entry',
            'finance_book',
            'finance_book_id',
            'shift'
        ],
        order_by='schedule_date asc'
    )
    return schedule


def get_depreciation_summary(asset_name):
    """
    Get computed depreciation summary for an asset
    
    Args:
        asset_name: Name/ID of the asset
    
    Returns:
        Dictionary with depreciation summary
    """
    try:
        asset = frappe.get_doc('Asset', asset_name)
        
        # Calculate total depreciation booked
        total_depreciation_booked = frappe.db.sql("""
            SELECT COALESCE(SUM(depreciation_amount), 0) as total
            FROM `tabDepreciation Schedule`
            WHERE parent = %s AND journal_entry IS NOT NULL AND journal_entry != ''
        """, asset_name)[0][0] or 0
        
        # Calculate pending depreciation entries
        pending_entries = frappe.db.count('Depreciation Schedule', {
            'parent': asset_name,
            'journal_entry': ['in', ['', None]]
        })
        
        # Calculate completed entries
        completed_entries = frappe.db.count('Depreciation Schedule', {
            'parent': asset_name,
            'journal_entry': ['not in', ['', None]]
        })
        
        return {
            'gross_purchase_amount': float(asset.gross_purchase_amount or 0),
            'total_asset_cost': float(asset.total_asset_cost or 0),
            'opening_accumulated_depreciation': float(asset.opening_accumulated_depreciation or 0),
            'total_depreciation_booked': float(total_depreciation_booked),
            'value_after_depreciation': float(asset.value_after_depreciation or 0),
            'is_fully_depreciated': asset.is_fully_depreciated,
            'pending_depreciation_entries': pending_entries,
            'completed_depreciation_entries': completed_entries,
            'calculate_depreciation': asset.calculate_depreciation
        }
    except Exception:
        return {}


@frappe.whitelist(allow_guest = True)
def get_asset_finance_books(asset_name):
    """
    Get finance books (depreciation configuration) for a specific asset
    
    Args:
        asset_name: Name/ID of the asset
    
    Returns:
        List of finance book entries with all depreciation details
    """
    try:
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        if not frappe.has_permission('Asset', 'read', asset_name):
            frappe.throw(_('Not permitted to access this asset'))
        
        finance_books = frappe.get_all(
            'Asset Finance Book',
            filters={'parent': asset_name},
            fields=[
                'name',
                'idx',
                'finance_book',
                'depreciation_method',
                'total_number_of_depreciations',
                'total_number_of_booked_depreciations',
                'daily_prorata_based',
                'shift_based',
                'frequency_of_depreciation',
                'depreciation_start_date',
                'salvage_value_percentage',
                'expected_value_after_useful_life',
                'value_after_depreciation',
                'rate_of_depreciation'
            ],
            order_by='idx asc'
        )
        
        frappe.response['message'] = {
            'asset_name': asset_name,
            'finance_books': finance_books,
            'count': len(finance_books)
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Finance Books API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_asset_depreciation_schedule(asset_name, finance_book=None):
    """
    Get depreciation schedule for a specific asset
    
    Args:
        asset_name: Name/ID of the asset
        finance_book: Optional filter by finance book
    
    Returns:
        List of depreciation schedule entries
    """
    try:
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        if not frappe.has_permission('Asset', 'read', asset_name):
            frappe.throw(_('Not permitted to access this asset'))
        
        filters = {'parent': asset_name}
        if finance_book:
            filters['finance_book'] = finance_book
        
        schedule = frappe.get_all(
            'Depreciation Schedule',
            filters=filters,
            fields=[
                'name',
                'idx',
                'schedule_date',
                'depreciation_amount',
                'accumulated_depreciation_amount',
                'journal_entry',
                'finance_book',
                'finance_book_id',
                'shift'
            ],
            order_by='schedule_date asc'
        )
        
        # Add status to each entry
        for entry in schedule:
            entry['status'] = 'Posted' if entry.get('journal_entry') else 'Pending'
        
        frappe.response['message'] = {
            'asset_name': asset_name,
            'depreciation_schedule': schedule,
            'total_entries': len(schedule),
            'posted_entries': len([s for s in schedule if s.get('journal_entry')]),
            'pending_entries': len([s for s in schedule if not s.get('journal_entry')])
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Depreciation Schedule API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def create_asset(asset_data):
    """
    Create a new asset with finance books (depreciation configuration)
    
    Args:
        asset_data: JSON string containing asset fields including finance_books array
        
    Example asset_data:
        {
            "asset_name": "Test Asset",
            "company": "My Company",
            "item_code": "ITEM-001",
            "gross_purchase_amount": 10000,
            "calculate_depreciation": 1,
            "available_for_use_date": "2025-01-01",
            "finance_books": [
                {
                    "finance_book": "Depreciation Entries",
                    "depreciation_method": "Straight Line",
                    "total_number_of_depreciations": 12,
                    "frequency_of_depreciation": 12,
                    "depreciation_start_date": "2025-01-01",
                    "expected_value_after_useful_life": 1000
                }
            ]
        }
    
    Returns:
        Created asset document with finance_books
    """
    try:
        import json
        
        # Parse asset data
        if isinstance(asset_data, str):
            asset_data = json.loads(asset_data)
        
        # Check if user has permission to create asset
        if not frappe.has_permission('Asset', 'create'):
            frappe.throw(_('Not permitted to create asset'))
        
        # Create new asset
        asset = frappe.get_doc({
            'doctype': 'Asset',
            **asset_data
        })
        
        asset.insert()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset': asset.as_dict(),
            'message': _('Asset created successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Create Asset API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_asset(asset_name, asset_data):
    """
    Update an existing asset including finance books
    
    Args:
        asset_name: Name/ID of the asset
        asset_data: JSON string containing fields to update (can include finance_books)
    
    Returns:
        Updated asset document
    """
    try:
        import json
        
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        # Parse asset data
        if isinstance(asset_data, str):
            asset_data = json.loads(asset_data)
        
        # Check if user has permission to update this asset
        if not frappe.has_permission('Asset', 'write', asset_name):
            frappe.throw(_('Not permitted to update this asset'))
        
        # Get asset
        asset = frappe.get_doc('Asset', asset_name)
        
        # Handle finance_books separately if provided
        finance_books_data = asset_data.pop('finance_books', None)
        
        # Update regular fields
        for key, value in asset_data.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        # Update finance_books if provided
        if finance_books_data is not None:
            asset.set('finance_books', [])
            for fb in finance_books_data:
                asset.append('finance_books', fb)
        
        asset.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset': asset.as_dict(),
            'message': _('Asset updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Asset API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def update_asset_finance_book(asset_name, finance_book_name, finance_book_data):
    """
    Update a specific finance book entry for an asset
    
    Args:
        asset_name: Name/ID of the asset
        finance_book_name: Name of the finance book row to update
        finance_book_data: JSON string containing fields to update
    
    Returns:
        Updated asset document
    """
    try:
        import json
        
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        if not finance_book_name:
            frappe.throw(_('Finance book name is required'))
        
        # Parse finance book data
        if isinstance(finance_book_data, str):
            finance_book_data = json.loads(finance_book_data)
        
        # Check if user has permission to update this asset
        if not frappe.has_permission('Asset', 'write', asset_name):
            frappe.throw(_('Not permitted to update this asset'))
        
        # Get asset
        asset = frappe.get_doc('Asset', asset_name)
        
        # Find and update the specific finance book
        updated = False
        for fb in asset.finance_books:
            if fb.name == finance_book_name:
                for key, value in finance_book_data.items():
                    if hasattr(fb, key):
                        setattr(fb, key, value)
                updated = True
                break
        
        if not updated:
            frappe.throw(_('Finance book entry not found'))
        
        asset.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset': asset.as_dict(),
            'message': _('Finance book updated successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Update Asset Finance Book API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def add_asset_finance_book(asset_name, finance_book_data):
    """
    Add a new finance book entry to an asset
    
    Args:
        asset_name: Name/ID of the asset
        finance_book_data: JSON string containing finance book fields
        
    Example finance_book_data:
        {
            "finance_book": "Depreciation Entries",
            "depreciation_method": "Straight Line",
            "total_number_of_depreciations": 12,
            "frequency_of_depreciation": 12,
            "depreciation_start_date": "2025-01-01",
            "expected_value_after_useful_life": 1000
        }
    
    Returns:
        Updated asset document
    """
    try:
        import json
        
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        # Parse finance book data
        if isinstance(finance_book_data, str):
            finance_book_data = json.loads(finance_book_data)
        
        # Check if user has permission to update this asset
        if not frappe.has_permission('Asset', 'write', asset_name):
            frappe.throw(_('Not permitted to update this asset'))
        
        # Get asset
        asset = frappe.get_doc('Asset', asset_name)
        
        # Add new finance book
        asset.append('finance_books', finance_book_data)
        
        asset.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset': asset.as_dict(),
            'message': _('Finance book added successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Add Asset Finance Book API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def delete_asset_finance_book(asset_name, finance_book_name):
    """
    Delete a finance book entry from an asset
    
    Args:
        asset_name: Name/ID of the asset
        finance_book_name: Name of the finance book row to delete
    
    Returns:
        Updated asset document
    """
    try:
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        if not finance_book_name:
            frappe.throw(_('Finance book name is required'))
        
        # Check if user has permission to update this asset
        if not frappe.has_permission('Asset', 'write', asset_name):
            frappe.throw(_('Not permitted to update this asset'))
        
        # Get asset
        asset = frappe.get_doc('Asset', asset_name)
        
        # Find and remove the specific finance book
        for i, fb in enumerate(asset.finance_books):
            if fb.name == finance_book_name:
                asset.finance_books.remove(fb)
                break
        else:
            frappe.throw(_('Finance book entry not found'))
        
        asset.save()
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'asset': asset.as_dict(),
            'message': _('Finance book deleted successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Delete Asset Finance Book API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def delete_asset(asset_name):
    """
    Delete an asset
    
    Args:
        asset_name: Name/ID of the asset
    
    Returns:
        Success message
    """
    try:
        if not asset_name:
            frappe.throw(_('Asset name is required'))
        
        # Check if user has permission to delete this asset
        if not frappe.has_permission('Asset', 'delete', asset_name):
            frappe.throw(_('Not permitted to delete this asset'))
        
        # Delete asset
        frappe.delete_doc('Asset', asset_name)
        frappe.db.commit()
        
        frappe.response['message'] = {
            'success': True,
            'message': _('Asset deleted successfully')
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Delete Asset API Error')
        frappe.response['message'] = {
            'success': False,
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_asset_filters():
    """
    Get available filter options for assets
    
    Returns:
        {
            "companies": [...],
            "locations": [...],
            "departments": [...],
            "asset_types": [...],
            "manufacturers": [...],
            "device_statuses": [...],
            "finance_books": [...],
            "depreciation_methods": [...]
        }
    """
    try:
        filters = {
            'companies': frappe.get_all('Company', fields=['name'], pluck='name'),
            'locations': frappe.db.get_all('Asset', 
                filters={'location': ['!=', '']}, 
                fields=['location'], 
                distinct=True,
                pluck='location'
            ),
            'departments': frappe.get_all('Department', fields=['name'], pluck='name'),
            'asset_types': frappe.db.get_all('Asset', 
                filters={'custom_asset_type': ['!=', '']}, 
                fields=['custom_asset_type'], 
                distinct=True,
                pluck='custom_asset_type'
            ),
            'manufacturers': frappe.db.get_all('Asset', 
                filters={'custom_manufacturer': ['!=', '']}, 
                fields=['custom_manufacturer'], 
                distinct=True,
                pluck='custom_manufacturer'
            ),
            'device_statuses': frappe.db.get_all('Asset', 
                filters={'custom_device_status': ['!=', '']}, 
                fields=['custom_device_status'], 
                distinct=True,
                pluck='custom_device_status'
            ),
            'finance_books': frappe.get_all('Finance Book', fields=['name'], pluck='name'),
            'depreciation_methods': [
                'Straight Line',
                'Double Declining Balance',
                'Written Down Value',
                'Manual'
            ]
        }
        
        frappe.response['message'] = filters
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Filters API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


@frappe.whitelist(allow_guest = True)
def get_asset_stats():
    """
    Get statistics about assets including depreciation stats
    
    Returns:
        {
            "total_assets": int,
            "by_status": {...},
            "by_company": {...},
            "by_type": {...},
            "total_amount": float,
            "depreciation_stats": {...}
        }
    """
    try:
        # Total assets
        total_assets = frappe.db.count('Asset')
        
        # Assets by device status
        by_status = {}
        status_data = frappe.db.sql("""
            SELECT custom_device_status, COUNT(*) as count
            FROM `tabAsset`
            WHERE custom_device_status IS NOT NULL AND custom_device_status != ''
            GROUP BY custom_device_status
        """, as_dict=True)
        for row in status_data:
            by_status[row.custom_device_status] = row.count
        
        # Assets by company
        by_company = {}
        company_data = frappe.db.sql("""
            SELECT company, COUNT(*) as count
            FROM `tabAsset`
            WHERE company IS NOT NULL AND company != ''
            GROUP BY company
        """, as_dict=True)
        for row in company_data:
            by_company[row.company] = row.count
        
        # Assets by type
        by_type = {}
        type_data = frappe.db.sql("""
            SELECT custom_asset_type, COUNT(*) as count
            FROM `tabAsset`
            WHERE custom_asset_type IS NOT NULL AND custom_asset_type != ''
            GROUP BY custom_asset_type
        """, as_dict=True)
        for row in type_data:
            by_type[row.custom_asset_type] = row.count
        
        # Total amount
        total_amount = frappe.db.sql("""
            SELECT SUM(custom_total_amount) as total
            FROM `tabAsset`
            WHERE custom_total_amount IS NOT NULL
        """)[0][0] or 0
        
        # Depreciation statistics
        depreciation_stats = get_depreciation_stats()
        
        frappe.response['message'] = {
            'total_assets': total_assets,
            'by_status': by_status,
            'by_company': by_company,
            'by_type': by_type,
            'total_amount': float(total_amount),
            'depreciation_stats': depreciation_stats
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Get Asset Stats API Error')
        frappe.response['message'] = {
            'error': str(e)
        }


def get_depreciation_stats():
    """
    Get depreciation statistics across all assets
    
    Returns:
        Dictionary with depreciation statistics
    """
    try:
        # Total gross purchase amount
        total_gross_amount = frappe.db.sql("""
            SELECT COALESCE(SUM(gross_purchase_amount), 0) as total
            FROM `tabAsset`
        """)[0][0] or 0
        
        # Total accumulated depreciation
        total_accumulated_depreciation = frappe.db.sql("""
            SELECT COALESCE(SUM(ds.depreciation_amount), 0) as total
            FROM `tabDepreciation Schedule` ds
            INNER JOIN `tabAsset` a ON ds.parent = a.name
            WHERE ds.journal_entry IS NOT NULL AND ds.journal_entry != ''
        """)[0][0] or 0
        
        # Total value after depreciation
        total_value_after_depreciation = frappe.db.sql("""
            SELECT COALESCE(SUM(value_after_depreciation), 0) as total
            FROM `tabAsset`
        """)[0][0] or 0
        
        # Assets with depreciation enabled
        assets_with_depreciation = frappe.db.count('Asset', {'calculate_depreciation': 1})
        
        # Fully depreciated assets
        fully_depreciated_assets = frappe.db.count('Asset', {'is_fully_depreciated': 1})
        
        # Pending depreciation entries
        pending_entries = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabDepreciation Schedule`
            WHERE (journal_entry IS NULL OR journal_entry = '')
        """)[0][0] or 0
        
        # By depreciation method
        by_depreciation_method = {}
        method_data = frappe.db.sql("""
            SELECT depreciation_method, COUNT(*) as count
            FROM `tabAsset Finance Book`
            WHERE depreciation_method IS NOT NULL AND depreciation_method != ''
            GROUP BY depreciation_method
        """, as_dict=True)
        for row in method_data:
            by_depreciation_method[row.depreciation_method] = row.count
        
        return {
            'total_gross_amount': float(total_gross_amount),
            'total_accumulated_depreciation': float(total_accumulated_depreciation),
            'total_value_after_depreciation': float(total_value_after_depreciation),
            'assets_with_depreciation': assets_with_depreciation,
            'fully_depreciated_assets': fully_depreciated_assets,
            'pending_depreciation_entries': pending_entries,
            'by_depreciation_method': by_depreciation_method
        }
    except Exception:
        return {}


@frappe.whitelist(allow_guest = True)
def search_assets(search_term, limit=10):
    """
    Search assets by name, serial number, or other fields
    
    Args:
        search_term: Search query string
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of matching assets
    """
    try:
        if not search_term:
            frappe.response['message'] = []
            return
        
        search_term = f"%{search_term}%"
        
        assets = frappe.db.sql("""
            SELECT 
                name,
                asset_name,
                custom_serial_number,
                location,
                company,
                custom_device_status,
                calculate_depreciation,
                value_after_depreciation,
                is_fully_depreciated
            FROM `tabAsset`
            WHERE 
                asset_name LIKE %(search)s
                OR custom_serial_number LIKE %(search)s
                OR location LIKE %(search)s
                OR custom_manufacturer LIKE %(search)s
            LIMIT %(limit)s
        """, {
            'search': search_term,
            'limit': int(limit)
        }, as_dict=True)
        
        frappe.response['message'] = assets
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Search Assets API Error')
        frappe.response['message'] = {
            'error': str(e)
        }