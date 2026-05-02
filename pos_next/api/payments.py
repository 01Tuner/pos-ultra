import frappe
from frappe import _
from frappe.utils import flt, nowdate, cint
import json

@frappe.whitelist()
def get_customer_outstanding_invoices(customer):
    """
    Get all outstanding sales invoices for a specific customer.
    Returns: List of dicts with outstanding amount info.
    """
    if not customer:
        frappe.throw(_("Customer is required"))
        
    invoices = frappe.db.sql("""
        SELECT 
            name, 
            posting_date, 
            grand_total, 
            outstanding_amount, 
            status,
            currency
        FROM `tabSales Invoice`
        WHERE 
            customer = %s 
            AND docstatus = 1 
            AND outstanding_amount > 0
        ORDER BY posting_date ASC
    """, (customer,), as_dict=True)

    return invoices

@frappe.whitelist()
def create_customer_payment(customer, mode_of_payment, amount, pos_profile=None, allocations=None, pos_opening_shift=None, write_off_amount=0):
    """
    Creates a Payment Entry to settle customer outstanding balances.
    allocations: JSON string of list
                 [{"name": "SINV-001", "allocated_amount": 100}]
    """
    amount = flt(amount)
    write_off_amount = flt(write_off_amount)
    
    if amount <= 0 and write_off_amount <= 0:
        frappe.throw(_("Payment amount or write off amount must be greater than zero"))

    if not allocations:
        allocations = "[]"
        
    if isinstance(allocations, str):
        allocations = json.loads(allocations)

    # 1. We need an account from Mode of Payment
    try:
        from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
        company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")
        
        # If pos_profile is passed, use its company
        if pos_profile:
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            company = profile_doc.company

        account_info = get_bank_cash_account(mode_of_payment, company)
        if not account_info or not account_info.get("account"):
            frappe.throw(_("Could not determine payment account for Mode of Payment: {0}").format(mode_of_payment))
        paid_to = account_info.get("account")
    except Exception as e:
        frappe.throw(_("Failed to fetch account for Mode of Payment: {0}. Error: {1}").format(mode_of_payment, str(e)))

    customer_group = frappe.db.get_value("Customer", customer, "customer_group")
    party_account = frappe.db.get_value("Party Account", {"parenttype": "Customer", "parent": customer, "company": company}, "account")
    
    if not party_account:
        # Get from company default
        party_account = frappe.get_cached_value("Company", company, "default_receivable_account")
        if not party_account:
            frappe.throw(_("Default Receivable Account not set for Company {0}").format(company))

    # 2. Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = customer
    pe.company = company
    pe.mode_of_payment = mode_of_payment
    pe.paid_from = party_account
    pe.paid_to = paid_to
    pe.paid_amount = amount
    pe.received_amount = amount
    pe.posting_date = nowdate()
    pe.reference_no = pos_opening_shift or (f"POS-{pos_profile}" if pos_profile else f"Payment-{customer}")
    pe.reference_date = nowdate()
    
    # Handle Write Off
    if write_off_amount > 0:
        write_off_account = None
        write_off_cost_center = None
        if pos_profile:
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            write_off_account = profile_doc.write_off_account
            write_off_cost_center = profile_doc.write_off_cost_center
            
        if not write_off_account:
            write_off_account = frappe.get_cached_value("Company", company, "write_off_account")
        if not write_off_cost_center:
            write_off_cost_center = frappe.get_cached_value("Company", company, "cost_center")
            
        if not write_off_account:
            frappe.throw(_("Please set Write Off Account in POS Profile or Company"))
            
        pe.append("deductions", {
            "account": write_off_account,
            "cost_center": write_off_cost_center,
            "amount": write_off_amount,
            "description": "Write Off for POS Payment"
        })
    
    # Optional field that many users add to track which POS profile created it
    # We will safely ignore it if the custom field doesn't exist
    if pe.meta.has_field("custom_pos_profile"):
        pe.custom_pos_profile = pos_profile

    # Add allocations
    for alloc in allocations:
        inv_name = alloc.get("name")
        alloc_amt = flt(alloc.get("allocated_amount"))
        if alloc_amt > 0:
            pe.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": inv_name,
                "allocated_amount": alloc_amt
            })

    pe.save(ignore_permissions=True)
    pe.submit()

    return {"status": "success", "payment_entry": pe.name}

@frappe.whitelist()
def get_pos_profile_payments(pos_opening_shift, limit=100):
    """
    Get payment entries created from this POS Profile.
    We identify them by matching reference_no like POS-PROFILE_NAME or using custom_pos_profile field if exists.
    """
    
    # Find base filter
    filters = {"payment_type": "Receive", "party_type": "Customer"}
    
    # Check if custom_pos_profile exists
    meta = frappe.get_meta("Payment Entry")
    has_custom = any(d.fieldname == "custom_pos_profile" for d in meta.fields)
    
    query = """
        SELECT name, posting_date, party, party_name, paid_amount, mode_of_payment, reference_no 
        FROM `tabPayment Entry` 
        WHERE payment_type = 'Receive' AND party_type = 'Customer'
    """
    
    values = []
    
    if has_custom:
        query += " AND custom_pos_profile = %s "
        values.append(pos_opening_shift)
    else:
        query += " AND reference_no = %s "
        values.append(pos_opening_shift)

    query += " ORDER BY posting_date DESC, creation DESC LIMIT %s "
    values.append(cint(limit) if limit else 100)

    res = frappe.db.sql(query, tuple(values), as_dict=True)
    return res

