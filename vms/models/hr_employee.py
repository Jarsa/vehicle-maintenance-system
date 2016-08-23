# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class HrEmployee(models.Model):
    _description = 'Employees'
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    mechanic = fields.Boolean(help='Validates if the employee is mechanic.')
