import frappe
from frappe import _

@frappe.whitelist()
def get_customers_with_balances(search_term="", pos_profile=None, limit=50):
    """
    Fetch a list of customers along with their outstanding balances from GL Entry.
    """
    limit = int(limit) if limit else 50

    filters = {}
    if pos_profile:
        profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
        customer_groups_list = profile_doc.get("customer_groups", [])
        if customer_groups_list:
            all_allowed_groups = []
            for row in customer_groups_list:
                if row.customer_group:
                    cg = frappe.get_cached_doc("Customer Group", row.customer_group)
                    descendants = frappe.get_all("Customer Group", filters={"lft": [">=", cg.lft], "rgt": ["<=", cg.rgt]}, pluck="name")
                    all_allowed_groups.extend(descendants)
            
            if all_allowed_groups:
                filters["customer_group"] = list(set(all_allowed_groups))

    query = """
        SELECT 
            c.name, 
            c.customer_name, 
            c.mobile_no, 
            c.email_id,
            COALESCE(SUM(gle.debit) - SUM(gle.credit), 0) as balance
        FROM `tabCustomer` c
        LEFT JOIN `tabGL Entry` gle 
            ON gle.party_type = 'Customer' 
            AND gle.party = c.name 
            AND gle.is_cancelled = 0
        WHERE c.disabled = 0
    """

    values = []

    if search_term:
        query += """ 
            AND (
                c.name LIKE %s 
                OR c.customer_name LIKE %s 
                OR c.mobile_no LIKE %s 
                OR c.email_id LIKE %s
            ) 
        """
        like_term = f"%{search_term}%"
        values.extend([like_term, like_term, like_term, like_term])

    if "customer_group" in filters and filters["customer_group"]:
        format_strings = ','.join(['%s'] * len(filters["customer_group"]))
        query += f" AND c.customer_group IN ({format_strings}) "
        values.extend(filters["customer_group"])

    query += """
        GROUP BY c.name
        ORDER BY c.customer_name ASC
        LIMIT %s
    """
    values.append(limit)

    result = frappe.db.sql(query, tuple(values), as_dict=True)
    return result
