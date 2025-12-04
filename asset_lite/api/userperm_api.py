import frappe
from frappe import _

# ============================================================================
# CONFIGURATION: Define field mappings for each doctype
# Add new doctypes here as needed - this is the ONLY place you need to update
# ============================================================================

DOCTYPE_PERMISSION_MAPPINGS = {
    "Asset": {
        "Company": "company",
        "Location": "location",
        "Department": "department",
        "Manufacturer": "custom_manufacturer",
        "Supplier": "supplier",
        "Modality": "custom_modality",
        "Cost Center": "cost_center",
        "Asset Type":"custom_asset_type",
        "Asset Category": "asset_category"
    },
    "Work_Order": {
        "Company": "company",
        "Location": "location",
        "Department": "department"
    },
    "Asset Maintenance": {
        "Company": "company",
        "Asset": "asset_name",
        "Supplier": "supplier"
    },
    "Asset Maintenance Log": {
        "Company": "company",
        "Asset": "asset_name"
    }
    # Add more doctypes as needed - just add them here!
}


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def is_system_user(user):
    """Check if user is Administrator or has System Manager role."""
    if user == "Administrator":
        return True
    
    roles = frappe.get_roles(user)
    return "System Manager" in roles


# ============================================================================
# CORE API FUNCTIONS - These 4 functions handle everything
# ============================================================================

@frappe.whitelist(allow_guest = True)
def get_user_permissions(user=None):
    """
    Get all user permissions for the logged-in user.
    
    Returns:
        dict: User permissions grouped by 'allow' doctype
    """
    if not user:
        user = frappe.session.user
    
    if is_system_user(user):
        return {
            "is_admin": True,
            "permissions": {},
            "user": user,
            "total_permissions": 0
        }
    
    permissions = frappe.get_all(
        "User Permission",
        filters={"user": user},
        fields=["name", "allow", "for_value", "is_default", "apply_to_all_doctypes", "applicable_for"],
        order_by="allow asc"
    )
    
    # Group by 'allow' doctype
    grouped = {}
    for perm in permissions:
        allow_doctype = perm.get("allow")
        if allow_doctype not in grouped:
            grouped[allow_doctype] = []
        grouped[allow_doctype].append({
            "for_value": perm.get("for_value"),
            "is_default": perm.get("is_default"),
            "apply_to_all_doctypes": perm.get("apply_to_all_doctypes"),
            "applicable_for": perm.get("applicable_for")
        })
    
    return {
        "is_admin": False,
        "permissions": grouped,
        "user": user,
        "total_permissions": len(permissions),
        "permission_types": list(grouped.keys())
    }


@frappe.whitelist(allow_guest = True)
def get_permission_filters(target_doctype, user=None):
    """
    Get permission filters for ANY doctype.
    This is the MAIN function - use this for all doctypes.
    
    Args:
        target_doctype: The doctype (e.g., "Asset", "Work Order", "Project")
        user: Optional user email
        
    Returns:
        dict: Filters to apply for queries
    """
    if not user:
        user = frappe.session.user
    
    # System users have full access
    if is_system_user(user):
        return {
            "is_admin": True,
            "filters": {},
            "restrictions": {},
            "target_doctype": target_doctype,
            "user": user
        }
    
    # Get field mapping for this doctype
    field_mapping = DOCTYPE_PERMISSION_MAPPINGS.get(target_doctype, {})
    
    if not field_mapping:
        return {
            "is_admin": False,
            "filters": {},
            "restrictions": {},
            "target_doctype": target_doctype,
            "user": user,
            "warning": f"No permission mapping defined for {target_doctype}"
        }
    
    filters = {}
    restrictions = {}
    
    for allow_doctype, target_field in field_mapping.items():
        permissions = frappe.get_all(
            "User Permission",
            filters={
                "user": user,
                "allow": allow_doctype
            },
            fields=["for_value", "applicable_for", "apply_to_all_doctypes"]
        )
        
        if permissions:
            # Filter permissions that apply to this doctype
            applicable = [
                p for p in permissions 
                if p.get("apply_to_all_doctypes") == 1 
                or not p.get("applicable_for") 
                or p.get("applicable_for") == target_doctype
            ]
            
            if applicable:
                allowed_values = list(set([p.get("for_value") for p in applicable]))
                filters[target_field] = ["in", allowed_values]
                restrictions[allow_doctype] = {
                    "field": target_field,
                    "values": allowed_values,
                    "count": len(allowed_values)
                }
    
    return {
        "is_admin": False,
        "filters": filters,
        "restrictions": restrictions,
        "target_doctype": target_doctype,
        "user": user,
        "total_restrictions": len(restrictions)
    }


@frappe.whitelist(allow_guest = True)
def get_allowed_values(allow_doctype, user=None):
    """
    Get allowed values for a specific permission type.
    
    Args:
        allow_doctype: e.g., "Company", "Location", "Department"
        user: Optional user email
        
    Returns:
        dict: List of allowed values
    """
    if not user:
        user = frappe.session.user
    
    if is_system_user(user):
        return {
            "is_admin": True,
            "allowed_values": [],
            "has_restriction": False
        }
    
    permissions = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": allow_doctype},
        fields=["for_value", "is_default"]
    )
    
    allowed_values = list(set([p.get("for_value") for p in permissions]))
    default_value = next((p.get("for_value") for p in permissions if p.get("is_default")), None)
    
    return {
        "is_admin": False,
        "allowed_values": sorted(allowed_values),
        "default_value": default_value,
        "has_restriction": len(allowed_values) > 0,
        "allow_doctype": allow_doctype
    }


@frappe.whitelist(allow_guest = True)
def check_document_access(doctype, docname, user=None):
    """
    Check if user has access to a specific document.
    
    Args:
        doctype: e.g., "Asset", "Work Order"
        docname: The document name/ID
        user: Optional user email
        
    Returns:
        dict: Access status
    """
    if not user:
        user = frappe.session.user
    
    if is_system_user(user):
        return {"has_access": True, "is_admin": True}
    
    try:
        doc = frappe.get_doc(doctype, docname)
    except frappe.DoesNotExistError:
        return {"has_access": False, "error": f"{doctype} '{docname}' not found"}
    except frappe.PermissionError:
        return {"has_access": False, "error": "Permission denied"}
    
    # Get permission filters
    perm_result = get_permission_filters(doctype, user)
    
    if perm_result.get("is_admin"):
        return {"has_access": True, "is_admin": True}
    
    restrictions = perm_result.get("restrictions", {})
    
    if not restrictions:
        return {"has_access": True, "no_restrictions": True}
    
    # Check each restriction
    for allow_doctype, info in restrictions.items():
        field = info.get("field")
        allowed_values = info.get("values", [])
        doc_value = getattr(doc, field, None)
        
        if doc_value and doc_value not in allowed_values:
            return {
                "has_access": False,
                "denied_by": allow_doctype,
                "field": field,
                "document_value": doc_value,
                "allowed_values": allowed_values
            }
    
    return {"has_access": True}


@frappe.whitelist(allow_guest = True)
def get_configured_doctypes():
    """Get list of doctypes that have permission mappings configured."""
    return {
        "doctypes": list(DOCTYPE_PERMISSION_MAPPINGS.keys()),
        "mappings": {
            dt: list(mapping.keys()) 
            for dt, mapping in DOCTYPE_PERMISSION_MAPPINGS.items()
        }
    }


@frappe.whitelist(allow_guest = True)
def get_user_defaults(user=None):
    """Get default values from user permissions (where is_default=1)."""
    if not user:
        user = frappe.session.user
    
    if is_system_user(user):
        return {"is_admin": True, "defaults": {}}
    
    permissions = frappe.get_all(
        "User Permission",
        filters={"user": user, "is_default": 1},
        fields=["allow", "for_value"]
    )
    
    defaults = {p.get("allow"): p.get("for_value") for p in permissions}
    
    return {"is_admin": False, "defaults": defaults}
