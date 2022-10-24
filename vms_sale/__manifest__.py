# Copyright 2022, Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "VMS for Sale",
    "summary": "Manage VMS Orders from Sale",
    "version": "15.0.1.0.0",
    "category": "Maintenance",
    "website": "https://git.vauxoo.com/jarsa/jarsa",
    "author": "Jarsa",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "vms",
        "sale_management",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
}
