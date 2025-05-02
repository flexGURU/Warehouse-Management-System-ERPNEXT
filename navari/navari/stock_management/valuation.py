import frappe
from frappe.utils import flt

def get_moving_average_rate(item_code, warehouse, posting_date=None):
   
    if not posting_date:
        posting_date = frappe.utils.today()
    
    # The SQL query to calculate moving average in one go
    result = frappe.db.sql("""
        SELECT 
            SUM(
                CASE WHEN quantity > 0 THEN quantity * incoming_rate ELSE 0 END
            ) / NULLIF(
                SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END), 0
            ) as valuation_rate
        FROM 
            `tabStateless Stock Ledger Entry`
        WHERE 
            item_code = %s
            AND warehouse = %s
            AND posting_date <= %s
    """, (item_code, warehouse, posting_date), as_dict=True)
    
    return flt(result[0].valuation_rate) if result and result[0].valuation_rate else 0

def get_stock_value(item_code, warehouse, posting_date=None):
    """Calculate stock value based on quantity and moving average rate"""
    if not posting_date:
        posting_date = frappe.utils.today()
    
    # Get current quantity
    quantity = get_stock_balance(item_code, warehouse, posting_date)
    
    # Get valuation rate
    valuation_rate = get_moving_average_rate(item_code, warehouse, posting_date)
    
    return flt(quantity) * flt(valuation_rate)

def get_stock_balance(item_code, warehouse, posting_date=None):
    if not posting_date:
        posting_date = frappe.utils.today()
    
    result = frappe.db.sql("""
        SELECT SUM(quantity) as balance
        FROM `tabStateless Stock Ledger Entry`
        WHERE item_code = %s
        AND warehouse = %s
        AND posting_date <= %s
    """, (item_code, warehouse, posting_date), as_dict=True)
    
    return flt(result[0].balance) if result and result[0].balance else 0