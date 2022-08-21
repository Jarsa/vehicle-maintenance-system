# Copyright 2016-2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Vehicle Maintenance System Reports",
    "summary": "Module to add reports to vehicle maintenance system",
    "version": "15.0.1.0.0",
    "category": "Maintenance",
    "website": "https://git.vauxoo.com/jarsa/jarsa",
    "author": "Jarsa",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "vms",
    ],
    "data": [
        "views/vms_order_view.xml",
        "views/vms_report_view.xml",
        "data/ir_sequence_data.xml",
    ],
}
