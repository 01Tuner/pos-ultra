import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "UOM",
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 80,
        },
        {
            "label": "Ordered Qty",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": "Delivered Qty",
            "fieldname": "delivered_qty",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": "Pending Qty",
            "fieldname": "pending_qty",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": "Sales Orders",
            "fieldname": "sales_orders",
            "fieldtype": "Int",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    having_clause = get_having_clause(filters)
    
    is_customer_wise = filters.get("customer_wise")

    select_clause = """
            soi.item_code,
            soi.item_name,
            soi.uom,
            SUM(soi.qty) AS qty,
            SUM(soi.delivered_qty) AS delivered_qty,
            SUM(soi.qty - soi.delivered_qty) AS pending_qty,
            COUNT(DISTINCT so.name) AS sales_orders
    """
    
    group_by_clause = "soi.item_code, soi.item_name, soi.uom"
    order_by_clause = "pending_qty DESC"

    if is_customer_wise:
        select_clause = """
            so.customer,
            so.customer_name,
        """ + select_clause
        group_by_clause = "so.customer, so.customer_name, " + group_by_clause
        order_by_clause = "so.customer_name, pending_qty DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            {select_clause}
        FROM
            `tabSales Order Item` soi
        INNER JOIN
            `tabSales Order` so ON so.name = soi.parent
        WHERE
            so.docstatus = 1
            AND so.status NOT IN ('Closed', 'Cancelled')
            {{conditions}}
        GROUP BY
            {group_by_clause}
        {{having_clause}}
        ORDER BY
            {order_by_clause}
        """.format(conditions=conditions, having_clause=having_clause),
        filters,
        as_dict=True,
    )

    if is_customer_wise:
        # Pre-compute totals per customer
        customer_totals = {}
        customer_meta = {}
        for row in data:
            cust = row.customer
            if cust not in customer_totals:
                customer_totals[cust] = {"qty": 0, "delivered_qty": 0, "pending_qty": 0, "sales_orders": 0}
                customer_meta[cust] = {"customer_name": row.customer_name}
            customer_totals[cust]["qty"] += row.qty or 0
            customer_totals[cust]["delivered_qty"] += row.delivered_qty or 0
            customer_totals[cust]["pending_qty"] += row.pending_qty or 0
            customer_totals[cust]["sales_orders"] += row.sales_orders or 0

        result = []
        current_customer = None

        for row in data:
            if row.customer != current_customer:
                totals = customer_totals[row.customer]
                # Add Parent Row for Accordion with totals
                result.append({
                    "id": row.customer,
                    "item_code": row.customer_name or row.customer,
                    "item_name": "",
                    "uom": "",
                    "qty": totals["qty"],
                    "delivered_qty": totals["delivered_qty"],
                    "pending_qty": totals["pending_qty"],
                    "sales_orders": totals["sales_orders"],
                    "indent": 0,
                    "is_group": 1,
                })
                current_customer = row.customer

            # Child row
            child_row = dict(row)
            child_row["id"] = f"{row.customer}-{row.item_code}"
            child_row["parent_id"] = row.customer
            child_row["indent"] = 1
            child_row["is_group"] = 0

            result.append(child_row)
        return result

    return data


def get_conditions(filters):
    conditions = []

    if filters.get("pos_profile"):
        conditions.append("so.pos_profile = %(pos_profile)s")

    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")

    if filters.get("customer"):
        conditions.append("so.customer = %(customer)s")

    if conditions:
        return "AND " + " AND ".join(conditions)
    return ""


def get_having_clause(filters):
    delivery_status = filters.get("delivery_status") or "Pending"

    if delivery_status == "Pending":
        # Items where at least some qty is not yet delivered
        return "HAVING SUM(soi.qty - soi.delivered_qty) > 0"
    elif delivery_status == "Delivered":
        # Items fully delivered (pending_qty = 0, but some delivered)
        return "HAVING SUM(soi.delivered_qty) > 0 AND SUM(soi.qty - soi.delivered_qty) <= 0"
    else:
        # All — no HAVING filter
        return ""
