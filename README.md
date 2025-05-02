# Navari Stock Management System

A custom stock management system built on Frappe/ERPNext that implements stateless stock ledger entries with moving average valuation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Creating Items](#creating-items)
  - [Managing Warehouses](#managing-warehouses)
  - [Stock Entries](#stock-entries)
  - [Viewing Reports](#viewing-reports)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

Navari Stock Management is a custom Frappe application that provides a lightweight alternative to ERPNext's stock management system. It uses a stateless stock ledger approach which simplifies inventory tracking while maintaining accurate valuation through moving average calculation.

### Why Stateless Stock Ledger?

Unlike ERPNext's standard implementation, our stateless approach:
- Reduces database complexity
- Improves query performance
- Simplifies maintenance and troubleshooting
- Maintains full compatibility with existing Frappe/ERPNext workflows

## ✨ Features

- **Custom DocTypes**
  - Stateless Stock Ledger Entry
  - Integration with standard Item and Warehouse DocTypes

- **Stock Operations**
  - Material Receipt
  - Material Issue
  - Material Transfer

- **Inventory Valuation**
  - Moving Average method
  - Accurate stock valuation calculation

- **Reports**
  - Stock Balance Report
  - Stock Ledger Report

## 📦 Installation

1. Install Frappe and ERPNext if not already installed:
   ```bash
   bench init frappe-bench
   cd frappe-bench
   bench get-app erpnext
   bench install-app erpnext
   ```

2. Get the Navari app:
   ```bash
   bench get-app navari https://github.com/yourusername/navari
   ```

3. Install the app:
   ```bash
   bench install-app navari
   ```

4. Build assets and restart:
   ```bash
   bench build
   bench restart
   ```

## ⚙️ Configuration

After installation, you'll need to:

1. Create a company
2. Set up warehouse structure
3. Create inventory items

## 🚀 Usage

### Creating Items

1. Navigate to **Stock > Items and Pricing > Item**
2. Click **New**
3. Fill in required fields:
   - Item Name
   - Item Group
   - Item Code (ID)
   - Valuation Rate
   - Default Unit of Measure

Example items:
```
Item Name: Philips LED Bulb
Item Group: Products
Item Code: bulbs-001
Valuation Rate: 150.00
Default UoM: Nos (Conversion Factor: 1)
```

### Managing Warehouses

1. Navigate to **Stock > Settings > Warehouse**
2. Create a tree structure of warehouses associated with your company

### Stock Entries

To add inventory:

1. Navigate to **Stock > Stock Transactions > Stock Entry**
2. Select **Material Receipt** as Stock Entry Type
3. Choose target warehouse 
4. Add items, quantities and rates
5. Save and Submit

For consumption:
1. Use **Material Issue** as Stock Entry Type
2. Specify source warehouse

For transfers:
1. Use **Material Transfer** as Stock Entry Type
2. Specify both source and target warehouses

### Viewing Reports

#### Stock Balance Report

1. Navigate to **Stock > Reports > Stateless Stock Balance Report**
2. Filter by warehouse and date to see:
   - Current quantities
   - Valuation rates
   - Total stock value

#### Stock Ledger Report

1. Navigate to **Stock > Reports > Stock Ledger Report**
2. View detailed movement history of all inventory transactions

## 🏗️ Architecture

### Core Components

1. **DocTypes**
   - Company and Warehouse (tree structure)
   - Item/Product
   - Stateless Stock Ledger Entry
   - Stock Entry Types (Receipt, Issue, Transfer)

2. **Hooks and Triggers**
   - Stock Entry submission triggers ledger creation
   - Cancellation triggers ledger deletion

3. **Business Logic**
   - Moving average calculation
   - Stock balance computation

### File Structure

```
navari/
├── navari/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── navari/
│   │   ├── __init__.py
│   │   ├── stock_management/
│   │   │   ├── __init__.py
│   │   │   ├── stock_ledger.py
│   ├── public/
│   ├── templates/
│   └── www/
├── setup.py
└── requirements.txt
```

## 📖 API Reference

### Stock Ledger Functions

#### `create_ledger_entries(doc, method=None)`

Processes a submitted Stock Entry and creates appropriate Stateless Stock Ledger entries.

Parameters:
- `doc`: The Stock Entry document
- `method`: Optional method name

#### `create_entry(item, warehouse, qty, incoming_rate, voucher_type, voucher_no, posting_date, posting_time, company)`

Creates a single Stateless Stock Ledger Entry.

Parameters:
- `item`: Item document
- `warehouse`: Warehouse ID
- `qty`: Quantity (positive for receipt, negative for issue)
- `incoming_rate`: Valuation rate
- `voucher_type`: Document type (typically "Stock Entry")
- `voucher_no`: Document name/ID
- `posting_date`: Transaction date
- `posting_time`: Transaction time
- `company`: Company ID

#### `get_moving_average_rate(item_code, warehouse, posting_date=None)`

Calculates the moving average valuation rate for an item in a specific warehouse.

Parameters:
- `item_code`: Item code/ID
- `warehouse`: Warehouse ID
- `posting_date`: Date to calculate rate for (defaults to today)

Returns:
- Calculated moving average rate (float)

#### `delete_ledger_entries(doc, method=None)`

Removes ledger entries when a Stock Entry is cancelled.

Parameters:
- `doc`: The Stock Entry document being cancelled
- `method`: Optional method name

## 🧪 Testing

The system includes comprehensive tests in the `TestStatelessStockLedger` class.

Run tests with:
```bash
bench run-tests --app navari
```

### Test Coverage

Tests verify:
1. Stock valuation rates calculation
2. Stock balance updates after transactions
3. Moving average calculation accuracy

### Sample Test Flow

1. Create initial receipt (10 units @ 100)
2. Verify valuation rate = 100
3. Add second receipt (5 units @ 120)
4. Verify new valuation rate = 106.67
5. Issue 8 units
6. Verify remaining balance = 7 units
7. Confirm valuation rate remains 106.67

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© X Electronics | Developed using Frappe/ERPNext