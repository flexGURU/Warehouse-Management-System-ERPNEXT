import frappe
from frappe import _


def create_ledger_entries(doc, method=None):
    frappe.log(
        "Submitting Stock Entry.................................................."
    )
    frappe.log(doc)

    if doc.docstatus != 1:
        return

    # if doc:
    #     frappe.log(f"document {doc.items}",)
    #     return

    for item in doc.items:

        if doc.stock_entry_type == "Material Receipt" and item.t_warehouse:
            create_entry(
                item=item,
                warehouse=item.t_warehouse,
                qty=item.qty,
                incoming_rate=item.basic_rate,
                voucher_type=doc.doctype,
                voucher_no=doc.name,
                posting_date=doc.posting_date,
                posting_time=doc.posting_time,
                company=doc.company,
            )

            # For Consume: Create negative entry
        elif doc.stock_entry_type == "Material Issue" and item.s_warehouse:
            create_entry(
                item=item,
                warehouse=item.s_warehouse,
                qty=-1 * item.qty,  # Negative quantity for outgoing
                incoming_rate=0,
                voucher_type=doc.doctype,
                voucher_no=doc.name,
                posting_date=doc.posting_date,
                posting_time=doc.posting_time,
                company=doc.company,
            )

        # For Transfer: Create both negative and positive entries
        elif doc.stock_entry_type == "Material Transfer":
            if item.s_warehouse:
                create_entry(
                    item=item,
                    warehouse=item.s_warehouse,
                    qty=-1 * item.qty,  # Negative for source
                    incoming_rate=0,
                    voucher_type=doc.doctype,
                    voucher_no=doc.name,
                    posting_date=doc.posting_date,
                    posting_time=doc.posting_time,
                    company=doc.company,
                )

            if item.t_warehouse:
                create_entry(
                    item=item,
                    warehouse=item.t_warehouse,
                    qty=item.qty,  # Positive for target
                    incoming_rate=item.basic_rate,
                    voucher_type=doc.doctype,
                    voucher_no=doc.name,
                    posting_date=doc.posting_date,
                    posting_time=doc.posting_time,
                    company=doc.company,
                )


def create_entry(
    item,
    warehouse,
    qty,
    incoming_rate,
    voucher_type,
    voucher_no,
    posting_date,
    posting_time,
    company,
):
    """Create a single stateless stock ledger entry"""
    sle = frappe.new_doc("Stateless Stock Ledger Entry")
    sle.item_code = item.item_code
    sle.warehouse = warehouse
    sle.quantity = qty
    sle.incoming_rate = incoming_rate if qty > 0 else 0
    sle.voucher_type = voucher_type
    sle.voucher_no = voucher_no
    sle.voucher_detail_no = item.name
    sle.company = company
    sle.posting_date = posting_date
    sle.posting_time = posting_time
    sle.stock_uom = item.stock_uom
    sle.transaction_uom = item.uom
    sle.conversion_factor = item.conversion_factor
    sle.insert()


def delete_ledger_entries(doc, method=None):
    """Delete stateless stock ledger entries when document is cancelled"""
    if doc.docstatus != 2:  # 2 means cancelled
        return

    frappe.db.delete(
        "Stateless Stock Ledger Entry",
        {"voucher_type": doc.doctype, "voucher_no": doc.name},
    )
