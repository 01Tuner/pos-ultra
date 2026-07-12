import frappe
from frappe import _


@frappe.whitelist()
def get_pos_products(pos_profile=None, search_term="", status_filter="", group_filter="", limit=50, offset=0):
    """
    Fetch ALL items (including non-stock items) with their selling price.
    Shows every item regardless of POS profile item group restrictions.
    """
    limit = int(limit) if limit else 50
    offset = int(offset) if offset else 0

    # Get price list and item groups from POS Profile
    price_list = None
    allowed_item_groups = []
    if pos_profile:
        try:
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            price_list = profile_doc.selling_price_list
            item_groups_list = profile_doc.get("item_groups", [])
            for row in item_groups_list:
                if row.item_group:
                    try:
                        ig = frappe.get_cached_doc("Item Group", row.item_group)
                        descendants = frappe.get_all(
                            "Item Group",
                            filters={"lft": [">=", ig.lft], "rgt": ["<=", ig.rgt]},
                            pluck="name"
                        )
                        allowed_item_groups.extend(descendants)
                    except Exception:
                        allowed_item_groups.append(row.item_group)
        except Exception:
            pass

    # Build query
    conditions = []
    values = []

    if search_term:
        conditions.append("(i.item_name LIKE %s OR i.name LIKE %s OR EXISTS (SELECT 1 FROM `tabItem Barcode` ib WHERE ib.parent = i.name AND ib.barcode LIKE %s))")
        like_term = f"%{search_term}%"
        values.extend([like_term, like_term, like_term])

    if status_filter == "enabled":
        conditions.append("i.disabled = 0")
    elif status_filter == "disabled":
        conditions.append("i.disabled = 1")

    if group_filter:
        conditions.append("i.item_group = %s")
        values.append(group_filter)
    # Note: No item group restriction from POS profile — show ALL items

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    # Price join
    price_join = ""
    price_select = "NULL as price"
    if price_list:
        price_join = """LEFT JOIN `tabItem Price` ip 
            ON ip.item_code = i.name 
            AND ip.price_list = %s 
            AND ip.selling = 1
            AND (ip.valid_upto IS NULL OR ip.valid_upto >= CURDATE())"""
        price_select = "ip.price_list_rate as price"
        values.insert(0, price_list)

    query = f"""
        SELECT 
            i.name,
            i.item_name,
            i.item_group,
            i.disabled,
            i.has_variants,
            i.is_stock_item,
            i.description,
            i.image,
            {price_select}
        FROM `tabItem` i
        {price_join}
        {where_clause}
        ORDER BY i.item_name ASC
        LIMIT %s OFFSET %s
    """
    values.extend([limit, offset])

    result = frappe.db.sql(query, tuple(values), as_dict=True)
    return {"items": result}


@frappe.whitelist()
def update_item_price(item_code, price, pos_profile=None):
    """
    Update or create the selling price for an item in the POS profile's price list.
    """
    price = float(price)

    # Determine price list
    price_list = "Standard Selling"
    if pos_profile:
        try:
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            if profile_doc.selling_price_list:
                price_list = profile_doc.selling_price_list
        except Exception:
            pass

    # Get company's default currency
    company = None
    if pos_profile:
        try:
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            company = profile_doc.company
        except Exception:
            pass

    currency = frappe.get_cached_value("Company", company, "default_currency") if company else frappe.defaults.get_defaults().get("currency") or "USD"

    # Check if Item Price exists
    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list, "selling": 1},
        "name"
    )

    if existing:
        doc = frappe.get_doc("Item Price", existing)
        doc.price_list_rate = price
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": price_list,
            "price_list_rate": price,
            "selling": 1,
            "currency": currency,
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    return {"success": True, "price": price}


@frappe.whitelist()
def toggle_item_status(item_code, disabled):
    """
    Enable or disable an Item.
    """
    disabled = int(disabled)
    frappe.db.set_value("Item", item_code, "disabled", disabled, update_modified=True)
    frappe.db.commit()
    return {"success": True, "disabled": disabled}


@frappe.whitelist()
def update_item(item_code, item_name, item_group=None, price=None, description=None, disabled=0, pos_profile=None):
    """
    Update an existing Item's details and optionally its price.
    """
    doc = frappe.get_doc("Item", item_code)
    doc.item_name = item_name
    if item_group:
        doc.item_group = item_group
    if description is not None:
        doc.description = description
    doc.disabled = int(disabled)
    doc.save(ignore_permissions=True)

    if price is not None:
        update_item_price(item_code, price, pos_profile)

    frappe.db.commit()

    # Return updated data
    result = frappe.db.get_value(
        "Item",
        item_code,
        ["name", "item_name", "item_group", "disabled", "image", "description"],
        as_dict=True
    )
    if result and price is not None:
        result["price"] = float(price)
    return result


@frappe.whitelist()
def create_item(item_name, item_group=None, price=None, description=None, pos_profile=None):
    """
    Create a new Item and add it to the POS profile's price list.
    """
    if not item_group:
        item_group = "Products"

    # Ensure item group exists, fallback to 'All Item Groups' root
    if not frappe.db.exists("Item Group", item_group):
        root_group = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name")
        item_group = root_group or "All Item Groups"

    doc = frappe.get_doc({
        "doctype": "Item",
        "item_name": item_name,
        "item_group": item_group,
        "description": description or "",
        "is_stock_item": 1,
        "stock_uom": "Nos",
    })
    doc.insert(ignore_permissions=True)

    # Set price
    if price is not None and float(price) > 0:
        update_item_price(doc.name, price, pos_profile)

    frappe.db.commit()

    return {
        "name": doc.name,
        "item_name": doc.item_name,
        "item_group": doc.item_group,
        "disabled": 0,
        "image": None,
        "description": doc.description,
        "price": float(price) if price else 0,
    }
