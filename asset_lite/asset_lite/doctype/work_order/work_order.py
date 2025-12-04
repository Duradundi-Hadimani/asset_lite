# Copyright (c) 2024, seyfert and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Work_Order(Document):
    @frappe.whitelist()
    def check_site_version(self):
        # Fetch the site version type from the site configuration
        site_version_type = frappe.local.conf.get("site_version_type", "")
        return site_version_type

    '''
    @frappe.whitelist()
    @frappe.validate_and_sanitize_search_inputs
    def get_team_members(doctype, txt, searchfield, start, page_len, filters):
        return frappe.db.get_values(
            "Maintenance Team Member", {"parent": filters.get("maintenance_team")}, "team_member"
        )

    '''

    
   
