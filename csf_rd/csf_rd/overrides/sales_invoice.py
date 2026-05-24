import frappe
from frappe import _
import re


def validate_ncf(doc, method):
    """Validar NCF en factura"""

    if doc.ncf:
        if not re.match(r'^[A-Z]\d{11}$', doc.ncf):
            frappe.throw(_("NCF inválido: debe ser letra + 11 dígitos"))


def send_to_dgii(doc, method):
    """Enviar factura a DGII"""

    try:
        customer = frappe.get_doc("Customer", doc.customer)

        if not customer.rnc:
            return

        rnc_comprador = customer.rnc

        existing = frappe.db.get_value(
            "eCF Document",
            {"sales_invoice": doc.name},
            "name"
        )

        data = {
            "company": doc.company,
            "sales_invoice": doc.name,
            "ncf": doc.ncf or generate_ncf(doc),
            "rnc_emisor": get_company_rnc(doc.company),
            "rnc_comprador": rnc_comprador,
            "fecha_emision": doc.posting_date,
            "monto_total": doc.grand_total
        }

        if existing:
            ecf = frappe.get_doc("eCF Document", existing)
            ecf.update(data)
            ecf.save(ignore_permissions=True)
        else:
            data["doctype"] = "eCF Document"
            ecf = frappe.get_doc(data).insert(ignore_permissions=True)

        ecf.send_to_dgii()

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Error enviando eCF a DGII"
        )


# ✅ generación simple (para pruebas)
def generate_ncf(doc):
    """Generar NCF simple (NO oficial DGII)"""

    last = frappe.db.get_value(
        "Sales Invoice",
        {},
        "ncf",
        order_by="creation desc"
    )

    if last and len(last) >= 12:
        seq = int(last[1:]) + 1
    else:
        seq = 1

    return f"A{seq:011d}"


def get_company_rnc(company):
    company_doc = frappe.get_doc("Company", company)
    return company_doc.tax_id or company_doc.default_tax_id