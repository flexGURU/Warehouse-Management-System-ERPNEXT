# Copyright (c) 2025, navari and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from navari.navari.stock_management.valuation import get_moving_average_rate

def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns(filters)
    data = get_stock_balance(filters)

    return columns, data


def get_columns(filters=None) -> list[dict]:
    """Return columns for the report.

    One field definition per column, just like a DocType field definition.
    """
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 230,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": _("Valuation Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Stock Value"),
            "fieldname": "stock_value",
            "fieldtype": "Currency",
            "width": 110,
        }
    ]
    
    # Add warehouse column if warehouse-wise balance is enabled
    if filters and filters.get("show_warehouse_wise_balance", 0):
        columns.insert(2, {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        })
    
    return columns


def get_stock_balance(filters):
    """Get stock balance data based on filters."""
    if not filters:
        filters = {}
        
    # Determine consolidation level
    group_by = "sle.item_code, item.item_name"
    if filters.get("show_warehouse_wise_balance", 0):
        group_by += ", sle.warehouse"

    # Build query
    balance_data = frappe.db.sql(
        """
        SELECT 
            sle.item_code, 
            item.item_name,
            {warehouse_field}
            SUM(sle.quantity) as balance_qty
        FROM 
            `tabStateless Stock Ledger Entry` sle
        LEFT JOIN
            `tabItem` item ON sle.item_code = item.name
        WHERE 
            sle.posting_date <= %(as_on_date)s
            {item_conditions}
            {warehouse_conditions}
        GROUP BY 
            {group_by}
        HAVING
            SUM(sle.quantity) != 0
        ORDER BY
            sle.item_code
    """.format(
            warehouse_field=(
                "sle.warehouse,"
                if filters.get("show_warehouse_wise_balance", 0)
                else ""
            ),
            item_conditions=(
                "AND sle.item_code = %(item_code)s" if filters.get("item_code") else ""
            ),
            warehouse_conditions=(
                "AND sle.warehouse = %(warehouse)s" if filters.get("warehouse") else ""
            ),
            group_by=group_by,
        ),
        {
            "as_on_date": filters.get("as_on_date") or frappe.utils.today(),
            "item_code": filters.get("item_code"),
            "warehouse": filters.get("warehouse"),
        },
        as_dict=1,
    )

    # Calculate valuation rates and values
    for row in balance_data:
        warehouse = (
            row.get("warehouse")
            if filters.get("show_warehouse_wise_balance", 0)
            else filters.get("warehouse")
        )

        # If consolidated without specific warehouse, use 0 as rate
        if not warehouse:
            row.valuation_rate = 0
            row.stock_value = 0
            continue

        row.valuation_rate = get_moving_average_rate(
            row.item_code, warehouse, filters.get("as_on_date") or frappe.utils.today()
        )

        row.stock_value = row.balance_qty * row.valuation_rate

    return balance_data