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
            "pos_profile": pos_profile
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

    # Fetch related Sales Invoices
    related_invoices = frappe.get_all(
        "Sales Invoice Item",
        filters={"sales_order": name, "docstatus": 1},
        fields=["parent"],
        distinct=True
    )
    order_data["related_invoices"] = [d.parent for d in related_invoices]

    # Fetch related Delivery Notes
    related_delivery_notes = frappe.get_all(
        "Delivery Note Item",
        filters={"against_sales_order": name, "docstatus": 1},
        fields=["parent"],
        distinct=True
    )
    order_data["related_delivery_notes"] = [d.parent for d in related_delivery_notes]
    
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
def make_delivery_note_from_sales_order(source_name):
    """Return mapped Delivery Note doc from Sales Order without inserting."""
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    doc = make_delivery_note(source_name)
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

@frappe.whitelist()
def get_sales_order_for_edit(name):
	"""
	Return Sales Order data prepared for loading into the POS cart for amendment.
	Allows cancelled orders since they are the primary amend source.
	"""
	if not name:
		frappe.throw(_("Sales Order name is required"))

	if not frappe.has_permission("Sales Order", "read", name):
		frappe.throw(_("You do not have permission to view this Sales Order"))

	doc = frappe.get_doc("Sales Order", name)
	return doc.as_dict()

@frappe.whitelist()
def amend_sales_order(old_name, new_doc):
	"""
	Amend a Sales Order using Frappe's standard copy_doc amendment mechanism.

	- Cancelled SO (docstatus=2): directly create an amendment linked via amended_from.
	- Submitted SO (docstatus=1): cancel it first, then create the amendment.
	- Draft SO (docstatus=0): delete it; the new SO is a fresh doc (no amended_from).

	Uses frappe.copy_doc() so that Frappe's naming pipeline sets amended_from
	correctly (e.g. SO-0001 → SO-0001-1).

	Returns the name of the new Sales Order.
	"""
	import json as _json

	if isinstance(new_doc, str):
		new_doc = _json.loads(new_doc)

	if not old_name:
		frappe.throw(_("Old Sales Order name is required"))

	if not frappe.has_permission("Sales Order", "write", old_name):
		frappe.throw(_("You do not have permission to amend this Sales Order"))

	old_so = frappe.get_doc("Sales Order", old_name)
	use_amendment = False

	if old_so.docstatus == 2:
		# Already cancelled — create an amendment directly
		use_amendment = True
	elif old_so.docstatus == 1:
		# Submitted — cancel it first, then amend
		old_so.cancel()
		use_amendment = True
	elif old_so.docstatus == 0:
		# Draft — just delete it; new doc will be a plain fresh SO
		frappe.delete_doc("Sales Order", old_name, force=True, ignore_permissions=True)
		use_amendment = False

	if use_amendment:
		# ── Use Frappe's proper amendment mechanism ────────────────────────────
		# frappe.copy_doc keeps amended_from through the full naming pipeline.
		old_so_reloaded = frappe.get_doc("Sales Order", old_name)
		so = frappe.copy_doc(old_so_reloaded)
		so.docstatus = 0
		so.amended_from = old_name   # Frappe naming will produce SO-XXXX-1 etc.

		# Replace items with those from the POS cart
		so.set("items", [])
		for item in new_doc.get("items") or []:
			so.append("items", {
				"item_code":         item.get("item_code"),
				"item_name":         item.get("item_name"),
				"description":       item.get("description") or item.get("item_name"),
				"uom":               item.get("uom"),
				"qty":               item.get("qty"),
				"rate":              item.get("rate"),
				"price_list_rate":   item.get("price_list_rate") or item.get("rate"),
				"warehouse":         item.get("warehouse"),
				"stock_uom":         item.get("stock_uom"),
				"conversion_factor": item.get("conversion_factor") or 1,
				"discount_percentage": item.get("discount_percentage") or 0,
			})

		# Overlay scalar fields the user may have changed
		for field in ("customer", "delivery_date", "currency",
		              "selling_price_list", "pos_profile", "company"):
			if field in new_doc and new_doc[field]:
				setattr(so, field, new_doc[field])

	else:
		# ── Plain fresh SO (was a Draft, no amendment link needed) ─────────────
		for field in ("name", "docstatus", "amended_from", "creation", "modified",
		              "modified_by", "owner", "idx"):
			new_doc.pop(field, None)
		for table_field in ("items", "taxes", "payment_schedule", "sales_team"):
			for row in new_doc.get(table_field) or []:
				row.pop("name", None)
				row.pop("parent", None)
		so = frappe.get_doc({"doctype": "Sales Order", **new_doc})

	so.insert()
	so.submit()
	frappe.db.commit()
	return so.name
