# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Activities Kiosk Mode",
    "summary": "Activities Kiosk Mode",
    "version": "15.0.1.0.0",
    "category": "Maintenance",
    "author": "Jarsa",
    "website": "https://git.vauxoo.com/jarsa/jarsa",
    "depends": ["vms_activity"],
    "license": "AGPL-3",
    "data": [
        "views/assets.xml",
        "views/hr_employee_view.xml",
        "views/tasks_kiosk_view.xml",
    ],
    "qweb": [
        "static/src/xml/vms_kiosk_templates.xml",
    ],
    "installable": True,
}
