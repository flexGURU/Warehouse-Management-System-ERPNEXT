// Copyright (c) 2025, navari and contributors
// For license information, please see license.txt

frappe.query_reports["Stateless Stock Balance Report"] = {
	filters: [
		{
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"label": "Warehouse",
			"mandatory": 0,
			"options": "Warehouse",
			"wildcard_filter": 0
		   }
	],
};
