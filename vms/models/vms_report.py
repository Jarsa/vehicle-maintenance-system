# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
        string='Driver')
    end_date = fields.Datetime()
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('confirmed', 'Confirmed'),
         ('close', 'Close'),
         ('cancel', 'Cancel')],
        default='draft')
    notes = fields.Html()

    @api.model
    def create(self, values):
        report = super(VmsReport, self).create(values)
        sequence = report.operating_unit_id.report_sequence_id
        report.name = sequence.next_by_id()
        return report

    @api.multi
    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'
