import frappe
from frappe import _
import re

def validate_rnc_format(doc, method):
    """Validar formato de RNC en Customer"""
    
    if doc.rnc:
        # limpiar guiones
        rnc = doc.rnc.replace("-", "").strip()
        
        # validar longitud
        if not re.match(r'^\d{9}(\d{2})?$', rnc):
            frappe.throw(_("El RNC debe tener 9 u 11 dígitos"))
        
        # guardar limpio
        doc.rnc = rnc
        
        # opcional: sincronizar con tax_id
        doc.tax_id = rnc
        
        create_or_update_dgii_customer(doc)


def create_or_update_dgii_customer(customer_doc):
    """Crear o actualizar registro en DGII Customer"""
    
    if not customer_doc.company:
        return
    
    try:
        existing = frappe.db.get_value(
            "DGII Customer",
            {
                "rnc": customer_doc.rnc,
                "company": customer_doc.company
            },
            "name"
        )

        data = {
            "rnc": customer_doc.rnc,
            "company": customer_doc.company,
            "customer_name": customer_doc.customer_name,
            "email": customer_doc.email_id,
            "phone": customer_doc.mobile_no or customer_doc.phone,
            "address": get_customer_address(customer_doc),
            "customer_type": "Individual" if customer_doc.customer_type == "Individual" else "Company"
        }

        if existing:
            dgii = frappe.get_doc("DGII Customer", existing)
            dgii.update(data)
            dgii.save(ignore_permissions=True)
        else:
            data["doctype"] = "DGII Customer"
            frappe.get_doc(data).insert(ignore_permissions=True)

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Error creando DGII Customer"
        )


def get_customer_address(customer_doc):
    """Construir dirección del cliente"""
    
    if not customer_doc.customer_primary_address:
        return ""

    try:
        addr = frappe.get_doc("Address", customer_doc.customer_primary_address)

        parts = [
            addr.address_line1,
            addr.address_line2,
            addr.city,
            addr.state,
            addr.country
        ]

        return ", ".join([p for p in parts if p])

    except Exception:
        return ""