# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def get_delivery_notes(pos_profile, limit=50):
    """
    Get Delivery Notes for a POS Profile.
    """
    if not pos_profile:
        frappe.throw(_("POS Profile is required"))

    limit = cint(limit)
    if limit <= 0:
        limit = 50

    delivery_notes = frappe.get_all(
        "Delivery Note",
        filters={
            "pos_profile": pos_profile,
            "docstatus": ["!=", 2]  # Exclude cancelled
        },
        fields=[
            "name",
            "customer",
            "customer_name",
            "posting_date as transaction_date",
            "grand_total",
            "status",
            "currency"
        ],
        order_by="posting_date desc, name desc",
        limit=limit
    )
    
    return delivery_notes

@frappe.whitelist()
def get_delivery_note(name):
    """
    Get detailed Delivery Note.
    """
    if not name:
        frappe.throw(_("Delivery Note name is required"))

    if not frappe.has_permission("Delivery Note", "read", name):
        frappe.throw(_("You do not have permission to view this Delivery Note"))

    doc = frappe.get_doc("Delivery Note", name)
    return doc.as_dict()

@frappe.whitelist()
def make_invoice_from_delivery_note(source_name):
    from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
    doc = make_sales_invoice(source_name)
    doc.insert()
    return doc.name

@frappe.whitelist()
def make_delivery_note_from_sales_order(source_name):
    """Return mapped Delivery Note doc from Sales Order without inserting."""
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    doc = make_delivery_note(source_name)
    return doc.as_dict()

@frappe.whitelist()
def make_delivery_note_from_invoice(source_name):
    """Return mapped Delivery Note doc from Sales Invoice without inserting."""
    from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
    doc = make_delivery_note(source_name)
    return doc.as_dict()

@frappe.whitelist()
def create_delivery_note(doc):
    """
    Create a Delivery Note from a dict.
    """
    if isinstance(doc, str):
        import json
        doc = json.loads(doc)
    
    dn = frappe.get_doc(doc)
    dn.insert()
    dn.submit()
    return dn.name
