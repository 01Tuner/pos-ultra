frappe.query_reports["Sales Order Item Wise Summary"] = {
    filters: [
        {
            fieldname: "pos_profile",
            label: __("POS Profile"),
            fieldtype: "Link",
            options: "POS Profile",
        },
        {
            fieldname: "delivery_status",
            label: __("Delivery Status"),
            fieldtype: "Select",
            options: "All\nPending\nDelivered",
            default: "Pending",
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer",
        },
        {
            fieldname: "customer_wise",
            label: __("Customer Wise"),
            fieldtype: "Check",
            default: 0,
        },
    ],
    
    tree: true,
    name_field: "id",
    parent_field: "parent_id",
    initial_depth: 1,

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && data.is_group) {
            value = `<b>${value || ""}</b>`;
        } else if (column.fieldname === "pending_qty" && data && data.pending_qty > 0) {
            value = `<span style="color: #e24c4c; font-weight: bold;">${value}</span>`;
        }

        return value;
    },
};
