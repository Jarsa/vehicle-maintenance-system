# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vehicle Maintenance System Operating Unit Sequence",
    "summary": "Module to add sequence by operating unit to orders",
    "version": "15.0.1.0.0",
    "category": "Maintenance",
    "website": "https://git.vauxoo.com/jarsa/jarsa",
    "author": "Jarsa",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "vms_operating_unit",
        "sale_operating_unit",
    ],
    "data": [
        "views/operating_unit_view.xml",
    ],
    "demo": [
        "demo/ir_sequence_demo.xml",
        "demo/operating_unit_demo.xml",
    ],
}
