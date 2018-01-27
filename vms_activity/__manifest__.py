# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'VMS Activities',
    'summary': 'Assign activities by mechanic',
    'version': '10.0.1.0.0',
    'category': 'Maintenance',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'depends': [
        'vms',
    ],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/vms_order_line_view.xml',
        'views/vms_activity_view.xml',
        'views/vms_activity_time_view.xml',
    ],
    'installable': True,
}
