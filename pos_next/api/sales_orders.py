# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint

@frappe.whitelist()
def get_sales_orders(pos_profile, limit=50):
    """
    Get Sales Orders for a POS Profile.
    """
    if not pos_profile:
        frappe.throw(_("POS Profile is required"))

    limit = cint(limit)
    if limit <= 0:
        limit = 50

    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "pos_profile": pos_profile,
            "docstatus": ["!=", 2]  # Exclude cancelled
        },
        fields=[
            "name",
            "customer",
            "customer_name",
            "transaction_date",
            "delivery_date",
            "grand_total",
            "advance_paid",
            "status",
            "currency"
        ],
        order_by="transaction_date desc, name desc",
        limit=limit
    )
    
    return sales_orders

@frappe.whitelist()
def get_sales_order(name):
    """
    Get detailed Sales Order with enriched payment info from Advances.
    """
    if not name:
        frappe.throw(_("Sales Order name is required"))

    if not frappe.has_permission("Sales Order", "read", name):
        frappe.throw(_("You do not have permission to view this Sales Order"))

    doc = frappe.get_doc("Sales Order", name)
    order_data = doc.as_dict()

    # Map Advances to payments list expected by frontend
    # This ensures we have the Payment Entry reference for printing
    payments = []
    
    # Check for standard Advances table
    if order_data.get("advances"):
        for adv in order_data.get("advances"):
            # Fetch mode of payment from the linked Payment Entry
            mode_of_payment = frappe.db.get_value("Payment Entry", adv.reference_name, "mode_of_payment") or "Unknown"
            
            payments.append({
                "mode_of_payment": mode_of_payment,
                "amount": adv.allocated_amount,
                "voucher_no": adv.reference_name,
                "voucher_type": "Payment Entry", # CRITICAL for print utility
                "creation": adv.creation,
                "account": adv.remarks, # storing remarks/account info if needed
            })
            
    # If no advances but has custom payments table (fallback)
    elif order_data.get("payments"):
        # This is existing behavior, but likely lacks voucher_no for proper PE printing
        payments = order_data.get("payments")
    
    order_data["payments"] = payments
    
    return order_data

@frappe.whitelist()
def cancel_sales_order(name):
    """
    Cancel a Sales Order.
    """
    if not name:
        frappe.throw(_("Sales Order name is required"))

    if not frappe.has_permission("Sales Order", "cancel", name):
        frappe.throw(_("You do not have permission to cancel this Sales Order"))

    doc = frappe.get_doc("Sales Order", name)
    if doc.docstatus == 2:
        frappe.throw(_("Sales Order is already cancelled"))
    
    if doc.docstatus == 0:
        frappe.delete_doc("Sales Order", name)
        return {"status": "deleted"}
    
    doc.cancel()
    return {"status": "cancelled"}

@frappe.whitelist()
def make_invoice_from_sales_order(source_name):
    """Return mapped Sales Invoice doc from Sales Order without inserting."""
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    doc = make_sales_invoice(source_name)
    return doc.as_dict()

@frappe.whitelist()
def create_invoice(doc):
    """Create a Sales Invoice from a dict (after user edits in the form)."""
    if isinstance(doc, str):
        import json
        doc = json.loads(doc)

    si = frappe.get_doc(doc)
    si.insert()
    si.submit()
    return si.name
