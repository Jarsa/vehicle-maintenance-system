# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vehicle Maintenance System",
    "summary": "Module to track maintenance of vehicles",
    "version": "15.0.1.0.0",
    "category": "Maintenance",
    "website": "https://git.vauxoo.com/jarsa/jarsa",
    "author": "Jarsa",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "account",
        "fleet",
        "hr",
        "purchase",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/vms_view.xml",
        "views/hr_employee_view.xml",
        "views/vms_program.xml",
        "views/vms_cycle_view.xml",
        "views/vms_product_line_view.xml",
        "views/vms_task_view.xml",
        "views/vms_order_line_view.xml",
        "views/vms_order_view.xml",
        "views/fleet_vehicle_view.xml",
        "views/stock_location_route_view.xml",
        "views/fleet_vehicle_model_view.xml",
        "data/ir_sequence_data.xml",
        "data/stock_picking_type_data.xml",
        "data/stock_location_route_data.xml",
        "data/stock_rule_data.xml",
        "data/ir_config_parameter.xml",
    ],
    "demo": [
        "demo/product_template.xml",
        "demo/vms_task.xml",
        "demo/hr_emplooye.xml",
        "demo/vms_cycle.xml",
        "demo/vms_program.xml",
        "demo/fleet_vehicle_model_brand.xml",
        "demo/fleet_vehicle.xml",
    ],
}
