import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180,
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

    data = frappe.db.sql(
        """
        SELECT
            soi.item_code,
            soi.item_name,
            soi.uom,
            SUM(soi.qty) AS qty,
            SUM(soi.delivered_qty) AS delivered_qty,
            SUM(soi.qty - soi.delivered_qty) AS pending_qty,
            COUNT(DISTINCT so.name) AS sales_orders
        FROM
            `tabSales Order Item` soi
        INNER JOIN
            `tabSales Order` so ON so.name = soi.parent
        WHERE
            so.docstatus = 1
            AND so.status NOT IN ('Closed', 'Cancelled')
            {conditions}
        GROUP BY
            soi.item_code, soi.item_name, soi.uom
        {having_clause}
        ORDER BY
            pending_qty DESC
        """.format(conditions=conditions, having_clause=having_clause),
        filters,
        as_dict=True,
    )

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
