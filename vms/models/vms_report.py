# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class VmsReport(models.Model):
    _description = 'VMS Reports'
    _name = 'vms.report'

    name = fields.Char(string='Number', readonly=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    unit_id = fields.Many2one(
        'fleet.vehicle',
        required=True,
        string='Unit')
    order_id = fields.Many2one(
        'vms.order',
        readonly=True,
        string='Order')
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        domain=[('driver', '=', 'True')],
        string='Driver')
    end_date = fields.Datetime()
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('close', 'Close'),
         ('cancel', 'Cancel')],
        readonly=True)
    notes = fields.Text(required=True)
