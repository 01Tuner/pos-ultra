import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "sales_person",
            "label": "Sales Person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200,
        },
        {
            "fieldname": "total_allocated_amount",
            "label": "Allocated Amount",
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
            st.sales_person,
            SUM(st.allocated_amount) as total_allocated_amount
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Team` st ON st.parent = si.name
        WHERE
            si.docstatus = 1
            {conditions}
        GROUP BY
            st.sales_person
        ORDER BY
            total_allocated_amount DESC
        """,
        filters,
        as_dict=1,
    )
