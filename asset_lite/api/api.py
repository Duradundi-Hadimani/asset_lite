import frappe
 
def set_default_homepage():
   
    """
    Set the default workspace based on the user's role.
    """
    # Get the current user
    current_user = frappe.session.user
 
    # Skip for system users
    if current_user in ("Administrator", "Guest"):
        return
 
    # Define role-based workspaces
    role_based_workspaces = {
        "Maintenance Manager": "asset-management",
        #"Maintenance User": "asset-management",
        #"Technician": "asset-management"
    }
 
    # Get the user's roles
    user_roles = frappe.get_roles(current_user)
 
    # Determine the default workspace
    for role, workspace in role_based_workspaces.items():
        if role in user_roles:
            # Set the session home page
            frappe.local.response["home_page"] = f"/app/{workspace}"
            return