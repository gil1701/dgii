import frappe
from frappe.model.document import Document

class ECFDocument(Document):
	# Usar controlador estándar de Frappe - sin lógica personalizada compleja
	pass

import frappe

def send_to_dgii(doc, method):
	"""Hook que se ejecuta al hacer submit de la factura"""

	try:
		# buscar si ya existe eCF Document
		ecf_name = frappe.db.get_value(
			"eCF Document",
			{"sales_invoice": doc.name},
			"name"
		)

		if ecf_name:
			ecf = frappe.get_doc("eCF Document", ecf_name)
		else:
			ecf = frappe.get_doc({
				"doctype": "eCF Document",
				"company": doc.company,
				"sales_invoice": doc.name,
				"ncf": doc.ncf,
				"rnc_emisor": frappe.db.get_value("Company", doc.company, "tax_id"),
				"rnc_comprador": frappe.db.get_value("Customer", doc.customer, "rnc"),
				"fecha_emision": doc.posting_date,
				"monto_total": doc.grand_total
			})
			ecf.insert(ignore_permissions=True)

		# aquí luego conectas DGII
		ecf.status = "Draft"
		ecf.save(ignore_permissions=True)

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			"Error en send_to_dgii"
		)