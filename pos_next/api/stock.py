import frappe
from frappe import _

@frappe.whitelist()
def create_stock_transfer(items, source_warehouse, target_warehouse, company):
    import json
    if isinstance(items, str):
        items = json.loads(items)
        
    if not items:
        frappe.throw(_("Please select at least one item to transfer"))
        
    if not source_warehouse or not target_warehouse:
        frappe.throw(_("Source and Target Warehouses are required"))
        
    if source_warehouse == target_warehouse:
        frappe.throw(_("Source and Target Warehouses cannot be the same"))

    # Create Stock Entry
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Transfer"
    se.purpose = "Material Transfer"
    se.company = company
    se.from_warehouse = source_warehouse
    se.to_warehouse = target_warehouse
    se.set_posting_time = 1
    
    for item in items:
        se.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "s_warehouse": source_warehouse,
            "t_warehouse": target_warehouse,
            "uom": item.get("uom") or frappe.db.get_value("Item", item.get("item_code"), "stock_uom")
        })
        
    se.insert()
    se.submit()
    
    return se.name

@frappe.whitelist()
def get_available_items_in_warehouse(warehouse):
    if not warehouse:
        return []
    
    # Get all items with actual_qty > 0 in the specified warehouse
    items = frappe.db.sql("""
        SELECT 
            b.item_code, 
            i.item_name, 
            i.stock_uom as uom, 
            b.actual_qty as available_qty
        FROM 
            `tabBin` b
        INNER JOIN 
            `tabItem` i ON b.item_code = i.name
        WHERE 
            b.warehouse = %s 
            AND b.actual_qty > 0
            AND i.disabled = 0
            AND i.is_stock_item = 1
            AND i.has_serial_no = 0
            AND i.has_batch_no = 0
    """, (warehouse,), as_dict=True)
    
    return items
