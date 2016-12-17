# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vehicle Maintenance System",
    "summary": "Module summary",
    "description": "System made for manage maintenance programs",
    "version": "9.0.0.1.0",
    "category": "Maintenance",
    "website": "https://jarsa/.com.mx",
    "author": "Jarsa Sistemas",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "account", "stock", "hr", "fleet", "purchase",
        "operating_unit"],
    "data": [
        "security/ir.model.access.csv",
        'views/vms_view.xml',
        'views/vms_activity.xml',
        'views/vms_activity_time_view.xml',
        'views/vms_vehicle_cycle.xml',
        'views/vms_program.xml',
        'views/hr_employee_view.xml',
        'views/vms_cycle_view.xml',
        'views/vms_product_line_view.xml',
        'views/wms_report_view.xml',
        'views/vms_task_view.xml',
        'views/vms_order_line_view.xml',
        'views/vms_order_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/operating_unit_view.xml',
        'data/ir_sequence_data.xml',
    ],
    "demo": [
    ]
}
