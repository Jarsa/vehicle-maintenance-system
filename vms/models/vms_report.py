# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsReport(models.Model):
    _description = 'VMS Reports'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'vms.report'

    name = fields.Char(string='Number', readonly=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Base', required=True)
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
        string='Driver',
        domain=[('mechanic', '=', True)],)
    end_date = fields.Datetime()
    state = fields.Selection(
        [('pending', 'Pending'),
         ('closed', 'Closed'),
         ('cancel', 'Cancel')],
        default='pending')
    notes = fields.Html()

    @api.model
    def create(self, values):
        res = super(VmsReport, self).create(values)
        if res.operating_unit_id.report_sequence_id:
            sequence = res.operating_unit_id.report_sequence_id
            res.name = sequence.next_by_id()
        else:
            raise ValidationError(_(
                'Verify that the sequences in the base are assigned'))
        return res

    @api.multi
    def action_confirmed(self):
        for rec in self:
            rec.state = 'closed'

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_pending(self):
        for rec in self:
            rec.state = 'pending'
