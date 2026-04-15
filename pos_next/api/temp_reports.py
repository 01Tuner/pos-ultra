import frappe
from frappe.modules import export_doc

def run():
    frappe.flags.in_import = False
    frappe.conf.developer_mode = 1
    
    for r in ["POS Customer Wise Summary", "POS Sales Order Item Wise Summary"]:
        doc = frappe.get_doc("Report", r)
        doc.is_standard = "Yes"
        doc.module = "POS Next"
        export_doc(doc)
        print(f"Exported {r}")

