import unittest
import frappe
from frappe.utils import add_days, today, nowtime
from navari.navari.stock_management.valuation import (
    get_moving_average_rate,
    get_stock_balance,
    get_stock_value,
)


class TestStatelessStockLedger(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.create_test_data()

    def tearDown(self):
        # Clean up
        self.delete_test_entries()

    def create_test_data(self):
        # Create test company if it doesn't exist
        if not frappe.db.exists("Company", "_Test Company"):
            company = frappe.get_doc(
                {
                    "doctype": "Company",
                    "company_name": "_Test Company",
                    "default_currency": "USD",
                }
            )
            company.insert()

        # Create test item if it doesn't exist
        if not frappe.db.exists("Item", "_Test Stateless Item"):
            item = frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_code": "_Test Stateless Item",
                    "item_name": "Test Stateless Item",
                    "item_group": "All Item Groups",
                    "is_stock_item": 1,
                    "stock_uom": "Nos",
                }
            )
            item.insert()

        # Create test warehouse if it doesn't exist
        if not frappe.db.exists("Warehouse", "_Test Stateless Warehouse - _C"):
            warehouse = frappe.get_doc(
                {
                    "doctype": "Warehouse",
                    "warehouse_name": "_Test Stateless Warehouse - _C",
                    "company": "_Test Company",
                }
            )
            warehouse.insert()

    def delete_test_entries(self):
        # Delete test ledger entries
        frappe.db.sql(
            """
            DELETE FROM `tabStateless Stock Ledger Entry`
            WHERE item_code = '_Test Stateless Item'
        """
        )

    def test_moving_average_calculation(self):
        # Create initial receipt - 10 units @ $100
        sle1 = frappe.get_doc(
            {
                "doctype": "Stateless Stock Ledger Entry",
                "item_code": "_Test Stateless Item",
                "warehouse": "_Test Stateless Warehouse - _C",
                "posting_date": today(),
                "posting_time": nowtime(),
                "quantity": 10,
                "incoming_rate": 100,
                "voucher_type": "Stock Entry",
                "voucher_no": "TEST-ENTRY-1",
                "company": "_Test Company",
                "stock_uom": "Nos",
                "transaction_uom": "Nos",
            }
        )
        sle1.insert()
        sle1.submit()

        sle_count = frappe.db.count(
            "Stateless Stock Ledger Entry",
            {
                "item_code": "_Test Stateless Item",
                "warehouse": "_Test Stateless Warehouse - _C",
            },
        )
        print(f"Number of SLEs found: {sle_count}")

        # Check valuation rate
        rate1 = get_moving_average_rate(
            "_Test Stateless Item", "_Test Stateless Warehouse - _C"
        )
        self.assertEqual(rate1, 100, f"Initial valuation rate should be 100 {rate1}")

        # Create second receipt - 5 units @ $120
        sle2 = frappe.get_doc(
            {
                "doctype": "Stateless Stock Ledger Entry",
                "item_code": "_Test Stateless Item",
                "warehouse": "_Test Stateless Warehouse - _C",
                "posting_date": today(),
                "posting_time": nowtime(),
                "quantity": 5,
                "incoming_rate": 120,
                "voucher_type": "Stock Entry",
                "voucher_no": "TEST-ENTRY-2",
                "company": "_Test Company",
                "stock_uom": "Nos",
                "transaction_uom": "Nos",
            }
        )
        sle2.insert()

        # Check new valuation rate - should be (10*100 + 5*120)/15 = 106.67
        rate2 = get_moving_average_rate(
            "_Test Stateless Item", "_Test Stateless Warehouse - _C"
        )
        self.assertAlmostEqual(
            rate2, 106.67, delta=0.01, msg="Moving average should be 106.67"
        )

        # Check stock balance
        balance = get_stock_balance(
            "_Test Stateless Item", "_Test Stateless Warehouse - _C"
        )
        self.assertEqual(balance, 15, "Stock balance should be 15 units")

        # Create consumption - 8 units
        sle3 = frappe.get_doc(
            {
                "doctype": "Stateless Stock Ledger Entry",
                "item_code": "_Test Stateless Item",
                "warehouse": "_Test Stateless Warehouse - _C",
                "posting_date": today(),
                "posting_time": nowtime(),
                "quantity": -8,
                "incoming_rate": 0,
                "voucher_type": "Stock Entry",
                "voucher_no": "TEST-ENTRY-3",
                "company": "_Test Company",
                "stock_uom": "Nos",
                "transaction_uom": "Nos",
            }
        )
        sle3.insert()

        # Check stock balance again
        balance2 = get_stock_balance(
            "_Test Stateless Item", "_Test Stateless Warehouse - _C"
        )
        self.assertEqual(
            balance2, 7, "Stock balance should be 7 units after consumption"
        )

        # Valuation rate should remain the same after consumption
        rate3 = get_moving_average_rate(
            "_Test Stateless Item", "_Test Stateless Warehouse - _C"
        )
        self.assertAlmostEqual(
            rate3,
            106.67,
            delta=0.01,
            msg="Valuation rate should not change after consumption",
        )
