# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
from datetime import datetime, timedelta
from openerp import _, api, exceptions, fields, models


class VmsVehicleCycle(models.Model):
    _description = 'Vms Vehicle Cycle'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'vms.vehicle.cycle'

    name = fields.Char()
    cycle_id = fields.Many2one(
        'vms.cycle',
        string='Cycle')
    schedule = fields.Float(
        required=True,
        default=True, string='Distance Schedule')
    sequence = fields.Integer(string='Sequence')
    order_id = fields.Many2one(
        'vms.order',
        string='Order',
        readonly=True, )
    date = fields.Datetime()
    distance = fields.Float(default=0.0, string='Distance Real')
    unit_id = fields.Many2one(
        'fleet.vehicle',
        string="Unit",
        required=True)
    order_state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released'),
         ('cancel', 'Cancel')],
        related='order_id.state',)
    next_service_date = fields.Datetime(
        compute='_compute_next_service_date',
        store=True, default=fields.Datetime.now)

    @api.depends('date', 'name')
    def _compute_next_service_date(self):
        for rec in self:
            if rec.sequence > 1:
                previous_sequence = rec.sequence - 1
                previous_cycle = rec.search([
                    ('unit_id', '=', rec.unit_id.id),
                    ('sequence', '=', previous_sequence)])
                if previous_cycle:
                    previous_date = previous_cycle.next_service_date
                    date = datetime.strptime(
                        previous_date, "%Y-%m-%d %H:%M:%S")
                    days = []
                    day = (rec.cycle_id.frequency / rec.unit_id.distance) * 24
                    days.append(day)
                    rec.next_service_date = (
                        date + timedelta(hours=min(days)))
                else:
                    rec.next_service_date = False
            else:
                if not rec.unit_id.next_service_date:
                    rec.next_service_date = fields.Datetime.now()
                else:
                    rec.next_service_date = rec.unit_id.next_service_date

    @api.model
    def create(self, values):
        cycle = super(VmsVehicleCycle, self).create(values)
        sequence_obj = self.env['ir.sequence']
        cycle.name = sequence_obj.next_by_code('cycle.vehicle.sequence')
        return cycle

    @api.multi
    def start_service_order(self):
        if self.sequence > 1:
            previous_sequence = self.sequence - 1
            previous_cycle = self.search([
                ('unit_id', '=', self.unit_id.id),
                ('sequence', '=', previous_sequence)])
            if previous_cycle:
                if (previous_cycle.order_id.state != 'released' or not
                        previous_cycle.order_id):
                    raise exceptions.ValidationError(
                        _('You must complete the previous'
                            ' maintenance order.'))
        cycle = self.search([
            ('unit_id', '=', self.unit_id.id),
            ('sequence', '=', self.sequence)])
        if cycle:
            if cycle.order_id:
                raise exceptions.ValidationError(
                    _('This cycle already has an active order.'))
        return {
            'name': 'Maintenance Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vms.order',
            'context': {
                'default_base_id': self.unit_id.operating_unit_id.id,
                'default_unit_id': self.unit_id.id,
                'default_type': 'preventive',
                'default_date': fields.Datetime.now(),
            },
            'type': 'ir.actions.act_window',
        }
