app_name = "asset_lite"
app_title = "Asset Lite"
app_publisher = "seyfert"
app_description = "Asset Management System"
app_email = "seyfert@example.com"
app_license = "mit"

# Apps
# ------------------
# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "asset_lite",
# 		"logo": "/assets/asset_lite/logo.png",
# 		"title": "Asset Lite",
# 		"route": "/asset_lite",
# 		"has_permission": "asset_lite.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/asset_lite/css/asset_lite.css"
app_include_css = "/assets/asset_lite/css/custom.css?v=1.0.2"
# app_include_js = "/assets/asset_lite/js/asset_lite.js"
app_include_js = "/assets/asset_lite/js/dashboard_embed.js?v=1.0.28"

# include js, css files in header of web template
# web_include_css = "/assets/asset_lite/css/asset_lite.css"
# web_include_js = "/assets/asset_lite/js/asset_lite.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "asset_lite/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Asset Maintenance Log" : "public/js/custom_asset_maintenance_log.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "asset_lite/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"
on_session_creation = "asset_lite.api.api.set_default_homepage"


# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "asset_lite.utils.jinja_methods",
# 	"filters": "asset_lite.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "asset_lite.install.before_install"
# after_install = "asset_lite.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "asset_lite.uninstall.before_uninstall"
# after_uninstall = "asset_lite.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "asset_lite.utils.before_app_install"
# after_app_install = "asset_lite.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "asset_lite.utils.before_app_uninstall"
# after_app_uninstall = "asset_lite.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "asset_lite.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
#    "Supplier Scorecard Criteria":"asset_lite.supplier_score_criteria_override.CustomSupplierScorecardCriteria"
# 	"ToDo": "custom_app.overrides.CustomToDo"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Asset":{
        "before_save": "asset_lite.public.py.asset.generate_asset_qr"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"asset_lite.tasks.all"
# 	],
# 	"daily": [
# 		"asset_lite.tasks.daily"
# 	],
# 	"hourly": [
# 		"asset_lite.tasks.hourly"
# 	],
# 	"weekly": [
# 		"asset_lite.tasks.weekly"
# 	],
# 	"monthly": [
# 		"asset_lite.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "asset_lite.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "asset_lite.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "asset_lite.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["asset_lite.utils.before_request"]
# after_request = ["asset_lite.utils.after_request"]

# Job Events
# ----------
# before_job = ["asset_lite.utils.before_job"]
# after_job = ["asset_lite.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"asset_lite.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
   "Workflow",
    "Workflow State",
    "Workflow Action Master",
    "Custom DocPerm",
    "Translation",

    {"doctype": "Custom Field", "filters": [
        [
            "module", "=", "Asset Lite"
        ]
    ]},
    {"doctype": "Property Setter", "filters": [
        [
            "module", "=", "Asset Lite"
        ]
    ]},
    # {
    #     "doctype": "Role",
    #     "filters": [
    #         ["creation", ">", "2024-09-12"]
    #     ]
    # },
    {"doctype": "Workspace", "filters": [
        [
            "module", "=", "Asset Lite"
        ]
    ]},
    {"dt": "Print Format", "filters": {"custom_format": 1}},
    {"doctype": "Client Script", "filters": [["module","=","Asset Lite"]]},
    {"doctype": "Server Script", "filters": [["module","=","Asset Lite"]]},
    {"doctype": "Notification", "filters": [["is_standard","=",0]]},
    {"doctype": "Report", "filters": [["module","=","Asset Lite"]]},
    {
        "doctype": "Dashboard Chart",
        "filters": [
            ["is_standard", "=", 0]
        ]
    },
    {
        "doctype": "Number Card",
        "filters": [
            ["is_standard", "=", 0]
        ]
    },
    {
        "doctype": "Dashboard",
        "filters": [
            ["is_standard", "=", 0]
        ]
    },

    # {
    #     "doctype": "Company",
    #     "filters": [
    #         ["domain", "=", "Healthcare"]
    #     ]
    # },
    {
        "doctype": "User Permission",
        "filters": [
            ["allow", "=", "Hospital"]
        ]
    },
]
