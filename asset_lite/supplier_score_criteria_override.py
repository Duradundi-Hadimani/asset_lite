import re

import frappe
from frappe import _
from frappe.model.document import Document

from erpnext.buying.doctype.supplier_scorecard_criteria.supplier_scorecard_criteria import SupplierScorecardCriteria

class CustomSupplierScorecardCriteria(SupplierScorecardCriteria):
    def validate_formula(self):
        # Evaluate the formula with 0's to ensure it is valid
        test_formula = self.formula.replace("\r", "").replace("\n", "")

        # Find and replace all placeholders with 0
        regex = r"\{(.*?)\}"
        mylist = re.finditer(regex, test_formula, re.MULTILINE | re.DOTALL)
        for match in mylist:
            test_formula = test_formula.replace("{" + match.group(1) + "}", "0")

        try:
            # Use safe_eval with a custom safe division function
            frappe.safe_eval(
                test_formula,
                None,
                {
                    "max": max,
                    "min": min,
                    "safe_div": lambda x, y: x / y if y != 0 else 0,  # Safe division logic
                },
            )
        except Exception as e:
            # Throw an error if formula evaluation fails
            frappe.throw(_("Error evaluating the criteria formula: {0}").format(str(e)))