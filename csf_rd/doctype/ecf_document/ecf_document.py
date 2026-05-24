import frappe
from frappe.model.document import Document

class ECFDocument(Document):

	def send_to_dgii(self):
		"""Lógica de envío a DGII (simulada por ahora)"""

		try:
			# generar XML básico
			self.xml = f"""
            <eCF>
                <NCF>{self.ncf}</NCF>
                <RNCEmisor>{self.rnc_emisor}</RNCEmisor>
                <RNCComprador>{self.rnc_comprador}</RNCComprador>
                <Monto>{self.monto_total}</Monto>
            </eCF>
            """

			# simular envío
			self.status = "Sent"
			self.track_id = f"TRACK-{self.name}"

			# QR simple
			self.qr_url = f"https://dgii.gov.do/consulta?trackId={self.track_id}"

			self.save(ignore_permissions=True)

		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				"Error en envío DGII"
			)

def send_to_dgii(doc, method):
	"""Hook de Sales Invoice → eCF"""

	try:
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

		# ✅ aquí se usa el método de la clase
		ecf.send_to_dgii()

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			"Error hook eCF"
		)
