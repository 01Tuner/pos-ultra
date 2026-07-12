import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": "Item Code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "fieldname": "item_name",
            "label": "Item Name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "item_group",
            "label": "Item Group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150,
        },
        {
            "fieldname": "total_qty",
            "label": "Total Quantity",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "total_amount",
            "label": "Total Net Amount",
            "fieldtype": "Currency",
            "options": "Company:company:default_currency",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"

    return frappe.db.sql(
        f"""
        SELECT
            sii.item_code,
            sii.item_name,
            sii.item_group,
            SUM(sii.stock_qty) as total_qty,
            SUM(sii.base_net_amount) as total_amount
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            {conditions}
        GROUP BY
            sii.item_code
        ORDER BY
            total_amount DESC
        """,
        filters,
        as_dict=1,
    )
