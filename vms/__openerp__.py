# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vehicle Maintenance System",
    "summary": "Module summary",
    "description": "System made for manage maintenance programs",
    "version": "9.0.0.1.0",
    "category": "Maintenance",
    "website": "https://jarsa/.com.mx",
    "author":  "Jarsa Sistemas",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "account",
        "stock",
        "hr",
        "fleet"
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/vms_view.xml',
        'views/vms_activity.xml',
        'views/vms_program.xml',
        'views/vms_vehicle_cycle.xml'
    ],
    "demo": [
    ]
}
