from . import __version__ as app_version

app_name = "csf_rd"
app_title = "República Dominicana ERPNext Customization"
app_publisher = "CSF RD Team"
app_description = "ERPNext DGII Integration RD"
app_icon = "drag"
app_color = "blue"
app_email = "support@csf-rd.com"
app_license = "GNU General Public License (v3)"

required_apps = ["erpnext"]

# Fixtures
fixtures = [
    {"doctype": "Custom Field"},
    {
        "doctype": "DocType Link",
        "filters": [
            ["link_doctype", "in", ["DGII Customer", "eCF Document"]]
        ]
    }
]

# JS overrides
doctype_js = {
    "Customer": "csf_rd/overrides/customer.js",
    "Sales Invoice": "csf_rd/overrides/sales_invoice.js"
}

# Hooks eventos
doc_events = {
    "Customer": {
        "before_save": "csf_rd.overrides.customer.validate_rnc_format"
    },
    "Supplier": {
        "before_save": "csf_rd.overrides.supplier.validate_rnc_format"
    },
    "Sales Invoice": {
        "before_save": "csf_rd.overrides.sales_invoice.validate_ncf",
        "on_submit": "csf_rd.doctype.ecf_document.ecf_document.send_to_dgii"
    }
}

# Jinja
jinja = {
    "methods": [
        "csf_rd.utils.qr_code_generator.generate_ecf_qr_code",
        "csf_rd.utils.dgii_utils.format_rnc"
    ]
}