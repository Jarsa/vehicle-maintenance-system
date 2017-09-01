# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mechanic = fields.Boolean(
        help='Validates if the employee is mechanic.')
