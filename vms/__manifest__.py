# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Vehicle Maintenance System',
    'summary': 'Module to track maintenance of vehicles',
    'version': '10.0.1.0.0',
    'category': 'Maintenance',
    'website': 'https://jarsa/.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'depends': [
        'account',
        'fleet',
        'hr',
        'purchase',
        'stock',
        'stock_operating_unit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/vms_view.xml',
        'views/hr_employee_view.xml',
        'views/vms_program.xml',
        'views/vms_cycle_view.xml',
        'views/vms_product_line_view.xml',
        'views/vms_report_view.xml',
        'views/vms_task_view.xml',
        'views/vms_order_line_view.xml',
        'views/vms_order_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/operating_unit_view.xml',
        'wizards/vms_wizard_maintenance_order_view.xml',
        'data/ir_sequence_data.xml',
        'data/stock_picking_type_data.xml',
        'data/procurement_route_data.xml',
        'data/cron_vms_order.xml',
        'data/ir_config_parameter.xml',
    ],
    'demo': [
    ]
}
