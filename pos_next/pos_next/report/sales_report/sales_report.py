import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "voucher_no",
            "label": "Voucher",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 120,
        },
        {
            "fieldname": "posting_date",
            "label": "Posting Date",
            "fieldtype": "Date",
            "width": 80,
        },
        {
            "fieldname": "mode_of_payment",
            "label": "Mode Of Payment",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "sales___sn",
            "label": "Sales - SN",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "fieldname": "net_total",
            "label": "Net Total",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "fieldname": "tax_total",
            "label": "Tax Total",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "fieldname": "grand_total",
            "label": "Grand Total",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
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
            'Sales Invoice' as voucher_type,
            si.name as voucher_no,
            si.posting_date,
            (
                SELECT GROUP_CONCAT(DISTINCT sip.mode_of_payment SEPARATOR ', ')
                FROM `tabSales Invoice Payment` sip
                WHERE sip.parent = si.name
            ) as mode_of_payment,
            si.base_net_total as sales___sn,
            si.base_net_total as net_total,
            (si.base_grand_total - si.base_net_total) as tax_total,
            si.base_grand_total as grand_total,
            si.currency
        FROM
            `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            {conditions}
        ORDER BY
            si.posting_date DESC, si.name DESC
        """,
        filters,
        as_dict=1,
    )
