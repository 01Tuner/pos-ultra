import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "mode_of_payment",
            "label": "Mode of Payment",
            "fieldtype": "Link",
            "options": "Mode of Payment",
            "width": 200,
        },
        {
            "fieldname": "total_amount",
            "label": "Total Amount",
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
            sip.mode_of_payment,
            SUM(sip.base_amount) as total_amount
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Payment` sip ON sip.parent = si.name
        WHERE
            si.docstatus = 1
            {conditions}
        GROUP BY
            sip.mode_of_payment
        ORDER BY
            total_amount DESC
        """,
        filters,
        as_dict=1,
    )
